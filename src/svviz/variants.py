import logging
import pyfaidx

from svviz.utilities import Locus, reverseComp, getListDefault


def getBreakpointFormatsStr(which=None):
    formats = []
    if which in ["del", None]:
        formats.append("Format for deletion breakpoints is '<chrom> <start> <end>'")
    if which in ["ins", None]:
        formats.append("Format for insertion breakpoints is '<chrom> <pos> [end] <seq>'; \n"
            "  specify 'end' to create a compound deletion-insertion, otherwise insertion \n"
            "  position is before 'pos'")
    if which in ["inv", None]:
        formats.append("Format for inversion breakpoints is '<chrom> <start> <end>'")
    if which in ["mei", None]:
        formats.append( "Format for mobile element insertion is '<mobile_elements.fasta> \n"
            "  <chrom> <pos> <ME name> [ME strand [start [end]]]'")
    return "\n".join(formats)


def getVariant(dataHub):
    # if dataHub.args.search_dist is None:
    #     dataHub.args.search_dist = dataHub.args.isize_mean * 2

    # alignDistance = int(max(dataHub.search_dist, dataHub.args.isize_mean*2))

    if dataHub.args.type.lower().startswith("del"):
        # if dataHub.args.deldemo:
        #     chrom, start, end = "chr1", 72766323, 72811840
        # else:
        assert len(dataHub.args.breakpoints) == 3, getBreakpointFormatsStr("del")
        chrom = dataHub.args.breakpoints[0]
        start = int(dataHub.args.breakpoints[1])
        end = int(dataHub.args.breakpoints[2])
        assert start < end

        variant = Deletion.from_breakpoints(chrom, start-1, end-1, dataHub.alignDistance, dataHub.genome)
    elif dataHub.args.type.lower().startswith("ins"):
        # if dataHub.args.insdemo:
        #     chrom, pos, seq = "chr3", 20090540, reverseComp(misc.L1SEQ)
        # else:
        assert len(dataHub.args.breakpoints) in [3,4], getBreakpointFormatsStr("ins")
        chrom = dataHub.args.breakpoints[0]
        pos = int(dataHub.args.breakpoints[1])
        if len(dataHub.args.breakpoints) == 3:
            seq = dataHub.args.breakpoints[2]
            end = pos
        else:
            end = int(dataHub.args.breakpoints[2])
            seq = dataHub.args.breakpoints[3]

        variant = Insertion(Locus(chrom, pos, end, "+"), seq, dataHub.alignDistance, dataHub.genome)
    elif dataHub.args.type.lower().startswith("inv"):
        assert len(dataHub.args.breakpoints) == 3, getBreakpointFormatsStr("inv")
        chrom = dataHub.args.breakpoints[0]
        start = int(dataHub.args.breakpoints[1])
        end = int(dataHub.args.breakpoints[2])
        if dataHub.args.min_mapq is None:
            dataHub.args.min_mapq = -1

        variant = Inversion(Locus(chrom, start, end, "+"), dataHub.alignDistance, dataHub.genome)
    elif dataHub.args.type.lower().startswith("mei"):
        assert len(dataHub.args.breakpoints) >= 4, getBreakpointFormatsStr("mei")

        insertionBreakpoint = Locus(dataHub.args.breakpoints[1], dataHub.args.breakpoints[2], dataHub.args.breakpoints[2], "+")

        meName = dataHub.args.breakpoints[3]
        meStrand = getListDefault(dataHub.args.breakpoints, 4, "+")
        meStart = getListDefault(dataHub.args.breakpoints, 5, 0)
        meEnd = getListDefault(dataHub.args.breakpoints, 6, 1e100)

        meCoords = Locus(meName, meStart, meEnd, meStrand)
        meFasta = pyfaidx.Fasta(dataHub.args.breakpoints[0], as_raw=True)

        variant = MobileElementInsertion(insertionBreakpoint, meCoords, meFasta, dataHub.alignDistance, dataHub.genome)
    else:
        raise Exception("only accept event types of deletion, insertion or mei")

    logging.info(" Variant: {}".format(variant))

    return variant



