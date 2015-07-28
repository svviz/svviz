import os
import pandas
import sys
import time

from svviz import app
from svviz import utilities

class MockArgs(object):
    def __getattr__(self, attr):
        return None

timings = {}

vcfs = [
    "/Users/nspies/Projects/svviz/tests/na12878_test_deletions.vcf",
    ]
bams = ["/Volumes/frida/nspies/NA12878/NA12878.mapped.ILLUMINA.bwa.CEU.high_coverage_pcr_free.20130906.bam"]
genome = "/Volumes/frida/nspies/data/hs37d5.fa"
summaryPath = "/Users/nspies/Projects/svviz/tests/newTestSummary.{}.txt"

summaries = pandas.DataFrame()

for vcf in vcfs:
    name = os.path.basename(vcf)
    print ">", name, "<"

    curSummaryPath = summaryPath.format(name)

    args = []
    args.append("test_script")
    args.append("-t batch")
    args.append("--summary {}".format(curSummaryPath))
    args.append(" ".join("-b {}".format(bam) for bam in bams))
    args.append(genome)
    args.append(vcf)

    args = " ".join(args).split()

    print args
    t0 = time.time()
    app.run(args)
    t1 = time.time()

    timings[name] = t1-t0

    curSummary = pandas.read_table(curSummaryPath)
    summaries = pandas.concat([curSummary, summaries])

previousSummaryPath = "/Users/nspies/Projects/svviz/tests/previousSummary.tsv"

if not os.path.exists(previousSummaryPath) or "-f" in sys.argv:
    print "="*30, "SAVING", "="*30
    summaries.to_csv(previousSummaryPath, sep="\t")
    print summaries
else:
    print "="*30, "COMAPRING", "="*30
    previousSummary = pandas.read_table(previousSummaryPath, index_col=0)

    combined = pandas.merge(previousSummary, summaries, how="outer", 
                            on=["variant", "sample","allele","key"],
                            suffixes=["_prev", "_new"])
    combined = combined.set_index(["variant", "sample","allele","key"])#.fillna(0)

    combined["diff"] = combined["value_new"] - combined["value_prev"]
    diff = combined.loc[combined["diff"]!=0, "diff"]

    if diff.shape[0] == 0:
        print "--- same as previous run ---"
    else:
        print combined.loc[diff.index]