import collections
import logging
import os
import subprocess
import sys

import pyfaidx
import pysam

from svviz import debug
from svviz import InsertSizeProbabilities
from svviz import CommandLine
from svviz import StructuralVariants
from svviz import remap
from svviz import disambiguate
from svviz import track
from svviz import export
from svviz.utilities import Locus, nameFromBamPath
from svviz.export import TrackCompositor


def launchFile(filepath):
    if sys.platform.startswith('darwin'):
        subprocess.call(('open', filepath))
    elif os.name == 'nt':
        os.startfile(filepath)
    elif os.name == 'posix':
        subprocess.call(('xdg-open', filepath))

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


def getVariant(args, genome, isds):
    if args.search_dist is None:
        args.search_dist = args.isize_mean * 2

    alignDistance = int(max(args.search_dist, args.isize_mean*2))

    if args.type.lower().startswith("del"):
        # if args.deldemo:
        #     chrom, start, end = "chr1", 72766323, 72811840
        # else:
        assert len(args.breakpoints) == 3, "Format for deletion breakpoints is '<chrom> <start> <end>'"
        chrom = args.breakpoints[0]
        start = int(args.breakpoints[1])
        end = int(args.breakpoints[2])
        assert start < end
        if args.min_mapq is None:
            args.min_mapq = 30

        variant = StructuralVariants.Deletion.from_breakpoints(chrom, start-1, end-1, alignDistance, genome)
    elif args.type.lower().startswith("ins"):
        # if args.insdemo:
        #     chrom, pos, seq = "chr3", 20090540, reverseComp(misc.L1SEQ)
        # else:
        assert len(args.breakpoints) == 3, "Format for insertion breakpoints is '<chrom> <pos> <seq>'"
        chrom = args.breakpoints[0]
        pos = int(args.breakpoints[1])
        seq = args.breakpoints[2]
        if args.min_mapq is None:
            args.min_mapq = -1

        variant = StructuralVariants.Insertion(Locus(chrom, pos, pos, "+"), seq, alignDistance, genome)
    elif args.type.lower().startswith("inv"):
        assert len(args.breakpoints) == 3, "Format for insertion breakpoints is '<chrom> <start> <end>'"
        chrom = args.breakpoints[0]
        start = int(args.breakpoints[1])
        end = int(args.breakpoints[2])
        if args.min_mapq is None:
            args.min_mapq = -1

        variant = StructuralVariants.Inversion(Locus(chrom, start, end, "+"), alignDistance, genome)
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

        variant = StructuralVariants.MobileElementInsertion(insertionBreakpoint, meCoords, meFasta, alignDistance, genome)
    else:
        raise Exception("only accept event types of deletion, insertion or mei")

    logging.info("Variant: {}".format(variant))

    return variant


def getTracks(chosenSets, variant, name):
    tracks = {}

    ref_chrom = track.ChromosomePart(variant.getRefSeq())
    ref_track = track.Track(ref_chrom, chosenSets["ref"], 3000, 4000, 0, len(variant.getRefSeq()), variant=variant, allele="ref")
    tracks["ref"] = ref_track

    alt_chrom = track.ChromosomePart(variant.getAltSeq())
    alt_track = track.Track(alt_chrom, chosenSets["alt"], 5000, 15000, 0, len(variant.getAltSeq()), variant=variant, allele="alt")
    tracks["alt"] = alt_track

    amb_track = track.Track(ref_chrom, chosenSets["amb"], 4000, 10000, 0, len(variant.getRefSeq()), variant=variant, allele="amb")
    tracks["amb"] = amb_track

    return tracks