class Segment(object):
    colors = {0:"red", 1:"blue", 2:"gray", 3:"orange", 4:"brown"}

    def __init__(self, chrom, start, end, strand, id_, source="genome"):
        self.chrom = chrom
        if start > end:
            start, end = end, start
        self.start = start
        self.end = end
        self.strand = strand
        self.id = id_
        self.source = source

    def __len__(self):
        return abs(self.end - self.start)

    def color(self):
        return self.colors[self.id]

    def __repr__(self):
        return "<Segment {} {}:{}-{}{} ({})>".format(self.id, self.chrom, self.start, self.end, self.strand, self.source)

def mergedSegments(segments):
    # quick-and-dirty recursive function to merge adjacent variant.Segment's
    if len(segments) == 1:
        return segments

    done = []
    for i in range(len(segments)-1):
        first = segments[i]
        second = segments[i+1]
        if first.chrom==second.chrom and first.strand==second.strand and first.end == second.start-1 and first.source==second.source:
            merged = Segment(first.chrom, first.start, second.end, second.strand, "{}_{}".format(first.id, second.id), first.source)
            result = done + mergedSegments([merged]+segments[i+2:])
            return result
        else:
            done.append(segments[i])

    done.append(segments[-1])
    return done
    
class StructuralVariant(object):
    def __init__(self, breakpoints, alignDistance, fasta):
        self.breakpoints = sorted(breakpoints, key=lambda x: x.start())
        self.alignDistance = alignDistance

        self.sources = {"genome":fasta}

        # self._refseq = None
        # self._altseq = None
        self._seqs = {}

    def __getstate__(self):
        """ allows pickling of StructuralVariant()s """
        for allele in ["alt", "ref"]:
            self.getSeq(allele)
        state = self.__dict__.copy()
        del state['sources']
        return state


    def __str__(self):
        return "{}({};{})".format(self.__class__.__name__, self.breakpoints, self.alignDistance)
    def shortName(self):
        return "{}_{}_{}".format(self.__class__.__name__[:3].lower(), self.breakpoints[0].chr(), self.breakpoints[0].start())

    def searchRegions(self):
        pass    
    def getRefSeq(self):
        return self.getSeq("ref")
    def getAltSeq(self):
        return self.getSeq("alt")

    def getSeq(self, allele):
        if allele not in self._seqs:
            segments = self.segments(allele)
            seqs = []
            for segment in segments:
                # if segment.source == "genome":
                #     seq = self.fasta[segment.chrom][segment.start:segment.end+1]
                # else:
                seq = self.sources[segment.source][segment.chrom][segment.start:segment.end+1]
                    # raise Exception("not yet implemented: non-genomic segments")

                if segment.strand == "-":
                    seq = reverseComp(seq)
                seqs.append(seq)
            self._seqs[allele] = "".join(seqs).upper()
        return self._seqs[allele]

    def getLength(self, allele):
        return len(self.getSeq(allele))
    def getRelativeBreakpoints(self, which):
        segments = self.segments(which)
        breakpoints = []
        curpos = 0
        for segment in segments[:-1]:
            curpos += len(segment)
            breakpoints.append(curpos)

        return breakpoints         

    def segments(self, allele):
        # for visual display of the different segments between breakpoints
        return None


