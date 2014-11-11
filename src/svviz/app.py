import pyfaidx
import pysam
import time

import CommandLine
import StructuralVariants
from remap import do_realign, disambiguate
import track
from utilities import Locus, reverseComp
import misc


def savereads(args, bam, reads):
    if args.save_reads:
        outbam_path = args.save_reads
        if not outbam_path.endswith(".bam"):
            outbam_path += ".bam"

        # print out just the reads we're interested for use later
        bam_small = pysam.Samfile(outbam_path, "wb", template=bam)
        for read in reads:
            bam_small.write(read)


def getVariant(args, genome):
    extraSpace = int(args.isize_mean) * 2

    if args.type.lower().startswith("del"):
        if args.deldemo:
            chrom, start, end = "chr1", 72766323, 72811840
        else:
            assert len(args.breakpoints) == 3, "Format for deletion breakpoints is [chrom, start, end]"
            chrom = args.breakpoints[0]
            start = int(args.breakpoints[1])
            end = int(args.breakpoints[2])
        if args.min_mapq is None:
            args.min_mapq = 30

        variant = StructuralVariants.Deletion.from_breakpoints(chrom, start-1, end-1, extraSpace, genome)
    elif args.type.lower().startswith("ins"):
        if args.insdemo:
            chrom, pos, seq = "chr3", 20090540, misc.L1SEQ
            print "here"
        else:
            assert len(args.breakpoints) == 3, "Format for insertion breakpoints is [chrom, pos, seq]"
            chrom = args.breakpoints[0]
            pos = int(args.breakpoints[1])
            seq = int(args.breakpoints[2])
        if args.min_mapq is None:
            args.min_mapq = -1

        print chrom, pos, seq
        variant = StructuralVariants.Insertion(Locus(chrom, pos, pos, "+"), reverseComp(seq), extraSpace, genome)
        print variant.searchRegions()
    else:
        raise Exception("only accept event types of deletion or insertion")

    return variant

def getTracks(selectedAltAlignments, selectedRefAlignments, selectedAmbiguousAlignments, variant):
    print "Ref:", len(selectedRefAlignments), "Alt:", len(selectedAltAlignments), "Amb:", len(selectedAmbiguousAlignments)


    c = track.ChromosomePart(variant.getRefSeq())
    t = track.Track(c, selectedRefAlignments, 3000, 4000, 0, len(variant.getRefSeq()), vlines=variant.getRefRelativeBreakpoints())
    # t = track.Track(c, selectedRefAlignments, 3000, 2500, 0, len(refseq), vlines=[8000+extraSpace, end-start+extraSpace])#, 4000, 7000+end-start)
    out = open("ref.svg", "w")
    out.write(t.render())


    c = track.ChromosomePart(variant.getAltSeq())
    t = track.Track(c, selectedAltAlignments, 5000, 15000, 0, len(variant.getAltSeq()), vlines=variant.getAltRelativeBreakpoints())

    # t = track.Track(c, selectedAltAlignments, 1000, 2500, 0, len(altseq), vlines=[8000+extraSpace])#, 8000, 8000+end-start)
    t0 = time.time()
    out = open("alt.svg", "w")
    out.write(t.render())
    t1 = time.time()

    print "time rendering alt:", t1-t0

    c = track.ChromosomePart(variant.getRefSeq())
    t = track.Track(c, selectedAmbiguousAlignments, 4000, 10000, 0, len(variant.getRefSeq()), vlines=variant.getRefRelativeBreakpoints())
    # t = track.Track(c, selectedAmbiguousAlignments, 1000, 2500, 0, len(refseq), vlines=[8000+extraSpace, end-start+extraSpace])#, 4000, 7000+end-start)
    out = open("amb.svg", "w")
    out.write(t.render())

    return {"AltCount":len(selectedAltAlignments),
            "RefCount":len(selectedRefAlignments),
            "AmbCount":len(selectedAmbiguousAlignments)}, selectedRefAlignments, selectedAltAlignments, selectedAmbiguousAlignments


def main():

    args = CommandLine.parseArgs()

    genome = pyfaidx.Fasta(args.ref, as_raw=True)
    bam = pysam.Samfile(args.bam, "rb")
    variant = getVariant(args, genome)
    print args

    refalignments, altalignments, reads = do_realign(variant, bam, args.min_mapq)
    altAlignments, refAlignments, ambiguousAlignments = disambiguate(refalignments, altalignments, 
        args.isize_mean, 2*args.isize_std, args.orientation)

    results, refalns, altalns, ambalns = getTracks(altAlignments, refAlignments, ambiguousAlignments, variant)

    if True:
        # launch web view
        import web
        web.RESULTS = results
        web.READ_INFO = {}

        for readset in refalns + altalns + ambalns:
            web.READ_INFO[readset.getAlignments()[0].name] = readset

        web.run()


if __name__ == '__main__':
    main()