def getISDs(args):
    """ Load the Insert Size Distributions """

    isds = {}
    for bampath in args.bam:
        name = nameFromBamPath(bampath)
        bam = pysam.Samfile(bampath, "rb")

        isds[name] = InsertSizeProbabilities.InsertSizeDistribution(bam, saveReads=True)

    if args.isize_mean is None or args.isize_std is None:
        mean_isizes = [isd.mean() for isd in isds.values()]
        std_isizes = [isd.std() for isd in isds.values()]

        logging.debug("calculated isize (mean, std): {}".format(zip(mean_isizes, std_isizes)))

        mean_isizes = [mean for mean in mean_isizes if mean is not None]
        std_isizes = [std for std in std_isizes if std is not None]

        if len(mean_isizes) > 0 and len(std_isizes) > 0:
            if args.isize_mean is None:
                args.isize_mean = max(mean_isizes)
                logging.info("isize-mean not specified; using value {} inferred from input data".format(args.isize_mean))
            if args.isize_std is None:
                args.isize_std = max(std_isizes)
                logging.info("isize-std not specified; using value {} inferred from input data".format(args.isize_std))
        else:
            raise Exception("Could not infer isize-mean from input files; make sure you have genome-wide read coverage in the input bams, or pass in the --isize-mean option on the command line")

    return isds

def main():
    if not remap.check_swalign():
        print "ERROR: check that svviz is correctly installed -- the 'ssw' Smith-Waterman alignment module does not appear to be functional"
        sys.exit(1)

    args = CommandLine.parseArgs()
    run(args)

def run(args):
    logging.debug(args)

    # need to calculate insert size distributions before defining the variant
    isds = getISDs(args)

    genome = pyfaidx.Fasta(args.ref, as_raw=True)
    variant = getVariant(args, genome, isds)
    datasets = collections.OrderedDict()


    for i, bampath in enumerate(args.bam):
        name = nameFromBamPath(bampath)
        bam = pysam.Samfile(bampath, "rb")
        curisd = isds[name]

        reads = remap.getReads(variant, bam, args.min_mapq, args.search_dist, args.single_ended)
        savereads(args, bam, reads+curisd.reads, i)

        alnCollections = remap.do_realign(variant, reads)
        # remap.disambiguate(alnCollections, curisd, args.isize_mean, 2*args.isize_std, args.orientation, bam, args.single_ended)
        expectedOrientations = args.orientation
        if args.single_ended:
            expectedOrientations = "any"
        disambiguate.batchDisambiguate(alnCollections, curisd, expectedOrientations, singleEnded=args.single_ended)


        chosenSets = collections.defaultdict(list)
        for alnCollection in alnCollections:
            chosenSets[alnCollection.choice].append(alnCollection.chosenSet())

        datasets[name] = {"alnCollections":alnCollections,
                          "chosenSets":chosenSets,
                          "isd": curisd,
                          "counts":collections.Counter([x.choice for x in alnCollections])}
    

    # launch web view
    import web

    web.VARIANT = variant
    
    for name in datasets:
        tracks = getTracks(datasets[name]["chosenSets"], variant, name)
        web.TracksByDataset[name] = dict((allele, tracks[allele]) for allele in tracks)

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
        plotISDs = True
        for name in web.SAMPLES:
            isd = datasets[name]["isd"]
            plotISDs = plotISDs and InsertSizeProbabilities.plotInsertSizeDistribution(isd, name, datasets[name])
        if plotISDs:
            web.ISIZES = web.SAMPLES


    tc = TrackCompositor(1200)
    tc.addTracks("Alternate Allele", datasets.keys(), [web.TracksByDataset[name]["alt"] for name in datasets])
    tc.addTracks("Reference Allele", datasets.keys(), [web.TracksByDataset[name]["ref"] for name in datasets])
    to_export = tc.render()
    

    web.TEMPSVG = to_export

    if args.export:
        exportFormat = args.export.split(".")[-1]
        exportData = to_export
        if exportFormat != "png":
            exportData = export.convertSVG(exportData, exportFormat)
        outf = open(args.export, "w")
        outf.write(exportData)
        outf.close()

        if args.open_exported:
            launchFile(args.export)

    if not args.no_web:
        web.run()



if __name__ == '__main__':
    main()