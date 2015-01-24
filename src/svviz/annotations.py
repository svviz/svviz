import logging
import os
import pysam

class AnnotationError(Exception):
    pass

def ensureIndexed(bedPath):
    if not bedPath.endswith(".gz"):
        if not os.path.exists(bedPath+".gz"):
            logging.info("bgzf compressing {}".format(bedPath))
            pysam.tabix_compress(bedPath, bedPath+".gz")
            if not os.path.exists(bedPath+".gz"):
                raise Exception("Failed to create compress bed file for {}; make sure the bed file is "
                    "sorted and the directory is writeable".format(bedPath))
        bedPath += ".gz"
    if not os.path.exists(bedPath+".tbi"):
        logging.info("creating tabix index for {}".format(bedPath))
        pysam.tabix_index(bedPath, preset="bed")
        if not os.path.exists(bedPath+".tbi"):
            raise Exception("Failed to create tabix index file for {}; make sure the bed file is "
                "sorted and the directory is writeable".format(bedPath))

    line = pysam.Tabixfile(bedPath).fetch().next()
    if len(line.strip().split("\t")) < 6:
        raise AnnotationError("BED files need to have at least 6 (tab-delimited) fields (including chrom, start, end, name, score, strand; score is unused)")

    return bedPath

class AnnotationSet(object):
    def __init__(self, bedPath):
        self.bedPath = ensureIndexed(bedPath)
        self.bed = pysam.Tabixfile(self.bedPath)

    def getAnnotations(self, chrom, start, end, clip=False):
        """ Returns annotations, in genome order, from the requested genomic region """
        annotations = []
        
        if chrom not in self.bed.contigs:
            return []
            
        for row in self.bed.fetch(chrom, start, end):
            values = row.split("\t")
            thickSegments = []
            anno = Annotation(values[0], values[1], values[2], values[5], values[3], thickSegments=thickSegments)
            if clip:
                anno.start = max(anno.start, start)
                anno.end = min(anno.end, end)
            annotations.append(anno)

        return annotations


class Annotation(object):
    def __init__(self, chrom, start, end, strand, name, thickSegments=None, info=None):
        self.chrom = chrom
        self.start = int(start)
        self.end = int(end)
        self.strand = strand
        self.name = name

        self.info = info if info is not None else {}
        self.thickSegments = thickSegments if thickSegments is not None else []

