import logging
import pysam
import sys

from svviz import commandline
from svviz import disambiguate
from svviz import debug
from svviz import datahub
from svviz import export
from svviz import insertsizes
from svviz import remap
from svviz import track
from svviz import utilities
from svviz import variants
from svviz import web

def checkRequirements():
    if not remap.check_swalign():
        print "ERROR: check that svviz is correctly installed -- the 'ssw' Smith-Waterman alignment module does not appear to be functional"
        sys.exit(1)

def loadISDs(dataHub):
    """ Load the Insert Size Distributions """

    for sample in dataHub:
        sample.insertSizeDistribution = insertsizes.InsertSizeDistribution(sample.bam, saveReads=True)

    if dataHub.args.isize_mean is None or dataHub.args.isize_std is None:
        mean_isizes = [sample.insertSizeDistribution.mean() for sample in dataHub.samples.values()]
        std_isizes = [sample.insertSizeDistribution.std() for sample in dataHub.samples.values()]

        logging.debug(" calculated isize (mean, std): {}".format(zip(mean_isizes, std_isizes)))

        mean_isizes = [mean for mean in mean_isizes if mean is not None]
        std_isizes = [std for std in std_isizes if std is not None]

        if len(mean_isizes) > 0 and len(std_isizes) > 0:
            if dataHub.args.isize_mean is None:
                dataHub.args.isize_mean = max(mean_isizes)
                logging.info(" isize-mean not specified; using value {} inferred from input data".format(dataHub.args.isize_mean))
            if dataHub.args.isize_std is None:
                dataHub.args.isize_std = max(std_isizes)
                logging.info(" isize-std not specified; using value {} inferred from input data".format(dataHub.args.isize_std))
        else:
            raise Exception("Could not infer isize-mean from input files; make sure you have genome-wide read coverage in the input bams, or pass in the --isize-mean option on the command line")

def loadReads(dataHub):
    for sample in dataHub:
        logging.info(" - {}".format(sample.name))
        sample.reads = remap.getReads(dataHub.variant, sample.bam, dataHub.args.min_mapq, sample.searchDistance, sample.singleEnded)

## TODO: fix this: tempSetSampleParams()
def tempSetSampleParams(dataHub):
    for sample in dataHub:
        sample.searchDistance = dataHub.args.search_dist
        sample.singleEnded = dataHub.args.single_ended
        sample.minMapq = dataHub.args.min_mapq

        sample.orientations = dataHub.args.orientation
        if sample.singleEnded:
            sample.orientations = "any"

def runRemap(dataHub):
    for sample in dataHub:
        sample.alnCollections = remap.do_realign(dataHub.variant, sample.reads)

def runDisambiguation(dataHub):
    for sample in dataHub:
        disambiguate.batchDisambiguate(sample.alnCollections, sample.insertSizeDistribution, 
            sample.orientations, singleEnded=sample.singleEnded)

def renderSamples(dataHub):
    for sample in dataHub:
        ref_chrom = track.ChromosomePart(dataHub.variant.getRefSeq())
        ref_track = track.Track(ref_chrom, sample.chosenSets("ref"), 3000, 4000, 0, len(dataHub.variant.getRefSeq()), variant=dataHub.variant, allele="ref")
        sample.tracks["ref"] = ref_track

        alt_chrom = track.ChromosomePart(dataHub.variant.getAltSeq())
        alt_track = track.Track(alt_chrom, sample.chosenSets("alt"), 5000, 15000, 0, len(dataHub.variant.getAltSeq()), variant=dataHub.variant, allele="alt")
        sample.tracks["alt"] = alt_track

        amb_track = track.Track(ref_chrom, sample.chosenSets("amb"), 4000, 10000, 0, len(dataHub.variant.getRefSeq()), variant=dataHub.variant, allele="amb")
        sample.tracks["amb"] = amb_track

