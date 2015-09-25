import collections
import logging
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
    def __init__(self, regions, sam, minmapq=-1, pair_minmapq=-1, is_paired=True, include_supplementary=False):
        self.include_supplementary = include_supplementary
        self.regions = regions
        self.sam = sam
        self.minmapq = minmapq
        self.readsByID = collections.defaultdict(ReadSet)
        self.tomatch = set()
        self.supplementaryAlignmentsFound = False

        for region in self.regions:
            self.tomatch.update(self.loadRegion(region.chr(), region.start(), region.end()))

        if is_paired:
            logging.debug("  To-match: {}, min-mapq: {}".format(len(self.tomatch), self.minmapq))
            self.domatching()

        # for read in self.tomatch:
        #     assert len(self.readsByID[read.qname]) > 1

        matchIDs = set(read.qname for read in self.tomatch)
        self.matched = [self.readsByID[id_].reads for id_ in matchIDs]

        if pair_minmapq > 0:
            self.matched = [self.readsByID[id_].reads for id_ in matchIDs 
                            if max(read.mapq for read in self.readsByID[id_].reads)>=pair_minmapq]

        # Unclear what to do with supplementary alignments...
        # self.matched = [[read for read in self.readsByID[id_].reads if read.flag&0x800==0] for id_ in matchIDs]

        logging.info("  missing pairs: {}".format(sum(1 for x in self.matched if (len(x)<2 and x[0].is_paired))))

    def domatching(self):
        t0 = None

        for i, read in enumerate(self.tomatch):#[:150]):
            if i % 1000 == 0:
                if t0 is None:
                    t0 = time.time()
                    elapsed = "Finding mate pairs..."
                else:
                    t1 = time.time()
                    elapsed = t1-t0
                    t0 = t1
                logging.info("  {} {} {}".format(i, len(self.tomatch), elapsed))
            if len(self.readsByID[read.qname].reads) < 2:
                self.findmatch(read)
                # if len(self.readsByID[read.qname]) < 2:
                #     print "couldn't find match:", read.qname, read.tid, read.pos, read.rnext, read.pnext


    def findmatch(self, read):
        if read.is_paired and read.rnext >= 0:
            chrom = self.sam.getrname(read.rnext)
            self.loadRegion(chrom, read.pnext, read.pnext+1)
        # self.loadRegion(read.next_reference_id, read.next_reference_start, read.next_reference_start)


    def loadRegion(self, chrom, start, end):
        reads = list(self.sam.fetch(chrom, start, end))

        if len(reads) > 100000:
            logging.warn("  LOTS OF READS IN MATE-PAIR REGION:{} {} {} {}".format(chrom, start, end, len(reads)))
            # return []

        goodReads = []
        for read in reads:
            if read.mapq >= self.minmapq and not read.is_secondary and not read.is_duplicate:
                if (read.flag & 0x800) != 0 and not self.include_supplementary:
                    self.supplementaryAlignmentsFound = True
                    continue
                # beforeString = str([(rr.qname, rr.flag) for rr in self.readsByID[read.qname].reads]) +str((read.qname, read.flag))
                self.readsByID[read.qname].add(read)
                goodReads.append(read)

                # if len(self.readsByID[read.qname].reads) > 1:
                #     print ""
                #     print "\n".join(map(str, self.readsByID[read.qname].reads))
                #     print "*"*200

        return goodReads