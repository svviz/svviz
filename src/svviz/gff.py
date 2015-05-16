""" Simple parser for gff/gtf format genes, indexed by tabix """

import collections
import pysam
import re
from svviz.tabix import ensureIndexed
from svviz.annotations import AnnotationSet, Annotation

RE_TRANSCRIPT = r".*transcript_id \"([^\"]*)\".*"
RE_GENE = r".*gene_id \"([^\"]*)\".*"
RE_LINE = r"(.*)\t(.*)\t(.*)\t(.*)\t(.*)\t(.*)\t(.*)\t(.*)\t(.*)"



class GeneAnnotationSet(AnnotationSet):
    def __init__(self, tabixPath):
        super(GeneAnnotationSet, self).__init__(tabixPath, preset="gff")
    
    def getAnnotations(self, chrom, start, end, clip=False, extension=1000000):
        chrom = self.fixChromFormat(chrom)
        
        lines = self.tabix.fetch(chrom, max(0, start-extension), end+extension)

        transcriptsToLines = collections.defaultdict(list)

        for line in lines:
            if len(line) < 2:
                continue                
            tx = re.match(RE_TRANSCRIPT, line).group(1)


            transcriptsToLines[tx].append(line)

        genes = []
        for transcript, lines in transcriptsToLines.iteritems():
            genes.append(GTFGene(lines))

        if extension > 0:
            for gene in genes:
                if gene.name == "NM_002653":
                    print gene.name, gene.start, gene.end, start, end
            genes = [gene for gene in genes if not (end<gene.start or start>gene.end)]#start<=gene.start<=end or start<=gene.end<=end)]

        if clip:
            for gene in genes:
                gene.clip(start, end)

        return genes


class GTFGene(Annotation):
    def __init__(self, gtfLines):
        self.name = None
        self.chrom = None
        self.start = None
        self.end = None
        self.strand = None
        self.info = None

        self.txExons = []
        self.cdExons = []

        self.fromGTFLines(gtfLines)

    def clip(self, start, end):
        self.start = max(start, self.start)
        self.end = min(end, self.end)

        newTxExons = []
        for txExon in self.txExons:
            curStart, curEnd = txExon
            if curStart>end or curEnd<start:
                continue
            newTxExons.append((max(start, curStart), min(end, curEnd)))
        self.txExons = newTxExons

        newCdExons = []
        for cdExon in self.cdExons:
            curStart, curEnd = cdExon
            if curStart>end or curEnd<start:
                continue
            newCdExons.append((max(start, curStart), min(end, curEnd)))
        self.cdExons = newCdExons


    def fromGTFLines(self, gtfLines):
        for line in gtfLines:
            fields = re.match(RE_LINE, line).groups()

            chrom = fields[0]
            start = int(fields[3])
            end = int(fields[4])
            strand = fields[6]

            event = fields[2]

            gene = re.match(RE_TRANSCRIPT, line).group(1)

            if self.name is not None and self.name != gene:
                raise Exception("transcripts don't belong to the same gene")
            self.name = gene

            if self.strand is not None and self.strand != strand:
                raise Exception("exons aren't on the same strand")
            self.strand = strand

            if self.chrom is not None and self.chrom != chrom:
                raise Exception("exons aren't on the same chromosome")
            self.chrom = chrom

            if self.start is None or start < self.start:
                self.start = start

            if self.end is None or end > self.end:
                self.end = end

            if self.end < self.start:
                self.start, self.end = self.end, self.start

            if event == "CDS":
                self.cdExons.append((start, end))

            if event == "exon":
                self.txExons.append((start, end))


    def __str__(self):
        return "{} {}:{}-{}{} {} {}".format(self.name, self.chrom, self.start, self.end, self.strand, self.txExons, self.cdExons)

    def __repr__(self):
        return str(self)

if __name__ == '__main__':
    """ UCSC Genes table exported as gtf, then sorted using:
    gsort -k1,1V -k4,4n -k5,4n /Users/nspies/Downloads/hg19.genes.gtf | bgzip > /Users/nspies/Downloads/hg19.genes.gtf.gz

    (or remove the V option to get it to work with normal OS X sort) """

    gtf = GeneAnnotationSet("/Users/nspies/Downloads/hg19.genes.gtf.gz")
    genes = gtf.getAnnotations("chr12", 66218240, 66360071)

    for gene in genes:
        print gene