class Deletion(StructuralVariant):
    @classmethod
    def from_breakpoints(class_, chrom, first, second, alignDistance, fasta):
        breakpointLoci = [Locus(chrom, first, first, "+"), Locus(chrom, second, second, "+")]
        return class_(breakpointLoci, alignDistance, fasta)

    def searchRegions(self, searchDistance):
        chrom = self.breakpoints[0].chr()
        deletionRegion = Locus(chrom, self.breakpoints[0].start()-searchDistance, self.breakpoints[-1].end()+searchDistance, "+")
        return [deletionRegion]

    def segments(self, allele):
        chrom = self.breakpoints[0].chr()

        if allele in ["ref", "amb"]:
            return [Segment(chrom, self.breakpoints[0].start()-self.alignDistance, self.breakpoints[0].start()-1, "+", 0),
                    Segment(chrom, self.breakpoints[0].start(), self.breakpoints[1].end(), "+", 1),
                    Segment(chrom, self.breakpoints[1].end()+1, self.breakpoints[1].end()+self.alignDistance, "+", 2)]
        elif allele == "alt":
            return [Segment(chrom, self.breakpoints[0].start()-self.alignDistance, self.breakpoints[0].start()-1, "+", 0),
                    Segment(chrom, self.breakpoints[1].end()+1, self.breakpoints[1].end()+self.alignDistance, "+", 2)]

    def __str__(self):
        deletionLength = self.breakpoints[1].end() - self.breakpoints[0].start()
        return "{}::{}:{:,}-{:,}({})".format(self.__class__.__name__, self.breakpoints[0].chr(), self.breakpoints[0].start(), 
            self.breakpoints[1].end(), deletionLength)


class Inversion(StructuralVariant):
    def __init__(self, region, alignDistance, fasta):
        breakpoints = [Locus(region.chr(), region.start(), region.start(), "+"), Locus(region.chr(), region.end(), region.end(), "+")]
        super(Inversion, self).__init__(breakpoints, alignDistance, fasta)

        self.region = region

    def chrom(self):
        return self.region.chr()

    def searchRegions(self, searchDistance):
        chrom = self.chrom()

        if len(self.region) < 2*searchDistance:
            # return a single region
            return [Locus(chrom, self.region.start()-searchDistance, self.region.end()+searchDistance, "+")]
        else:
            # return two regions, each around one of the ends of the inversion
            searchRegions = []
            searchRegions.append(Locus(chrom, self.region.start()-searchDistance, self.region.start()+searchDistance, "+"))
            searchRegions.append(Locus(chrom, self.region.end()-searchDistance, self.region.end()+searchDistance, "+"))
            return searchRegions

    def segments(self, allele):
        chrom = self.chrom()

        if allele in ["ref", "amb"]:
            return [Segment(chrom, self.region.start()-self.alignDistance, self.region.start()-1, "+", 0),
                    Segment(chrom, self.region.start(), self.region.end(), "+", 1),
                    Segment(chrom, self.region.end()+1, self.region.end()+self.alignDistance, "+", 2)]
        elif allele == "alt":
            return [Segment(chrom, self.region.start()-self.alignDistance, self.region.start()-1, "+", 0),
                    Segment(chrom, self.region.start(), self.region.end(), "-", 1),
                    Segment(chrom, self.region.end()+1, self.region.end()+self.alignDistance, "+", 2)]

                
    def __str__(self):
        return "{}::{}:{:,}-{:,}".format(self.__class__.__name__, self.region.chr(), self.region.start(), self.region.end())


