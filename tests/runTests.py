import datetime
import json
import os
import pandas
import subprocess
import sys
import time
import traceback

from svviz import demo
from svviz import testIssues
from svviz import rendertest
from svviz import testDemos
from svviz import testCounts


# USAGE = """
# python runTests.py run|reset [hg19.ref.fa]

# run         - run all svviz tests
# reset       - removes then regenerates all values stored for each test;
#               use only after verifying that svviz behavior has changed
#               and that the new behavior is correct
# hg19.ref.fa - path to reference genome; must be defined here or using
#               the environmental variable SVVIZ_HG19_FASTA
# """


# reset ...

def reset():
    print "resetting test values..."

    previousSummaryPath = "countsTest.previousSummary.txt"
    os.remove(previousSummaryPath)

    raise Exception("not yet implemented: reset for demos and for render test")



# run ...


def _runTest(fn, description):
    print "\n\n -- running {} --\n\n".format(description)
    try:
        t0 = time.time()
        result = fn()
        t1 = time.time()
        result = [result[0], result[1], t1-t0]
    except Exception, e:
        print " ** error running {}: {} **".format(description, e)
        print traceback.print_exc()
        result = [False, str(e), -1]

    return result

def getHG19Ref(path=None):
    if path is not None:
        os.environ["SVVIZ_HG19_FASTA"] = path
        return path

    path = os.environ.get("SVVIZ_HG19_FASTA", None)
    assert os.path.exists(path), "Can't find hg19 reference fasta at path '{}'".format(path)

    return path

def getCountsData():
    path = "svviz-examples/countsTest"
    if not os.path.exists(path):
        result = demo.downloadDemo("countsTest")
        if not result:
            raise Exception("Couldn't download the countsTest data.")


def runTestCounts():
    getCountsData()

    genome = getHG19Ref()
    vcfs = ["svviz-examples/countsTest/na12878_test_deletions.vcf"]
    bams = ["svviz-examples/countsTest/reads.sorted.bam"]
    previousSummaryPath = "countsTest.previousSummary.txt"

    return testCounts.run(genome, vcfs, bams, previousSummaryPath)

def runTestIssues():
    genome = getHG19Ref()

    return testIssues.run(genome)

def saveTimingInfo(summary):
    timingsPath = "test_timings.csv"
    git_version = subprocess.check_output(["git", "describe"]).strip()
    
    new_row = summary[["timing"]].T
    new_row["date"] = [datetime.datetime.now()]
    new_row["version"] = git_version


    if os.path.exists(timingsPath):
        timings = pandas.read_csv(timingsPath, index_col=0)
        timings = pandas.concat([timings, new_row])
    else:
        timings = new_row

    timings.to_csv(timingsPath)

    print timings

        


def run(which):
    print "running all tests..."
    summary = pandas.DataFrame(columns=["pass", "info", "timing"])

    # Test chromosome ends
    if len(which)==0 or "chrom_ends" in which:
        summary.loc["chrom_ends"] = _runTest(runTestIssues, "issues")

    # Run the demos
    if len(which)==0 or "demos" in which:
        summary.loc["demos"] = _runTest(testDemos.run, "demos")

    # Run regression testing on ref/alt/amb counts
    if len(which)==0 or "counts" in which:
        summary.loc["counts"] = _runTest(runTestCounts, "counts")

    # Run the render regression tests
    if len(which)==0 or "rendering" in which:
        summary.loc["rendering"] = _runTest(rendertest.run, "rendering")    

    summary["timing"] = summary["timing"].apply(lambda x: "{}".format(datetime.timedelta(seconds=int(x))))
    print summary

    saveTimingInfo(summary)




def main():
    # don't ask me why I rolled my own regression testing code instead of using one of the 
    # gazillion existing frameworks...

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--reference", help="path for hg19 reference fasta; must be defined here or "
        "using the environmental variable SVVIZ_HG19_FASTA")

    parser.add_argument("mode", help="run|reset")
    parser.add_argument("which", nargs="*", help="which analyses to run (default all)")

    args = parser.parse_args()

    print args.which

    # if len(sys.argv) < 2:
    #     print USAGE
    #     return 

    if args.mode == "run":
        if getHG19Ref(args.reference) is None:
            parser.print_help()
            print "ERROR: Must provide path for hg19 reference fasta"
            sys.exit(1)
        run(args.which)
    elif args.mode == "reset":
        reset()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()