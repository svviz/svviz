import collections
import time
import pyfaidx
import pysam
from ssw import ssw_wrap
from Multiprocessor import Multiprocessor

from utilities import reverseComp
import StructuralVariants
from Alignment import Alignment, AlignmentSet
from PairFinder import PairFinder


def findBestAlignment(seq, aligner):
    revseq = reverseComp(seq)
    forward_al = aligner.align(seq)
    reverse_al = aligner.align(revseq)

    strand = None

    if not forward_al:
        if reverse_al:
            strand = "-"
    else:
        if not reverse_al:
            strand = "+"
        else:
            if forward_al.score >= reverse_al.score:
                strand = "+"
            else:
                strand = "-"

    if strand == "+":
        return "+", forward_al
    else:
        return "-", reverse_al


class Multimap(Multiprocessor):
    def __init__(self, refseq):
        self.aligner = ssw_wrap.Aligner(refseq, report_cigar=True)

    def remap(self, seq):
        return seq, findBestAlignment(seq, self.aligner)

def do1remap(refseq, reads):
    remapped = dict(Multimap.map(Multimap.remap, [read.seq for read in reads], initArgs=[refseq], verbose=3, processes=8))

    alignmentSets = collections.defaultdict(AlignmentSet)
    for read in reads:
        strand, aln = remapped[read.seq]
        seq = read.seq

        genome_seq = refseq[aln.ref_begin:aln.ref_end+1].upper()

        if strand == "-":
            seq = reverseComp(seq)
            # genome_seq = reverseComp(genome_seq)
        if read.is_reverse:
            strand = "+" if strand=="-" else "-"
        aln = Alignment(read.qname, aln.ref_begin, aln.ref_end, strand, seq, aln.cigar_string, aln.score, genome_seq)
        alignmentSets[read.qname].addAlignment(aln)

    return alignmentSets



def do_realign(variant, bam, minmapq):
    t0 = time.time()
    pairFinder = PairFinder(variant.searchRegions(), bam, minmapq=minmapq)
    reads = [item for sublist in pairFinder.matched for item in sublist]
    t1 = time.time()

    print "time to find reads and mates:", t1 - t0
    print "number of reads found:", len(reads)

    # reads = reads[:25]

    t0 = time.time()
    refalignments = do1remap(variant.getRefSeq(), reads)
    altalignments = do1remap(variant.getAltSeq(), reads)
    t1 = time.time()

    print "time for realigning:", t1-t0

    return refalignments, altalignments, reads



def disambiguate(refalignments, altalignments, MEAN_INSERT_SIZE, INSERT_SIZE_2STD, ORIENTATION):
    print ORIENTATION, MEAN_INSERT_SIZE, INSERT_SIZE_2STD

    selectedRefAlignments = []
    selectedAltAlignments = []
    selectedAmbiguousAlignments = []

    # count = 0
    for key in set(refalignments).union(set(altalignments)):
        # if count > 200:
        #     break
        # count += 1
        refset = refalignments[key]
        altset = altalignments[key]

        refscore = sum(aln.score for aln in refset.getAlignments())
        altscore = sum(aln.score for aln in altset.getAlignments())

        # print refscore, altscore, refset.getAlignments()[0].seq, refset.getAlignments()[1].seq

        if refscore == altscore and refset.allSegmentsWellAligned():
            if refset.is_aligned() and abs(len(refset) - MEAN_INSERT_SIZE) < INSERT_SIZE_2STD and refset.orientation() == ORIENTATION:
                if altset.is_aligned() and abs(len(altset) - MEAN_INSERT_SIZE) < INSERT_SIZE_2STD and altset.orientation() == ORIENTATION:
                    # both good
                    # print refscore, altscore
                    selectedAmbiguousAlignments.append(refset)
                    refset.color = "blue"
                else:
                    selectedRefAlignments.append(refset)
                    refset.color = "black"
            elif altset.is_aligned() and abs(len(altset) - MEAN_INSERT_SIZE) < INSERT_SIZE_2STD and altset.orientation() == ORIENTATION:
                selectedAltAlignments.append(altset)
                altset.color = "red"
            else:
                selectedAmbiguousAlignments.append(refset)
                refset.color = "orange"
        elif refscore > altscore and refset.allSegmentsWellAligned():
            if abs(len(refset) - MEAN_INSERT_SIZE) < INSERT_SIZE_2STD and refset.orientation() == ORIENTATION:
                selectedRefAlignments.append(refset)
                refset.color = "purple"
            else:
                selectedAmbiguousAlignments.append(refset)
                refset.color = "gray"
        elif altset.allSegmentsWellAligned():
            if abs(len(altset) - MEAN_INSERT_SIZE) < INSERT_SIZE_2STD and altset.orientation() == ORIENTATION:
                selectedAltAlignments.append(altset)
                altset.color = "green"
            else:
                selectedAmbiguousAlignments.append(refset)
                refset.color = "gray"
        # else:
        #     selectedAmbiguousAlignments.append(refset)
        #     refset.color = "red"

    return selectedAltAlignments, selectedRefAlignments, selectedAmbiguousAlignments


def main():
    pass
    # genomeFastaPath = sys.argv[1]
    # genome = pyfaidx.Fasta(genomeFastaPath, as_raw=True)

    # bamPath = sys.argv[2]
    # bam = pysam.Samfile(bamPath, "rb")

    # eventType = sys.argv[3]

    # if eventType.lower().startswith("del"):
    #     if len(sys.argv) == 4:
    #         chrom, start, end = "chr1", 72766323, 72811840
    #     else:
    #         chrom = sys.argv[4]
    #         start = int(sys.argv[5])
    #         end = int(sys.argv[6])
    #     minmapq = 30

    #     variant = StructuralVariants.Deletion.from_breakpoints(chrom, start-1, end-1, extraSpace, genome)

    # elif eventType.lower().startswith("ins"):
    #     if len(sys.argv) == 4:
    #         chrom, pos, seq = "chr3", 20090540, L1SEQ
    #     else:
    #         chrom = sys.argv[4]
    #         pos = int(sys.argv[5])
    #         seq = int(sys.argv[6])
    #     minmapq = -1
    #     variant = StructuralVariants.Insertion(Locus(chrom, pos, pos, "+"), reverseComp(seq), extraSpace, genome)





if __name__ == '__main__':
    main()