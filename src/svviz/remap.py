import collections
import logging
# import multiprocessing
import time
# import numpy
import math
from svviz.multiprocessor import Multiprocessor

from svviz.utilities import reverseComp, Locus
from svviz.alignment import Alignment, AlignmentSet, AlignmentSetCollection
from svviz.pairfinder import PairFinder
from svviz import misc

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
    def __init__(self, namesToReferences):
        from ssw import ssw_wrap

        self.namesToAligners = {}
        for name, ref in namesToReferences.iteritems():
            self.namesToAligners[name] = ssw_wrap.Aligner(ref, report_cigar=True, report_secondary=True)

    def remap(self, seq):
        results = {}
        for name, aligner in self.namesToAligners.iteritems():
            results[name] = findBestAlignment(seq, aligner)
        return seq, results


def filterDegenerateOnly(reads):
    degenerateOnly = set("N")
    filtered = [read for read in reads if set(read.seq) != degenerateOnly]
    if len(filtered) < len(reads):
        logging.info("  Removed {} reads with only degenerate nucleotides ('N')".format(len(reads)-len(filtered)))
    return filtered

def chooseBestAlignment(read, mappings, chromPartsCollection):
    # TODO: this should be read-pair aware
    # TODO: this is kind of ridiculous; we need to make pickleable reads that can be sent to 
    # and from the Multimapper
    # mappings: name -> (strand, aln)
    bestName = None
    bestAln = None
    bestStrand = None
    secondScore = None

    for name, mapping in mappings.iteritems():
        strand, aln = mapping
        if bestAln is None or aln.score > bestAln.score:
            bestName = name
            bestAln = aln
            bestStrand = strand

    for name, mapping in mappings.iteritems():
        strand, aln = mapping
        if name == bestName:
            if secondScore is None or bestAln.score2 > secondScore:
                secondScore = bestAln.score2
        else:
            if secondScore is None or aln.score > secondScore:
                secondScore = aln.score

    seq = read.seq
    genome_seq = chromPartsCollection.getPart(bestName).getSeq()[bestAln.ref_begin:bestAln.ref_end+1].upper()

    if bestStrand == "-":
        seq = reverseComp(seq)
    if read.is_reverse:
        bestStrand = "+" if bestStrand=="-" else "-"
    bestAln = Alignment(read.qname, bestName, bestAln.ref_begin, bestAln.ref_end, bestStrand, seq, bestAln.cigar_string, 
                    bestAln.score, genome_seq, secondScore, read.mapq)
    return bestAln


def do1remap(chromPartsCollection, reads, processes):
    reads = filterDegenerateOnly(reads)

    namesToReferences = {}
    for name, chromPart in chromPartsCollection.parts.iteritems():
        namesToReferences[chromPart.id] = chromPart.getSeq()

    # map each read sequence against each chromosome part (the current allele only)

    if processes != 1:
        remapped = dict(Multimap.map(Multimap.remap, [read.seq for read in reads], initArgs=[namesToReferences], 
            verbose=3, processes=processes))#multiprocessing.cpu_count()))
    else:
        mapper = Multimap(namesToReferences)

        remapped = {}
        for i, read in enumerate(reads):
            if i % 1000 == 0:
                print "realigned", i, "of", len(reads)
            seq, result = mapper.remap(read.seq)
            remapped[seq] = result

    alignmentSets = collections.defaultdict(AlignmentSet)
    for read in reads:
        # TODO: for paired-end, if there are equally-scoring alignments in multiple parts, we should pick
        # the pair which are in the correct orientation
        aln = chooseBestAlignment(read, remapped[read.seq], chromPartsCollection)
        alignmentSets[read.qname].addAlignment(aln)

    return alignmentSets



def _getreads(searchRegions, bam, minmapq, pair_minmapq, single_ended, include_supplementary):
    pairFinder = PairFinder(searchRegions, bam, minmapq=minmapq, pair_minmapq=pair_minmapq,
        is_paired=(not single_ended), include_supplementary=include_supplementary)
    reads = [item for sublist in pairFinder.matched for item in sublist]
    return reads, pairFinder.supplementaryAlignmentsFound

def getReads(variant, bam, minmapq, pair_minmapq, searchDistance, single_ended=False, include_supplementary=False):
    t0 = time.time()
    searchRegions = variant.searchRegions(searchDistance)

    # This cludge tries the chromosomes as given ('chr4' or '4') and if that doesn't work
    # tries to switch to the other variation ('4' or 'chr4')
    try:
        reads, supplementaryAlignmentsFound = _getreads(searchRegions, bam, minmapq, pair_minmapq, single_ended, include_supplementary)
    except ValueError, e:
        oldchrom = searchRegions[0].chr()
        try:
            if "chr" in oldchrom:
                newchrom = oldchrom.replace("chr", "")
                searchRegions = [Locus(l.chr().replace("chr", ""), l.start(), l.end(), l.strand()) for l in searchRegions]
            else:
                newchrom = "chr{}".format(oldchrom)
                searchRegions = [Locus("chr{}".format(l.chr()), l.start(), l.end(), l.strand()) for l in searchRegions]

            logging.warn("  Couldn't find reads on chromosome '{}'; trying instead '{}'".format(oldchrom, newchrom))

            reads, supplementaryAlignmentsFound = _getreads(searchRegions, bam, minmapq, pair_minmapq, single_ended, include_supplementary)

        except ValueError:
            raise e
    t1 = time.time()

    if supplementaryAlignmentsFound:
        logging.warn("  ** Supplementary alignments found: these alignments (with sam flag 0x800) **\n"
                     "  ** are poorly documented among mapping software and may result in missing **\n"
                     "  ** portions of reads; consider using the --include-supplementary command line **\n"
                     "  ** argument if you think this is happening                                **")
        
    logging.debug("  time to find reads and mates:{}".format(t1 - t0))
    logging.info("  number of reads found: {}".format(len(reads)))

    return reads

def do_realign(variant, reads, processes=None):
    if processes is None or processes == 0:
        # we don't really gain from using virtual cores, so try to figure out how many physical
        # cores we have
        processes = misc.cpu_count_physical()

    t0 = time.time()
    refalignments = do1remap(variant.chromParts("ref"), reads, processes)
    altalignments = do1remap(variant.chromParts("alt"), reads, processes)
    t1 = time.time()

    logging.debug("  time for realigning:{}".format(t1-t0))

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