class Insertion(StructuralVariant):
    def __init__(self, breakpoint, insertSeq, alignDistance, fasta):
        super(Insertion, self).__init__([breakpoint], alignDistance, fasta)
        self.sources["insertion"] = {}
        self.sources["insertion"]["insertion"] = insertSeq
        self.insertionLength = len(insertSeq)


    def searchRegions(self, searchDistance):
        chrom = self.breakpoints[0].chr()
        return [Locus(chrom, self.breakpoints[0].start()-searchDistance, self.breakpoints[-1].end()+searchDistance, "+")]

    def segments(self, allele):
        breakpoint = self.breakpoints[0]
        chrom = breakpoint.chr()

        # If breakpoint has no length, we make the insertion before the breakpoint coordinate
        deletionOffset = 0
        if len(breakpoint) > 1:
            # If we're deleting some bases in addition to inserting, we'll make sure to start
            # the last segment after the deleted bases
            deletionOffset = 1

        if allele in ["ref", "amb"]:
            refSegments = []
            refSegments.append(Segment(chrom, breakpoint.start()-self.alignDistance, breakpoint.start()-1, "+", 0))
            if len(breakpoint) > 1:
                refSegments.append(Segment(chrom, breakpoint.start(), breakpoint.end(), "+", 3))

            refSegments.append(Segment(chrom, breakpoint.end()+deletionOffset, breakpoint.end()+self.alignDistance, "+", 2))
            return refSegments
        elif allele == "alt":
            return [Segment(chrom, breakpoint.start()-self.alignDistance, breakpoint.start()-1, "+", 0),
                    Segment("insertion", 0, self.insertionLength, "+", 1, source="insertion"),
                    Segment(chrom, breakpoint.end()+deletionOffset, breakpoint.end()+self.alignDistance, "+", 2)]

    def __str__(self):
        return "{}::{}:{:,};len={}".format(self.__class__.__name__, self.breakpoints[0].chr(), self.breakpoints[0].start(), self.insertionLength)
       

class MobileElementInsertion(StructuralVariant):
    def __init__(self, breakpoint, insertedSeqLocus, insertionFasta, alignDistance, refFasta):
        super(MobileElementInsertion, self).__init__([breakpoint], alignDistance, refFasta)

        self.sources["repeats"] = insertionFasta
        self.insertedSeqLocus = insertedSeqLocus

        # insertionSequence = insertionFasta[insertedSeqLocus.chr()][insertedSeqLocus.start():insertedSeqLocus.end()+1].upper()
        # if insertedSeqLocus.strand() == "-":
        #     insertionSequence = reverseComp(insertionSequence)

    def searchRegions(self, searchDistance):
        chrom = self.breakpoints[0].chr()
        return [Locus(chrom, self.breakpoints[0].start()-searchDistance, self.breakpoints[-1].end()+searchDistance, "+")]

    def segments(self, allele):
        chrom = self.breakpoints[0].chr()

        if allele in ["ref", "amb"]:
            return [Segment(chrom, self.breakpoints[0].start()-self.alignDistance, self.breakpoints[0].start()-1, "+", 0),
                    Segment(chrom, self.breakpoints[0].end(), self.breakpoints[0].end()+self.alignDistance, "+", 2)]
        elif allele == "alt":
            return [Segment(chrom, self.breakpoints[0].start()-self.alignDistance, self.breakpoints[0].start()-1, "+", 0),
                    Segment(self.insertedSeqLocus.chr(), self.insertedSeqLocus.start(), 
                        self.insertedSeqLocus.end(), self.insertedSeqLocus.strand(), 1, source="repeats"),
                    Segment(chrom, self.breakpoints[0].end(), self.breakpoints[0].end()+self.alignDistance, "+", 2)]

    def __str__(self):
        return "{}::{}({});{})".format(self.__class__.__name__, self.insertedSeqLocus.chr(), self.breakpoints, self.alignDistance)
    def shortName(self):
        return "{}_{}_{}".format("mei", self.breakpoints[0].chr(), self.breakpoints[0].start())




if __name__ == '__main__':
    import pyfaidx
    from hts.GenomeFetch import GenomeFetch

    genomeFetch = GenomeFetch("/Users/nspies/Data/hg19-no-newlines/")
    genome = pyfaidx.Fasta("/Users/nspies/Data/hg19/hg19.fasta", as_raw=True)

    deletion = Deletion([Locus("chr1", 72766323-1, 72766323-1, "+"), Locus("chr1", 72811840-1, 72811840-1, "+")],
        100, genome)

    print deletion.getAltSeq()

    print genomeFetch.get_seq_from_to("chr1", 72766323-1-100, 72766323-1, "+").upper() + \
                genomeFetch.get_seq_from_to("chr1", 72811840-1, 72811840-1+100).upper()