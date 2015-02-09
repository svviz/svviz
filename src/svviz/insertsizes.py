import collections
import logging
import os
import tempfile
import time
import numpy

from svviz.utilities import mean, stddev
from svviz.kde import gaussian_kde

def removeOutliers(data, m = 10.):
    """ a method of trimming outliers from a list/array using 
    outlier-safe methods of calculating the center and variance;
    only removes the upper tail, not the lower tail """
    data = numpy.array(data)
    d_abs = numpy.abs(data - numpy.median(data))
    d = data - numpy.median(data)
    mdev = numpy.median(d_abs)
    s = d/mdev if mdev else 0.
    return data[s<m]

def chooseOrientation(orientations):
    logging.info("  counts +/-:{:<6} -/+:{:<6} +/+:{:<6} -/-:{:<6} unpaired:{:<6}".format(orientations[False, True], 
                                                    orientations[True, False], 
                                                    orientations[True, True],
                                                    orientations[False, False],
                                                    orientations["unpaired"]))
    ranked = sorted(orientations, key=lambda x: orientations[x])
    chosenOrientations = [ranked.pop()]
    while len(ranked) > 0:
        candidate = ranked.pop()
        if orientations[chosenOrientations[-1]] < 2* orientations[candidate]:
            chosenOrientations.append(candidate)
        else:
            break
    if chosenOrientations[0] == "unpaired":
        chosenOrientations = "any"
    else:
        d = {False: "+", True:"-"}
        chosenOrientations = ["".join(d[x] for x in o) for o in chosenOrientations]
    return chosenOrientations

def sampleInsertSizes(bam, maxreads=50000, skip=0, minmapq=40, maxExpectedSize=20000, keepReads=False):
    """ get the insert size distribution, cutting off the tail at the high end, 
    and removing most oddly mapping pairs

    50,000 reads seems to be sufficient to get a nice distribution, and higher values
        don't tend to change the distribution much """

    inserts = []
    readLengths  = []
    
    # TODO: should create a more complete list of searchable regions, for general use over smaller genomes

    count = 0
    start = 2500000
    end = 50000000

    reads = []
    # get the chromosomes and move X, Y, M/MT to the end
    chromosomes = []
    for i in range(bam.nreferences):
        if bam.lengths[i] > start:
            chromosomes.append(bam.getrname(i))

    orientations = collections.Counter()
    NMs = []
    INDELs = []

    for chrom in sorted(chromosomes):
        for read in bam.fetch(chrom, start, end):
            if skip > 0:
                skip -= 1
                continue

            try:
                NMs.append(read.opt("NM")/float(len(read.seq)))
            except KeyError:
                pass

            try:
                INDELs.append(sum(1 for i in zip(*read.cigartuples)[1] if i in[1,2])/float(len(read.seq)))
            except TypeError:
                pass

            if orientations["unpaired"] > 2500 and count < 1000:
                # bail out early if it looks like it's single-ended
                break

            if not read.is_paired:
                orientations["unpaired"] += 1
                readLengths.append(len(read.seq))
                continue
                
            if not read.is_read1:
                continue
            
            if not read.is_proper_pair:
                continue
            if read.is_unmapped or read.mate_is_unmapped:
                continue
            if read.tid != read.rnext:
                continue
            if read.mapq < minmapq:
                continue
            
            # if abs(read.isize) < 20000:
            inserts.append(abs(read.isize))

            curOrient = (read.is_reverse, read.mate_is_reverse)
            if read.reference_start > read.next_reference_start:
                curOrient = not curOrient[0], not curOrient[1]
            orientations[curOrient] += 1
            readLengths.append(len(read.seq))

            if keepReads:
                reads.append(read)

            count += 1
            if count > maxreads:
                break
        if count > maxreads:
            break

    print "NM:", mean(NMs), stddev(NMs)
    print "INDELs:", mean(INDELs), stddev(INDELs)

    chosenOrientations = chooseOrientation(orientations)

    return removeOutliers(inserts), reads, chosenOrientations, numpy.array(readLengths)


