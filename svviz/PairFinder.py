import collections
import time

class ReadSet(object):
    def __init__(self):
        self.reads = []
        self.strings = []
    def add(self, newread):
        if str(newread) not in self.strings:
            self.strings.append(str(newread))
            self.reads.append(newread)

class PairFinder(object):
    def __init__(self, regions, sam, minmapq=-1):
        self.regions = regions
        self.sam = sam
        self.minmapq = minmapq
        self.readsByID = collections.defaultdict(ReadSet)
        self.tomatch = set()
        for region in self.regions:
            self.tomatch.update(self.loadRegion(region.chr(), region.start(), region.end()))

        print len(self.tomatch), self.minmapq
        self.domatching()

        # for read in self.tomatch:
        #     assert len(self.readsByID[read.qname]) > 1

        matchIDs = set(read.qname for read in self.tomatch)
        self.matched = [self.readsByID[id_].reads for id_ in matchIDs]

        # Unclear what to do with supplementary alignments...
        # self.matched = [[read for read in self.readsByID[id_].reads if read.flag&0x800==0] for id_ in matchIDs]

        print "missing pairs:", sum(1 for x in self.matched if len(x)<2)

    def domatching(self):
        t0 = None

        for i, read in enumerate(self.tomatch):#[:150]):
            if i % 1000 == 0:
                if t0 is None:
                    t0 = time.time()
                    elapsed = "starting..."
                else:
                    t1 = time.time()
                    elapsed = t1-t0
                    t0 = t1
                print i, len(self.tomatch), elapsed
            if len(self.readsByID[read.qname].reads) < 2:
                self.findmatch(read)
                # if len(self.readsByID[read.qname]) < 2:
                #     print "couldn't find match:", read.qname, read.tid, read.pos, read.rnext, read.pnext


    def findmatch(self, read):
        chrom = self.sam.getrname(read.rnext)
        self.loadRegion(chrom, read.pnext, read.pnext+1, verbose=True)
        # self.loadRegion(read.next_reference_id, read.next_reference_start, read.next_reference_start)


    def loadRegion(self, chrom, start, end, verbose=False):
        reads = list(self.sam.fetch(chrom, start, end, reopen=False))

        if len(reads) > 100000:
            if verbose:
                print "LOTS OF READS IN REGION:", chrom, start, end, len(reads)
            # return []

        for read in reads:
            if read.mapq > self.minmapq:
                # beforeString = str([(rr.qname, rr.flag) for rr in self.readsByID[read.qname].reads]) +str((read.qname, read.flag))
                self.readsByID[read.qname].add(read)

                # if len(self.readsByID[read.qname].reads) > 2:
                #     print self.readsByID[read.qname]

        reads = [read for read in reads if read.mapq > self.minmapq]
        return reads