import collections
import logging
import os
import pyfaidx
import pysam
import time

from svviz import debug
import InsertSizeProbabilities
import CommandLine
import StructuralVariants
import remap
import track
from utilities import Locus, reverseComp
import misc


def getListDefault(list_, index, default=None):
    if len(list_) <= index:
        return default

    return list_[index]

def savereads(args, bam, reads, n=None):
    if args.save_reads:
        outbam_path = args.save_reads
        if not outbam_path.endswith(".bam"):
            outbam_path += ".bam"

        if n is not None:
            logging.debug("Using i = {}".format(n))
            outbam_path = outbam_path.replace(".bam", ".{}.bam".format(n))

        # print out just the reads we're interested for use later
        bam_small = pysam.Samfile(outbam_path, "wb", template=bam)
        for read in reads:
            bam_small.write(read)

        bam_small.close()
        sorted_path = outbam_path.replace(".bam", ".sorted")
        pysam.sort(outbam_path, sorted_path)
        pysam.index(sorted_path+".bam")


def getVariant(args, genome):
    extraSpace = int(args.isize_mean) * 2

    if args.type.lower().startswith("del"):
        if args.deldemo:
            chrom, start, end = "chr1", 72766323, 72811840
        else:
            assert len(args.breakpoints) == 3, "Format for deletion breakpoints is '<chrom> <start> <end>'"
            chrom = args.breakpoints[0]
            start = int(args.breakpoints[1])
            end = int(args.breakpoints[2])
            assert start < end
        if args.min_mapq is None:
            args.min_mapq = 30

        variant = StructuralVariants.Deletion.from_breakpoints(chrom, start-1, end-1, extraSpace, genome)
    elif args.type.lower().startswith("ins"):
        if args.insdemo:
            chrom, pos, seq = "chr3", 20090540, reverseComp(misc.L1SEQ)
        else:
            assert len(args.breakpoints) == 3, "Format for insertion breakpoints is '<chrom> <pos> <seq>'"
            chrom = args.breakpoints[0]
            pos = int(args.breakpoints[1])
            seq = int(args.breakpoints[2])
        if args.min_mapq is None:
            args.min_mapq = -1

        variant = StructuralVariants.Insertion(Locus(chrom, pos, pos, "+"), seq, extraSpace, genome)
    elif args.type.lower().startswith("mei"):
        assert len(args.breakpoints) >= 4, "Format for mobile element insertion is '<mobile_elements.fasta> <chrom> <pos> <ME name> [ME strand [start [end]]]'"
        if args.min_mapq is None:
            args.min_mapq = -1

        insertionBreakpoint = Locus(args.breakpoints[1], args.breakpoints[2], args.breakpoints[2], "+")

        meName = args.breakpoints[3]
        meStrand = getListDefault(args.breakpoints, 4, "+")
        meStart = getListDefault(args.breakpoints, 5, 0)
        meEnd = getListDefault(args.breakpoints, 6, 1e100)

        meCoords = Locus(meName, meStart, meEnd, meStrand)
        meFasta = pyfaidx.Fasta(args.breakpoints[0], as_raw=True)

        variant = StructuralVariants.MobileElementInsertion(insertionBreakpoint, meCoords, meFasta, extraSpace, genome)
    else:
        raise Exception("only accept event types of deletion or insertion")

    logging.info("Variant: {}".format(variant))

    return variant

def getTracks(chosenSets, variant, name="x"):
    svgs = {}

    ref_chrom = track.ChromosomePart(variant.getRefSeq())
    ref_track = track.Track(ref_chrom, chosenSets["ref"], 3000, 4000, 0, len(variant.getRefSeq()), vlines=variant.getRefRelativeBreakpoints())
    svgs["ref"] = ref_track.render()

    alt_chrom = track.ChromosomePart(variant.getAltSeq())
    alt_track = track.Track(alt_chrom, chosenSets["alt"], 5000, 15000, 0, len(variant.getAltSeq()), vlines=variant.getAltRelativeBreakpoints())
    svgs["alt"] = alt_track.render()

    amb_track = track.Track(ref_chrom, chosenSets["amb"], 4000, 10000, 0, len(variant.getRefSeq()), vlines=variant.getRefRelativeBreakpoints())
    svgs["amb"] = amb_track.render()

    return svgs


def main():
    args = CommandLine.parseArgs()
    run(args)

def run(args):
    logging.debug(args)

    genome = pyfaidx.Fasta(args.ref, as_raw=True)
    variant = getVariant(args, genome)
    datasets = collections.OrderedDict()

    

    # from IPython import embed; embed()

    for i, bampath in enumerate(args.bam):
        name = os.path.basename(bampath).replace(".bam", "").replace(".sorted", "").replace(".sort", "").replace(".", "_").replace("+", "_")
        bam = pysam.Samfile(bampath, "rb")

        reads = remap.getReads(variant, bam, args.min_mapq)
        savereads(args, bam, reads, i)

        alnCollections = remap.do_realign(variant, reads)
        isd = InsertSizeProbabilities.InsertSizeDistribution(bam)
        remap.disambiguate(alnCollections, isd, args.isize_mean, 2*args.isize_std, args.orientation, bam)

        chosenSets = collections.defaultdict(list)
        for alnCollection in alnCollections:
            chosenSets[alnCollection.choice].append(alnCollection.chosenSet())

        datasets[name] = {"alnCollections":alnCollections,
                          "chosenSets":chosenSets,
                          "isd": isd,
                          "counts":collections.Counter([x.choice for x in alnCollections])}

    if not args.no_web:
        # launch web view
        import web

        web.SVGsByDataset = {}

        for name in datasets:
            web.SVGsByDataset[name] = getTracks(datasets[name]["chosenSets"], variant, name)

        web.READ_INFO = {}
        web.RESULTS = collections.OrderedDict()
        for name in datasets:
            dataset = datasets[name]
            for readCollection in dataset["alnCollections"]:
                web.READ_INFO[readCollection.name] = readCollection.chosenSet()
            web.RESULTS[name] = dataset["counts"]

        web.RESULTS["Total"] = dict((col, sum(web.RESULTS[row][col] for row in web.RESULTS)) for col in ["alt", "ref", "amb"])
        web.SAMPLES = datasets.keys()

        if all(not dataset["isd"].fail for dataset in datasets.itervalues()):
            web.ISIZES = web.SAMPLES
            for name in web.SAMPLES:
                isd = datasets[name]["isd"]
                InsertSizeProbabilities.plotInsertSizeDistribution(isd, name, datasets[name])

        web.run()


if __name__ == '__main__':
    main()