import argparse
import logging
import sys

from svviz import demo
from svviz.alignment import AlignmentSet

def setDefault(args, key, default):
    if args.__dict__[key] is None:
        args.__dict__[key] = default

def checkDemoMode():
    inputArgs = sys.argv[1:]

    if len(inputArgs) < 1:
        return []
        
    if inputArgs[0] == "demo":
        which = "example1"
        if len(inputArgs) > 1:
            if inputArgs[1] in ["1","2"]:
                which = "example{}".format(inputArgs[1])
            else:
                raise Exception("Don't know how to load this example: {}".format(inputArgs[1]))
        cmd = demo.loadDemo(which)
        if cmd is not None:
            inputArgs = cmd
            logging.info("Running the following command:")
            logging.info("{} {}".format(sys.argv[0], " ".join(inputArgs)))
            logging.info("")
        else:
            raise Exception("couldn't load demo command from info.txt file.")

    return inputArgs

def parseArgs():
    inputArgs = checkDemoMode()

    parser = argparse.ArgumentParser(usage="%(prog)s [options] [demo] [ref breakpoint-info...]", epilog="For an example, run 'svviz demo'.")

    parser.add_argument("ref", help="reference fasta file (a .faidx index file will be "
        "created if it doesn't exist so you need write permissions for this directory)")
    parser.add_argument("breakpoints", nargs="*")

    requiredParams = parser.add_argument_group("required parameters")
    requiredParams.add_argument("-b", "--bam", action="append", help="sorted, indexed bam file containing reads of interest to plot; "
        "can be specified multiple times to load multiple samples")

    inputParams = parser.add_argument_group("input parameters")
    inputParams.add_argument("-t", "--type", help="event type: either del[etion], ins[ertion] or mei (mobile element insertion)")
    inputParams.add_argument("-S", "--single-ended", action="store_true", help="single-ended sequencing (default is paired-end)")
    inputParams.add_argument("-o", "--orientation", help="read orientation; probably want fr, rf or similar (only needed for paired-end data; default rf)")

    inputParams.add_argument("-A", "--annotations", action="append", help="bed file containing annotations to plot; will be compressed and indexed "
        "using samtools tabix in place if needed (can specify multiple annotations files)")

    inputParams.add_argument("-m", "--isize-mean", metavar="MEAN", type=float, help="mean insert size; used to determine concordant read pairs (paired-end)"
        "and the size of the flanking region to align against around breakpoints (default: inferred from input bam)")
    inputParams.add_argument("-s", "--isize-std", metavar="STD", type=float, help="stdev of the insert size (default: inferred from input bam)")
    inputParams.add_argument("-d", "--search-dist", metavar="DISTANCE", type=int, help="distance in base-pairs from the breakpoints to search for reads; "
        "default: 2x the isize-mean (paired end) or 1000 (single-end)")

    inputParams.add_argument("-q", "--min-mapq", metavar="MAPQ", type=float, help="minimum mapping quality for reads")
    inputParams.add_argument("-a", "--aln-quality", metavar="QUALITY", type=float, 
        help="minimum score of the Smith-Waterman alignment against the ref or alt allele in order to be considered (multiplied by 2)")
    inputParams.add_argument("--include-supplementary", action="store_true", help="include supplementary alignments "
        "(ie, those with the 0x800 bit set in the bam flags); default: false")

    interfaceParams = parser.add_argument_group("interface parameters")
    interfaceParams.add_argument("--no-web", action="store_true", help="don't show the web interface")
    interfaceParams.add_argument("--save-reads", metavar="OUT_BAM_PATH", help="save relevant reads to this file (bam)")
    inputParams.add_argument("-e", "--export", metavar="EXPORT", type=str, help="export view to file; exported file format is determined "
        "from the filename extension (automatically sets --no-web)")
    inputParams.add_argument("-O", "--open-exported", action="store_true", help="automatically open the exported file (OS X only)")

    defaults = parser.add_argument_group("presets")
    defaults.add_argument("--mate-pair", action="store_true", help="sets defaults for ~6.5kb insert mate pair libraries")
    defaults.add_argument("--pacbio", action="store_true", help="sets defaults for pacbio libraries")
    defaults.add_argument("--moleculo", action="store_true", help="sets defaults for moleculo libraries")

    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)
        
    args = parser.parse_args(inputArgs)

    # Presets
    if args.mate_pair:
        args.orientation = "-+"
        args.isize_mean = 6500
        args.isize_std = 1100
    elif args.pacbio:
        args.single_ended = True
        setDefault(args, "aln_quality", 0.65)
        setDefault(args, "isize_mean", 10000)
        setDefault(args, "isize_std", 200000)
    elif args.moleculo:
        args.single_ended = True
        setDefault(args, "aln_quality", 0.85)
        setDefault(args, "isize_mean", 20000)
        setDefault(args, "isize_std", 200000)


    if args.single_ended:
        setDefault(args, "search_dist", 1000)
        setDefault(args, "orientation", "any")
    elif args.orientation is not None:
        args.orientation = args.orientation.replace("r", "-").replace("f", "+")
        args.orientation = args.orientation.split(",")

    if args.aln_quality is not None:
        AlignmentSet.AlnThreshold = args.aln_quality
    
    if args.export is not None:
        args.no_web = True
        if not args.export.lower()[-3:] in ["svg", "png", "pdf"]:
            print "Export filename must end with one of .svg, .png or .pdf"
            sys.exit(1)

    logging.info(str(args))
    return args

if __name__ == '__main__':
    print parseArgs()