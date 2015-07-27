import logging
import os
import pysam
import sys

from svviz import commandline
from svviz import disambiguate
from svviz import debug
from svviz import datahub
from svviz import dotplots
from svviz import export
from svviz import flanking
from svviz import insertsizes
from svviz import remap
from svviz import summarystats
from svviz import track
from svviz import utilities
from svviz import variants
from svviz import vcf
from svviz import web

def checkRequirements(args):
    if not remap.check_swalign():
        print "ERROR: check that svviz is correctly installed -- the 'ssw' Smith-Waterman alignment module does not appear to be functional"
        sys.exit(1)
    if args.export and (args.export.lower().endswith("pdf") or args.export.lower().endswith("png")):
        if not export.canConvertSVGToPDF():
            print "ERROR: librsvg needs to be installed in order to export to pdf and png format."
            sys.exit(1)

def loadISDs(dataHub):
    """ Load the Insert Size Distributions """

    for sample in dataHub:
        logging.info(" > {} <".format(sample.name))
        sample.readStatistics = insertsizes.ReadStatistics(sample.bam, keepReads=dataHub.args.save_reads)

        if sample.readStatistics.orientations != "any":
            if len(sample.readStatistics.orientations) > 1:
                logging.warn("  ! multiple read pair orientations found within factor !\n"
                             "  ! of 2x of one another; if you aren't expecting your  !\n"
                             "  ! input data to contain multiple orientations, this   !\n"
                             "  ! could be a bug in the mapping software or svviz     !")
            if len(sample.readStatistics.orientations) < 1:
                logging.error("  No valid read orientations found for dataset:{}".format(sample.name))


        sample.orientations = sample.readStatistics.orientations
        if sample.orientations == "any":
            sample.singleEnded = True
        logging.info("  valid orientations: {}".format(",".join(sample.orientations) if sample.orientations!="any" else "any"))

        if sample.orientations == "any":
            searchDist = sample.readStatistics.readLengthUpperQuantile()
            alignDist = sample.readStatistics.readLengthUpperQuantile()*1.25 + dataHub.args.context
        else:
            searchDist = sample.readStatistics.meanInsertSize()+sample.readStatistics.stddevInsertSize()*2
            alignDist = sample.readStatistics.meanInsertSize()+sample.readStatistics.stddevInsertSize()*4 + dataHub.args.context
        if dataHub.args.flanks:
            searchDist += dataHub.args.context

        sample.searchDistance = int(searchDist)
        dataHub.alignDistance = max(dataHub.alignDistance, int(alignDist))

        logging.info("  Using search distance: {}".format(sample.searchDistance))

    logging.info(" Using align distance: {}".format(dataHub.alignDistance))


def loadReads(dataHub):
    readCount = 0
    for sample in dataHub:
        logging.info(" - {}".format(sample.name))
        sample.reads = remap.getReads(dataHub.variant, sample.bam, dataHub.args.min_mapq, dataHub.args.pair_min_mapq,
            sample.searchDistance, sample.singleEnded, dataHub.args.include_supplementary)
        readCount += len(sample.reads)

    return readCount

def setSampleParams(dataHub):
    for sample in dataHub:
        sample.minMapq = dataHub.args.min_mapq

        if sample.singleEnded:
            sample.orientations = "any"

def runRemap(dataHub):
    for sample in dataHub:
        sample.alnCollections = remap.do_realign(dataHub.variant, sample.reads, dataHub.args.processes)

def runDisambiguation(dataHub):
    flankingRegionCollection = flanking.FlankingRegionCollection(dataHub.variant)
    for sample in dataHub:
        disambiguate.batchDisambiguate(sample.alnCollections, sample.readStatistics, sample.orientations, 
            singleEnded=sample.singleEnded, flankingRegionCollection=flankingRegionCollection,
            maxMultimappingSimilarity=dataHub.args.max_multimapping_similarity)

    return disambiguate.checkMultimapping(dataHub)

def renderSamples(dataHub):
    for sample in dataHub:
        flankingReads = {"ref":[], "alt":[]}
        if dataHub.args.flanks:
            flankingReads["ref"] = [alnCollection.sets["ref"] for alnCollection in sample.alnCollections if alnCollection.why=="flanking"]
            flankingReads["alt"] = [alnCollection.sets["alt"] for alnCollection in sample.alnCollections if alnCollection.why=="flanking"]

        ref_track = track.Track(dataHub.variant.chromParts("ref"), sample.chosenSets("ref")+flankingReads["ref"], 3000, 4000, 
            variant=dataHub.variant, allele="ref", thickerLines=dataHub.args.thicker_lines, colorCigar=(not dataHub.args.skip_cigar))
        sample.tracks["ref"] = ref_track

        alt_track = track.Track(dataHub.variant.chromParts("alt"), sample.chosenSets("alt")+flankingReads["alt"], 5000, 15000, 
            variant=dataHub.variant, allele="alt", thickerLines=dataHub.args.thicker_lines, colorCigar=(not dataHub.args.skip_cigar))
        sample.tracks["alt"] = alt_track

        amb_track = track.Track(dataHub.variant.chromParts("ref"), sample.chosenSets("amb"), 4000, 10000,
            variant=dataHub.variant, allele="amb", thickerLines=dataHub.args.thicker_lines, colorCigar=(not dataHub.args.skip_cigar))
        sample.tracks["amb"] = amb_track

