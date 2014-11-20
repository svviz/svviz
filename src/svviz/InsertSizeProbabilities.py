import numpy
from scipy.stats import gaussian_kde

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
        isizes = sampleInsertSizes(bam)
        if len(isizes) < 10:
            self.fail = True
            self.min = 0
            return
        self.fail = False
        self.kde = gaussian_kde(isizes)
        self.min = numpy.min(self.kde(numpy.linspace(0, max(isizes), 100)))
        print "Min score:", self.min

    def score(self, isize):
        # we don't ever want a 0 probability
        if self.fail:
            return 0
        score = self.kde(abs(isize))
        return max(score, self.min)




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