class ReadStatistics(object):
    def __init__(self, bam, keepReads=False):
        self.insertSizes = []
        self.readLengths = []
        self.orientations = []
        self._insertSizeKDE = None
        self.singleEnded = False

        self._insertSizeScores = {} # cache

        try:
            self.insertSizes, self.reads, self.orientations, self.readLengths = sampleInsertSizes(bam, keepReads=keepReads)
        except ValueError:
            print "*"*100, "here"

    def hasInsertSizeDistribution(self):
        if len(self.insertSizes) > 1000:
            return True
        return False

    def meanInsertSize(self):
        if self.hasInsertSizeDistribution():
            return mean(self.insertSizes)
        return None

    def stddevInsertSize(self):
        if self.hasInsertSizeDistribution():
            return stddev(self.insertSizes)
        return None

    # def insertSizeKDE(self):
    #     if self.hasInsertSizeDistribution() and self._insertSizeKDE is None:
    #         self._insertSizeKDE = gaussian_kde(self.insertSizes)
    #     return self._insertSizeKDE

    def scoreInsertSize(self, isize):
        if not self.hasInsertSizeDistribution():
            return 0

        if self._insertSizeKDE is None:
            self._insertSizeKDE = gaussian_kde(self.insertSizes)
        # the gaussian kde call is pretty slow with ~50,000 data points in it, so we'll cache the result for a bit of a speed-up
        isize = abs(isize)
        if not isize in self._insertSizeScores:
            self._insertSizeScores[isize] = self._insertSizeKDE(isize)

        return self._insertSizeScores[isize]


    def hasReadLengthDistribution(self):
        if len(self.readLengths) > 1000:
            return True
        return False

    def meanReadLength(self):
        if self.hasReadLengthDistribution():
            return mean(self.readLengths)
        return None

    def stddevReadLength(self):
        if self.hasReadLengthDistribution():
            return stddev(self.readLengths)
        return None

    def readLengthUpperQuantile(self):
        if self.hasReadLengthDistribution():
            return numpy.percentile(self.readLengths, 99)
        return None




# class InsertSizeDistribution(object):

#     """ Use this class to calculate the distribution of insert sizes from a bam;
#     then score new read pairs for the likelihood that the insert size came from this distribution """

#     def __init__(self, bam, saveReads=False):
#         """ bam must be a sorted, indexed pysam.Samfile """

#         self._totalTime = 0
#         self._totalIterations = 0

#         try:
#             self.isizes, self.reads, self.orientations, self.readLengths = sampleInsertSizes(bam, saveReads=saveReads)
#         except ValueError:
#             self.isizes = []
#             self.readLengths = []
#             self.reads = []
#             self.orientations = []
        
#         if len(self.isizes) < 1000:
#             self.fail = True
#             # self.min = 0
#             return

#         if gaussian_kde is None:
#             # self.min = 0
#             self.fail = True
#             return

#         self.fail = False
#         self.kde = gaussian_kde(self.isizes)

#         self._cache = {}
#         # self.min = numpy.min(self.kde(numpy.linspace(0, max(self.isizes), 100)))
#         # print "Min score:", self.min

#     def mean(self):
#         if len(self.isizes) >= 1000:
#              return mean(self.isizes)
#         return None

#     def std(self):
#         if len(self.isizes) >= 1000:
#              return stddev(self.isizes)
#         return None

#     def score(self, isize):
#         if self.fail:
#             return 0

#         # the gaussian kde call is pretty slow with ~50,000 data points in it, so we'll cache the result for a bit of a speed-up
#         isize = abs(isize)
#         if not isize in self._cache:
#             self._cache[isize] = self.kde(isize)

#         return self._cache[isize]

#         # we don't ever want a 0 probability
#         # return max(score, self.min)


def plotInsertSizeDistribution(isd, sampleName, dataHub):
    try:
        from biorpy import r, plotting
        d = tempfile.mkdtemp()
        filename = os.path.join(d, sampleName)

        if not filename.endswith(".svg"):
            filename += ".svg"

        r.svg(filename)

        alleles = ["alt", "ref", "amb"]
        others = [[len(chosenSet) for chosenSet in dataHub.samples[sampleName].chosenSets(allele)] for allele in alleles]
        plotting.ecdf([isd.insertSizes]+others,
            ["average"]+alleles, xlab="Insert size (bp)", main=sampleName)
        
        # x = numpy.arange(0, max(isd.isizes), max(isd.isizes)/250)
        # r.plot(x, isd.kde(x), col="black", xlab="Insert Size (bp)", ylab="Number of reads", main=name, type="l")

        # for color, name in zip(["red", "green", "lightblue"], ["altalns", "refalns", "ambalns"]):
        #     h = numpy.histogram([len(alnset) for alnset in dataset[name]])
        #     x = h[1]
        #     y = numpy.concatenate([[0], h[0]])/h[0].astype("float").sum()
        #     r.lines(x, y, col=color, type="S")

        #     print name
        #     print x, y
        r.devoff()

        data = open(filename).read()
        return data
    except ImportError:
        return None    


if __name__ == '__main__':
    import pysam
    from biorpy import r
    import time

    bam = pysam.Samfile("/Volumes/frida/nspies/working/Q001_MP_IVF1.paired_bwamem.sorted.bam", "rb")

    t0 = time.time()
    isd = InsertSizeDistribution(bam)
    t1 = time.time()

    print "loading time:", t1-t0

    x = numpy.linspace(0, 15000, 250)
    y = isd.kde(x)

    r.plot(x, y, type="l")
    r.abline(h=isd.min)

    more_reads = bam.fetch("chr2", 2500000, 5000000)
    for i in range(50):
        nextread = more_reads.next()
        x = abs(nextread.isize)
        y = isd.kde(x)

        print x, y
        r.points(x, y, col="red")

    t0 = time.time()
    for i in range(1000):
        isd.score(55)
    t1 = time.time()

    print "time to score 1000:", t1-t0

    raw_input()
