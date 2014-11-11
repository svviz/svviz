import argparse

def parseArgs():
    parser = argparse.ArgumentParser()

    parser.add_argument("-t", "--type", help="event type: either del[etion] or ins[ertion]")
    parser.add_argument("-o", "--orientation", help="read orientation; probably want +-, -+ or similar")
    parser.add_argument("-m", "--isize-mean", type=float, help="mean insert size")
    parser.add_argument("-s", "--isize-std", type=float, help="stdev of the insert size")

    parser.add_argument("-q", "--min-mapq", type=float, help="minimum mapping quality for reads")

    parser.add_argument("--save-reads", help="save relevant reads to this file (bam)")

    defaults = parser.add_mutually_exclusive_group()
    defaults.add_argument("--mate-pair", action="store_true", help="sets defaults for ~6.5kb insert mate pair libraries")
    defaults.add_argument("--paired300", action="store_true", help="sets defaults for ~300 bp insert short fragment paired end libraries")
    defaults.add_argument("--deldemo", action="store_true", help="")
    defaults.add_argument("--insdemo", action="store_true", help="")

    parser.add_argument("ref", help="reference fasta file (a .faidx index file will be "
        "created if it doesn't exist so you need write permissions for this directory)")
    parser.add_argument("bam", help="sorted, indexed bam file containing reads of interest to plot")
    parser.add_argument("breakpoints", nargs="*")

    args = parser.parse_args()

    if args.mate_pair or args.deldemo or args.insdemo:
        args.orientation = "-+"
        args.isize_mean = 6500
        args.isize_std = 1100
    elif args.paired300:
        args.orientation = "+-"
        args.isize_mean = 300
        args.isize_std = 25

    if args.deldemo:
        args.type = "del"
    if args.insdemo:
        args.type = "ins"
        
    return args

if __name__ == '__main__':
    print parseArgs()