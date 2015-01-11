from utilities import Locus, reverseComp

class Segment(object):
    colors = {0:"red", 1:"blue", 2:"gray", 3:"green", 4:"brown"}

    def __init__(self, start, end, strand, id_):
        self.start = start
        self.end = end
        self.strand = strand
        self.id = id_
    def color(self):
        return self.colors[self.id]

class StructuralVariant(object):
    def __init__(self, breakpoints, alignDistance, fasta):
        self.breakpoints = sorted(breakpoints, key=lambda x: x.start())
        self.alignDistance = alignDistance
        self.fasta = fasta

        self._refseq = None
        self._altseq = None

    def __str__(self):
        return "{}({};{})".format(self.__class__.__name__, self.breakpoints, self.alignDistance)

    def searchRegions(self):
        pass    
    def getRefSeq(self):
        pass
    def getAltSeq(self):
        pass

    def getRelativeBreakpoints(self, which):
        if which in ["ref", "amb"]:
            return self._getRefRelativeBreakpoints()
        elif which == "alt":
            return self._getAltRelativeBreakpoints()
        else:
            raise Exception("unknown allele {}".format(which))            

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

    def getRefSeq(self):
        if self._refseq is not None:
            return self._refseq

        chrom = self.breakpoints[0].chr()
        start = self.breakpoints[0].start() - self.alignDistance
        end = self.breakpoints[-1].end() + self.alignDistance

        # self._refseq = self.genomeFetch.get_seq_from_to(chrom, start, end, "+").upper()
        self._refseq = self.fasta[chrom][start:end+1]
        return self._refseq.upper()

    def _getRefRelativeBreakpoints(self):
        return [self.alignDistance, self.alignDistance+self.breakpoints[-1].start()-self.breakpoints[0].end()]
    def _getAltRelativeBreakpoints(self):
        return [self.alignDistance]

    def getAltSeq(self):
        if self._altseq is not None:
            return self._altseq
        chrom = self.breakpoints[0].chr()
        upstream = self.fasta[chrom][self.breakpoints[0].start()-self.alignDistance:
                                     self.breakpoints[0].end()+1]
        downstream = self.fasta[chrom][self.breakpoints[-1].start():
                                       self.breakpoints[-1].end()+self.alignDistance+1]

        self._altseq = upstream.upper() + downstream.upper()
        return self._altseq


class Inversion(StructuralVariant):
    def __init__(self, region, alignDistance, fasta):
        breakpoints = [Locus(region.chr(), region.start(), region.start(), "+"), Locus(region.chr(), region.end(), region.end(), "+")]
        super(Inversion, self).__init__(breakpoints, alignDistance, fasta)

        self.region = region

    def searchRegions(self, searchDistance):
        chrom = self.region.chr()

        if len(self.region) < 2*searchDistance:
            # return a single region
            return [Locus(chrom, self.region.start()-searchDistance, self.region.end()+searchDistance, "+")]
        else:
            # return two regions, each around one of the ends of the inversion
            searchRegions = []
            searchRegions.append(Locus(chrom, self.region.start()-searchDistance, self.region.start()+searchDistance, "+"))
            searchRegions.append(Locus(chrom, self.region.end()-searchDistance, self.region.end()+searchDistance, "+"))
            return searchRegions

    def getRefSeq(self):
        if self._refseq is None:
            chrom = self.region.chr()
            start = self.region.start() - self.alignDistance
            end = self.region.end() + self.alignDistance

            self._refseq = self.fasta[chrom][start:end+1].upper()
        return self._refseq

    def _getRefRelativeBreakpoints(self):
        return [self.alignDistance, self.alignDistance+len(self.region)]

    def _getAltRelativeBreakpoints(self):
        return [self.alignDistance, self.alignDistance+len(self.region)]

    def getAltSeq(self):
        if self._altseq is None:
            chrom = self.region.chr()
            before = self.fasta[chrom][self.region.start()-self.alignDistance:
                                       self.region.start()]
            within = reverseComp(self.fasta[chrom][self.region.start():self.region.end()+1])
            after = self.fasta[chrom][self.region.end()+1:
                                      self.region.end()+self.alignDistance+1]

            self._altseq = before + within + after
            self._altseq = self._altseq.upper()                       
        return self._altseq

    def __str__(self):
        return "{}::{}:{:,}-{:,}".format(self.__class__.__name__, self.region.chr(), self.region.start(), self.region.end())


class Insertion(StructuralVariant):
    def __init__(self, breakpoint, insertSeq, alignDistance, fasta):
        super(Insertion, self).__init__([breakpoint], alignDistance, fasta)
        self.insertSeq = insertSeq

    def searchRegions(self, searchDistance):
        chrom = self.breakpoints[0].chr()
        return [Locus(chrom, self.breakpoints[0].start()-searchDistance, self.breakpoints[-1].end()+searchDistance, "+")]

    def getRefSeq(self):
        chrom = self.breakpoints[0].chr()
        start = self.breakpoints[0].start()-self.alignDistance
        end = self.breakpoints[-1].end()+self.alignDistance+1
        return self.fasta[chrom][start:end].upper()

    def _getRefRelativeBreakpoints(self):
        return [self.alignDistance]

    def getAltSeq(self):
        chrom = self.breakpoints[0].chr()
        before = self.fasta[chrom][self.breakpoints[0].start()-self.alignDistance:
                                   self.breakpoints[0].start()]
        after = self.fasta[chrom][self.breakpoints[0].start():
                                  self.breakpoints[0].start()+self.alignDistance+1]
        return before.upper() + self.insertSeq + after.upper()

    def _getAltRelativeBreakpoints(self):
        return [self.alignDistance, self.alignDistance+len(self.insertSeq)]

    def segments(self, allele):
        # for visual display of the different segments between breakpoints

        if allele in ["ref", "amb"]:
            return [Segment(0, self.alignDistance, "+", 0),
                    Segment(self.alignDistance, self.alignDistance*2, "+", 1)]
        elif allele == "alt":
            return [Segment(0, self.alignDistance, "+", 0),
                    Segment(self.alignDistance, self.alignDistance+len(self.insertSeq), "+", 2),
                    Segment(self.alignDistance+len(self.insertSeq), self.alignDistance*2+len(self.insertSeq), "+", 1)]
                
class MobileElementInsertion(Insertion):
    def __init__(self, breakpoint, insertedSeqLocus, insertionFasta, alignDistance, refFasta):
        self.insertedSeqLocus = insertedSeqLocus
        insertionSequence = insertionFasta[insertedSeqLocus.chr()][insertedSeqLocus.start():insertedSeqLocus.end()+1].upper()
        if insertedSeqLocus.strand() == "-":
            insertionSequence = reverseComp(insertionSequence)

        super(MobileElementInsertion, self).__init__(breakpoint, insertionSequence, alignDistance, refFasta)

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