def renderAxesAndAnnotations(dataHub):
    for allele in ["alt", "ref"]:
        # TODO: store width somewhere better
        t = dataHub.samples.values()[0].tracks[allele]

        for name, annotationSet in dataHub.annotationSets.iteritems():
            dataHub.alleleTracks[allele][name] = track.AnnotationTrack(annotationSet, t.scale, dataHub.variant, allele)

        axis = track.Axis(t.scale, dataHub.variant, allele)
        dataHub.alleleTracks[allele]["axis"] = axis

def ensureExportData(dataHub):
    if dataHub.trackCompositor is None:
        dataHub.trackCompositor = export.TrackCompositor(dataHub)
        # TODO: make TrackCompositor take a DataHub object directly
        # dataHub.trackCompositor.addTracks("Alternate Allele", dataHub.samples.keys(), [sample.tracks["alt"] for sample in dataHub])
        # dataHub.trackCompositor.addTracks("Reference Allele", dataHub.samples.keys(), [sample.tracks["ref"] for sample in dataHub])


def runDirectExport(dataHub):
    if dataHub.args.export:
        logging.info("* Exporting views *")
        ensureExportData(dataHub)

        exportFormat = dataHub.args.export.split(".")[-1]
        exportData = dataHub.trackCompositor.render()
        if exportFormat != "svg":
            exportData = export.convertSVG(exportData, exportFormat)
        outf = open(dataHub.args.export, "w")
        outf.write(exportData)
        outf.close()

        if dataHub.args.open_exported:
            utilities.launchFile(dataHub.args.export)

def runWebView(dataHub):
    if not dataHub.args.no_web:
        ## TODO: only prepare export SVG when needed
        ensureExportData(dataHub)
        plotInsertSizeDistributions(dataHub)

        web.dataHub = dataHub
        web.run()

def plotInsertSizeDistributions(dataHub):
    if all(not sample.insertSizeDistribution.fail for sample in dataHub):
        plotISDs = True
        for name, sample in dataHub.samples.iteritems():
            isd = sample.insertSizeDistribution
            sample.insertSizePlot = insertsizes.plotInsertSizeDistribution(isd, name, dataHub)
            plotISDs = plotISDs and sample.insertSizePlot
        if not plotISDs:
            for sample in dataHub:
                sample.insertSizePlot = None


def saveReads(dataHub):
    if dataHub.args.save_reads:
        logging.info("* Saving relevant reads *")
        for i, sample in enumerate(dataHub):
            outbam_path = dataHub.args.save_reads
            if not outbam_path.endswith(".bam"):
                outbam_path += ".bam"

            if len(dataHub.samples) > 1:
                logging.debug("Using i = {}".format(i))
                outbam_path = outbam_path.replace(".bam", ".{}.bam".format(i))

            # print out just the reads we're interested for use later
            bam_small = pysam.Samfile(outbam_path, "wb", template=sample.bam)
            for read in sample.reads:
                bam_small.write(read)

            for read in sample.insertSizeDistribution.reads:
                bam_small.write(read)

            bam_small.close()
            sorted_path = outbam_path.replace(".bam", ".sorted")
            pysam.sort(outbam_path, sorted_path)
            pysam.index(sorted_path+".bam")

def main():
    checkRequirements()

    args = commandline.parseArgs()

    dataHub = datahub.DataHub()
    dataHub.setArgs(args)

    logging.info("* Sampling reads to calculate Insert Size Distributions *")
    loadISDs(dataHub)

    logging.info("* Loading variant *")
    dataHub.variant = variants.getVariant(dataHub)

    ## TODO: set parameters by sample separately
    logging.info("* TEMP: should set these parameters separately for each sample (tempSetSampleParams()) *")
    tempSetSampleParams(dataHub)

    logging.info("* Loading reads and finding mates *")
    loadReads(dataHub)
    saveReads(dataHub)

    logging.info("* Realigning reads *")
    runRemap(dataHub)

    logging.info("* Assigning reads to most probable alleles *")
    runDisambiguation(dataHub)


    logging.info("* Rendering tracks *")
    renderSamples(dataHub)
    renderAxesAndAnnotations(dataHub)

    runDirectExport(dataHub)

    runWebView(dataHub)

if __name__ == '__main__':
    main()