def renderAxesAndAnnotations(dataHub):
    for allele in ["alt", "ref", "amb"]:
        # TODO: store width somewhere better
        t = dataHub.samples.values()[0].tracks[allele]

        for name, annotationSet in dataHub.annotationSets.iteritems():
            dataHub.alleleTracks[allele][name] = track.AnnotationTrack(annotationSet, t.scale, dataHub.variant, allele)

        axis = track.Axis(t.scale, dataHub.variant, allele)
        dataHub.alleleTracks[allele]["axis"] = axis

def ensureExportData(dataHub):
    if dataHub.trackCompositor is None:
        dataHub.trackCompositor = export.TrackCompositor(dataHub)

def runDirectExport(dataHub):
    if dataHub.args.export:
        logging.info("* Exporting views *")
        ensureExportData(dataHub)

        if dataHub.args.type == "batch" or dataHub.args.format is not None:
            exportFormat = dataHub.args.format
            if exportFormat is None:
                exportFormat = "pdf"
            if not os.path.exists(dataHub.args.export):
                os.makedirs(dataHub.args.export)

            path = os.path.join(dataHub.args.export, "{}.{}".format(dataHub.variant.shortName(), exportFormat))
        else:
            exportFormat = dataHub.args.export.split(".")[-1]
            path = dataHub.args.export

        exportData = dataHub.trackCompositor.render()
        if exportFormat.lower() != "svg":
            exportData = export.convertSVG(exportData, exportFormat)
        outf = open(path, "w")
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
        web.run(dataHub.args.port)

def plotInsertSizeDistributions(dataHub):
    # TODO: show only for samples with insert size distributions (ie paired end)
    if all(sample.readStatistics.hasInsertSizeDistribution() for sample in dataHub):
        plotISDs = True
        for name, sample in dataHub.samples.iteritems():
            isd = sample.readStatistics
            sample.insertSizePlot = insertsizes.plotInsertSizeDistribution(isd, name, dataHub)
            plotISDs = plotISDs and sample.insertSizePlot
        if not plotISDs:
            for sample in dataHub:
                sample.insertSizePlot = None

def generateDotplots(dataHub):
    if dataHub.args.dotplots:
        logging.info(" * Generating dotplots *")
        if len(dataHub.variant.chromParts("ref")) > 1:
            logging.warning("  --> currently don't support producing dotplots with multi-part variants")
            return

        dotplotPngData = dotplots.dotplot(dataHub)
        if dotplotPngData is not None:
            dataHub.dotplots["ref vs ref"] = dotplotPngData

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

            for read in sample.readStatistics.reads:
                bam_small.write(read)

            bam_small.close()
            sorted_path = outbam_path.replace(".bam", ".sorted")
            pysam.sort(outbam_path, sorted_path)
            pysam.index(sorted_path+".bam")

def saveState(dataHub):
    import cPickle as pickle

    pickle.dump(dataHub, open(dataHub.args.save_state, "w"))
    logging.warn("^"*20 + " saving state to pickle and exiting " + "^"*20)

def run(args):
    # entry point from python
    args = commandline.parseArgs(args)
    checkRequirements(args)

    dataHub = datahub.DataHub()
    dataHub.setArgs(args)

    logging.info("* Sampling reads to calculate Insert Size Distributions *")
    loadISDs(dataHub)

    if args.type == "batch":
        logging.info("* Loading variants from input VCF file *")
        dataHub.args.no_web = True
        svs = vcf.getVariants(dataHub)

        logging.info(" Loaded {} variants".format(len(svs)))
    else:
        logging.info("* Loading variant *")
        svs = [variants.getVariant(dataHub)]

    summaryStats = summarystats.Summary()
    skipped = 0
    for i, variant in enumerate(svs):
        logging.info("* Running for variant {}/{} {} *".format(i+1, len(svs), variant))
        dataHub.reset()

        dataHub.variant = variant
        setSampleParams(dataHub)

        debug.printDebugInfo(dataHub)

        logging.info("* Loading reads and finding mates *")
        readCount = loadReads(dataHub)
        saveReads(dataHub)

        if dataHub.args.max_reads and readCount > dataHub.args.max_reads:
            logging.info("+++ Skipping variant -- number of reads ({}) exceeds threshold set by user ({})".format(
                readCount, dataHub.args.max_reads))
            skipped += 1
            continue

        logging.info("* Realigning reads *")
        runRemap(dataHub)

        logging.info("* Assigning reads to most probable alleles *")
        runDisambiguation(dataHub)

        if not dataHub.args.no_web or dataHub.args.export:
            logging.info("* Rendering tracks *")
            renderSamples(dataHub)
            renderAxesAndAnnotations(dataHub)
        generateDotplots(dataHub)

        runDirectExport(dataHub)

        summaryStats.addVariantResults(dataHub)

    summaryStats.display()
    if dataHub.args.summary is not None:
        summaryStats.saveToPath(dataHub.args.summary)

    if skipped > 0:
        logging.info("\n\nSkipped {} variants because they exceeded the --max-reads threshold\n\n".format(skipped))
    if dataHub.args.save_state is not None:
        saveState(dataHub)
        return

    runWebView(dataHub)
    
def main():
    # entry point for shell script
    run(sys.argv)

if __name__ == '__main__':
    main()

