try:
    import numpy
    from scipy.stats import gaussian_kde
except ImportError:
    numpy = None
    gaussian_kde = None

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

def sampleInsertSizes(bam, maxreads=50000, skip=0, minmapq=40, maxExpectedSize=20000):
    """ get the insert size distribution, cutting off the tail at the high end, 
    and removing most oddly mapping pairs

    50,000 reads seems to be sufficient to get a nice distribution, and higher values
        don't tend to change the distribution much """

    inserts = []
    
    count = 0

    # this is a fairly innocuous region on chr1
    for read in bam.fetch("chr1", 2500000, 50000000):
        if skip > 0:
            skip -= 1
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

        count += 1
        if count > maxreads:
            break

    return removeOutliers(inserts)



class InsertSizeDistribution(object):
    """ Use this class to calculate the distribution of insert sizes from a bam;
    then score new read pairs for the likelihood that the insert size came from this distribution """

    def __init__(self, bam):
        """ bam must be a sorted, indexed pysam.Samfile """
        if gaussian_kde is None:
            self.min = 0
            self.fail = True
            return

        try:
            self.isizes = sampleInsertSizes(bam)
        except ValueError:
            self.isizes = []
            
        if len(self.isizes) < 10:
            self.fail = True
            self.min = 0
            return
        self.fail = False
        self.kde = gaussian_kde(self.isizes)
        self.min = numpy.min(self.kde(numpy.linspace(0, max(self.isizes), 100)))
        print "Min score:", self.min

    def score(self, isize):
        # we don't ever want a 0 probability
        if self.fail:
            return 0
        score = self.kde(abs(isize))
        return max(score, self.min)


def plotInsertSizeDistribution(isd, name, dataset):
    try:
        from biorpy import r, plotting
        filename = name
        if not filename.endswith(".svg"):
            filename += ".svg"
        r.svg(filename)

        alnsetNames = ["altalns", "refalns", "ambalns"]
        plotting.ecdf([isd.isizes]+[[len(alnset) for alnset in dataset[alnsetName]] for alnsetName in alnsetNames],
            ["average"]+alnsetNames, xlab="Insert size (bp)", main=name)
        
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
        return True
    except ImportError:
        return False    


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
