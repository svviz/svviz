import collections
import logging
import time
# import numpy
import math
import pyfaidx
import pysam
from Multiprocessor import Multiprocessor

from utilities import reverseComp
import StructuralVariants
from Alignment import Alignment, AlignmentSet, AlignmentSetCollection
from PairFinder import PairFinder

def log2(x):
    try:
        return math.log(x, 2)
    except ValueError:
        return float("nan")


def check_swalign():
    try:
        from ssw import ssw_wrap
        aligner = ssw_wrap.Aligner("AGTCGT", report_cigar=True, report_secondary=True)
        aligner.align("AGTC")
    except OSError:
        return False

    return True


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
        from ssw import ssw_wrap
        self.aligner = ssw_wrap.Aligner(refseq, report_cigar=True, report_secondary=True)

    def remap(self, seq):
        # print seq
        return seq, findBestAlignment(seq, self.aligner)

def do1remap(refseq, reads):
    # mm = Multimap(refseq)
    # remapped = dict(map(mm.remap, [read.seq for read in reads]))

    # tempf = open("reads.txt", "w")
    # for read in reads:
    #     tempf.write(read.seq+"\n")

    # tempg = open("genome.txt", "w")
    # tempg.write(refseq)

    # return

    degenerateOnly = set("N")
    originalLength = len(reads)
    reads = [read for read in reads if set(read.seq) != degenerateOnly]
    if len(reads) < originalLength:
        logging.info("Removed {} reads with only degenerate nucleotides ('N')".format(originalLength-len(reads)))

    remapped = dict(Multimap.map(Multimap.remap, [read.seq for read in reads], initArgs=[refseq], verbose=3, processes=8))

    # mm = Multimap(refseq)
    # remapped = dict(map(mm.remap, [read.seq for read in reads]))

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
        aln = Alignment(read.qname, aln.ref_begin, aln.ref_end, strand, seq, aln.cigar_string, aln.score, genome_seq, aln.score2)
        alignmentSets[read.qname].addAlignment(aln)

    return alignmentSets


def getReads(variant, bam, minmapq, searchDistance, single_ended=False):
    t0 = time.time()
    searchRegions = variant.searchRegions(searchDistance)
    pairFinder = PairFinder(searchRegions, bam, minmapq=minmapq, is_paired=(not single_ended))
    reads = [item for sublist in pairFinder.matched for item in sublist]
    t1 = time.time()

    logging.debug("  time to find reads and mates:{}".format(t1 - t0))
    logging.info("  number of reads found: {}".format(len(reads)))

    return reads

def do_realign(variant, reads):
    # reads = reads[:25]

    t0 = time.time()
    refalignments = do1remap(variant.getRefSeq(), reads)
    altalignments = do1remap(variant.getAltSeq(), reads)
    t1 = time.time()

    logging.debug("time for realigning:{}".format(t1-t0))

    assert refalignments.keys() == altalignments.keys()

    alnCollections = []
    for key in refalignments:
        alnCollection = AlignmentSetCollection(key)
        alnCollection.addSet(refalignments[key], "ref")
        alnCollection.addSet(altalignments[key], "alt")
        alnCollections.append(alnCollection)

    return alnCollections




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