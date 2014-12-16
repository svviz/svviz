import numpy
import pysam
import random
import multiprocessing
from svviz import Multiprocessor, utilities

from ssw import ssw_wrap
from svviz import Alignment

# random.seed(2532)

def getRef():
    ref = "".join(random.choice("ACGT") for i in range(2000))
    return ref


def getReads(ref):
    reads = []
    for i in range(10000):
        start = random.randint(0, len(ref)-100)
        end = random.randint(start+50, len(ref))
        read = list(ref[start:end])

        for i in range(random.randint(2,5)):
            pos = random.randint(0, len(read)-1)
            read[pos] = random.choice(list(set("ACGT")-set(read[pos])))
        reads.append("".join(read))

    return reads




def findBestAlignment(seq, aligner):
    revseq = utilities.reverseComp(seq)
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


class Multimap(Multiprocessor.Multiprocessor):
    def __init__(self, refseq):
        self.aligner = ssw_wrap.Aligner(refseq, report_cigar=True, report_secondary=True)

    def remap(self, seq):
        return seq, findBestAlignment(seq, self.aligner)


def main():
    # aligner = ssw_wrap.Aligner(ref, report_cigar=True)

    # for read in reads:
    #     aln = aligner.align(read)


    # pool = multiprocessing.Pool()

    reads = []
    readf = open("reads.txt")
    for line in readf:
        reads.append(line.strip())
    ref = open("genome.txt").read().strip()

    for i in range(100):
        print i
        # ref = getRef()
        # reads = getReads(ref)

        x = Multimap.map(Multimap.remap, reads, processes=1, verbose=10, initArgs=[ref])
        print len(x)

        read, aln = x[-1]
        strand, aln = aln
        print x[-1]
        genome_seq = ref[aln.ref_begin:aln.ref_end+1].upper()
        print Alignment._getBlastRepresentation(read, genome_seq, aln.cigar_string)


if __name__ == '__main__':
    main()


