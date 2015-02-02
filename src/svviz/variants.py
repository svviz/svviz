import logging
import pyfaidx

from svviz.utilities import Locus, reverseComp, getListDefault


def getVariant(dataHub):
    if dataHub.args.search_dist is None:
        dataHub.args.search_dist = dataHub.args.isize_mean * 2

    alignDistance = int(max(dataHub.args.search_dist, dataHub.args.isize_mean*2))

    if dataHub.args.type.lower().startswith("del"):
        # if dataHub.args.deldemo:
        #     chrom, start, end = "chr1", 72766323, 72811840
        # else:
        assert len(dataHub.args.breakpoints) == 3, "Format for deletion breakpoints is '<chrom> <start> <end>'"
        chrom = dataHub.args.breakpoints[0]
        start = int(dataHub.args.breakpoints[1])
        end = int(dataHub.args.breakpoints[2])
        assert start < end
        if dataHub.args.min_mapq is None:
            dataHub.args.min_mapq = 30

        variant = Deletion.from_breakpoints(chrom, start-1, end-1, alignDistance, dataHub.genome)
    elif dataHub.args.type.lower().startswith("ins"):
        # if dataHub.args.insdemo:
        #     chrom, pos, seq = "chr3", 20090540, reverseComp(misc.L1SEQ)
        # else:
        assert len(dataHub.args.breakpoints) == 3, "Format for insertion breakpoints is '<chrom> <pos> <seq>'"
        chrom = dataHub.args.breakpoints[0]
        pos = int(dataHub.args.breakpoints[1])
        seq = dataHub.args.breakpoints[2]
        if dataHub.args.min_mapq is None:
            dataHub.args.min_mapq = -1

        variant = Insertion(Locus(chrom, pos, pos, "+"), seq, alignDistance, dataHub.genome)
    elif dataHub.args.type.lower().startswith("inv"):
        assert len(dataHub.args.breakpoints) == 3, "Format for insertion breakpoints is '<chrom> <start> <end>'"
        chrom = dataHub.args.breakpoints[0]
        start = int(dataHub.args.breakpoints[1])
        end = int(dataHub.args.breakpoints[2])
        if dataHub.args.min_mapq is None:
            dataHub.args.min_mapq = -1

        variant = Inversion(Locus(chrom, start, end, "+"), alignDistance, dataHub.genome)
    elif dataHub.args.type.lower().startswith("mei"):
        assert len(dataHub.args.breakpoints) >= 4, "Format for mobile element insertion is '<mobile_elements.fasta> <chrom> <pos> <ME name> [ME strand [start [end]]]'"
        if dataHub.args.min_mapq is None:
            dataHub.args.min_mapq = -1

        insertionBreakpoint = Locus(dataHub.args.breakpoints[1], dataHub.args.breakpoints[2], dataHub.args.breakpoints[2], "+")

        meName = dataHub.args.breakpoints[3]
        meStrand = getListDefault(dataHub.args.breakpoints, 4, "+")
        meStart = getListDefault(dataHub.args.breakpoints, 5, 0)
        meEnd = getListDefault(dataHub.args.breakpoints, 6, 1e100)

        meCoords = Locus(meName, meStart, meEnd, meStrand)
        meFasta = pyfaidx.Fasta(dataHub.args.breakpoints[0], as_raw=True)

        variant = MobileElementInsertion(insertionBreakpoint, meCoords, meFasta, alignDistance, dataHub.genome)
    else:
        raise Exception("only accept event types of deletion, insertion or mei")

    logging.info(" Variant: {}".format(variant))

    return variant



class Segment(object):
    colors = {0:"red", 1:"blue", 2:"gray", 3:"green", 4:"brown"}

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

class StructuralVariant(object):
    def __init__(self, breakpoints, alignDistance, fasta):
        self.breakpoints = sorted(breakpoints, key=lambda x: x.start())
        self.alignDistance = alignDistance

        self.sources = {"genome":fasta}

        self._refseq = None
        self._altseq = None

    def __str__(self):
        return "{}({};{})".format(self.__class__.__name__, self.breakpoints, self.alignDistance)

    def searchRegions(self):
        pass    
    def getRefSeq(self):
        return self.getSeq("ref")
    def getAltSeq(self):
        return self.getSeq("alt")

    def getSeq(self, allele):
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
        return "".join(seqs).upper()

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

    # def getRefSeq(self):
    #     if self._refseq is not None:
    #         return self._refseq

    #     chrom = self.breakpoints[0].chr()
    #     start = self.breakpoints[0].start() - self.alignDistance
    #     end = self.breakpoints[-1].end() + self.alignDistance

    #     self._refseq = self.fasta[chrom][start:end+1]
    #     return self._refseq.upper()

    # def _getRefRelativeBreakpoints(self):
    #     return [self.alignDistance, self.alignDistance+self.breakpoints[-1].start()-self.breakpoints[0].end()]
    # def _getAltRelativeBreakpoints(self):
    #     return [self.alignDistance]

    # def getAltSeq(self):
    #     if self._altseq is not None:
    #         return self._altseq
    #     chrom = self.breakpoints[0].chr()
    #     upstream = self.fasta[chrom][self.breakpoints[0].start()-self.alignDistance:
    #                                  self.breakpoints[0].end()+1]
    #     downstream = self.fasta[chrom][self.breakpoints[-1].start():
    #                                    self.breakpoints[-1].end()+self.alignDistance+1]

    #     self._altseq = upstream.upper() + downstream.upper()
    #     return self._altseq


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
        chrom = self.breakpoints[0].chr()

        if allele in ["ref", "amb"]:
            return [Segment(chrom, self.breakpoints[0].start()-self.alignDistance, self.breakpoints[0].start()-1, "+", 0),
                    Segment(chrom, self.breakpoints[0].end()+1, self.breakpoints[0].end()+self.alignDistance, "+", 2)]
        elif allele == "alt":
            return [Segment(chrom, self.breakpoints[0].start()-self.alignDistance, self.breakpoints[0].start()-1, "+", 0),
                    Segment("insertion", 0, self.insertionLength, "+", 1, source="insertion"),
                    Segment(chrom, self.breakpoints[0].end()+1, self.breakpoints[0].end()+self.alignDistance, "+", 2)]

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
                    Segment(chrom, self.breakpoints[0].end()+1, self.breakpoints[0].end()+self.alignDistance, "+", 2)]
        elif allele == "alt":
            return [Segment(chrom, self.breakpoints[0].start()-self.alignDistance, self.breakpoints[0].start()-1, "+", 0),
                    Segment(self.insertedSeqLocus.chr(), self.insertedSeqLocus.start(), 
                        self.insertedSeqLocus.end(), self.insertedSeqLocus.strand(), 1, source="repeats"),
                    Segment(chrom, self.breakpoints[0].end()+1, self.breakpoints[0].end()+self.alignDistance, "+", 2)]

    def __str__(self):
        return "{}::{}({});{})".format(self.__class__.__name__, self.insertedSeqLocus.chr(), self.breakpoints, self.alignDistance)




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