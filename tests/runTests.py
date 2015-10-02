import datetime
import os
import pandas
import sys
import time

from svviz import demo
from svviz import rendertest
from svviz import test
from svviz import testCounts


USAGE = """
python runTests.py run|reset [hg19.ref.fa]

run         - run all svviz tests
reset       - removes then regenerates all values stored for each test;
              use only after verifying that svviz behavior has changed
              and that the new behavior is correct
hg19.ref.fa - path to reference genome; must be defined here or using
              the environmental variable SVVIZ_HG19_FASTA
"""


# reset ...

def reset():
    print "resetting test values..."

    raise Exception("not yet implemented...")



# run ...


def _runTest(fn, description):
    print "\n\n -- running {} --\n\n".format(description)
    try:
        t0 = time.time()
        fn()
        t1 = time.time()
        result = [True, "", t1-t0]
    except Exception, e:
        print " ** error running {}: {} **".format(description, e)
        result = [False, str(e), -1]

    return result

def getHG19Ref():
    path = os.environ.get("SVVIZ_HG19_FASTA", None)
    if path is None:
        if len(sys.argv) < 3:
            return None
        path = sys.argv[2]
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

    testCounts.run(genome, vcfs, bams, previousSummaryPath)


def run():
    print "running all tests..."
    summary = pandas.DataFrame(columns=["pass", "info", "timing"])


    # # Run the demos
    # summary.loc["demos"] = _runTest(test.run, "demos")

    # # Run regression testing on ref/alt/amb counts
    # summary.loc["counts"] = _runTest(runTestCounts, "counts")

    # Run the render regression tests
    summary.loc["rendering"] = _runTest(rendertest.run, "rendering")
    


    summary["timing"] = summary["timing"].apply(lambda x: "{}".format(datetime.timedelta(seconds=int(x))))
    print summary


def main():
    if len(sys.argv) < 2:
        print USAGE
        return 

    if sys.argv[1] == "run":
        if getHG19Ref() is None:
            print USAGE
            print "ERROR: Must provide path for hg19 reference fasta"
            sys.exit(1)
        run()
    elif sys.argv[1] == "reset":
        reset()
    else:
        print USAGE
if __name__ == '__main__':
    main()