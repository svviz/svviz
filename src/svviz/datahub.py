import collections
import os
import pyfaidx
import pysam

from svviz import annotations

def nameFromBamPath(bampath):
    return os.path.basename(bampath).replace(".bam", "").replace(".sorted", "").replace(".sort", "").replace(".", "_").replace("+", "_")
def nameFromBedPath(bampath):
    return os.path.basename(bampath).replace(".bed", "").replace(".sorted", "").replace(".sort", "").replace(".", "_").replace("+", "_").replace(".gz", "")


class DataHub(object):
    def __init__(self):
        self.args = None
        self.searchDistance = None
        self.alignDistance = None
        self.samples = collections.OrderedDict()
        self.genome = None
        self.sources = {}
        self.annotationSets = collections.OrderedDict()

        # for storing axes, annotations, etc, by allele
        self.alleleTracks = collections.defaultdict(collections.OrderedDict)
        self.trackCompositor = None

        self.dotplots = {}
        self.info = {}

        self.reset()

    def __getstate__(self):
        """ allows pickling of DataHub()s """
        state = self.__dict__.copy()
        del state["args"]
        del state["genome"]
        return state

    def reset(self):
        """ reset for a new variant; keeps the ReadStatistics """
        self.variant = None
        self._counts = None
        self._alignmentSetsByName = None
        for sampleName, sample in self.samples.iteritems():
            sample.reset()
        self.trackCompositor = None

    def setArgs(self, args):
        self.args = args

        try:
            self.genome = pyfaidx.Fasta(args.ref, as_raw=True)

            for bamPath in self.args.bam:
                name = nameFromBamPath(bamPath)

                sample = Sample(name, bamPath)
                self.samples[name] = sample

            if self.args.annotations:
                for annoPath in self.args.annotations:
                    name = nameFromBedPath(annoPath)
                    self.annotationSets[name] = annotations.AnnotationSet(annoPath)
        except:
            self.args._parser.print_help()
            print ""
            raise

    def getCounts(self):
        if self._counts is None:
            self._counts = collections.OrderedDict()
            for name, sample in self.samples.iteritems():
                self._counts[name] = collections.Counter([alnCollection.choice for alnCollection in sample.alnCollections])
            self._counts["Total"] = dict((allele, sum(self._counts[name][allele] for name in self.samples)) 
                                          for allele in ["alt", "ref", "amb"])

        return self._counts

    def getAlignmentSetByName(self, name):
        if self._alignmentSetsByName is None:
            self._alignmentSetsByName = {}
            for sample in self:
                for alnCollection in sample.alnCollections:
                    self._alignmentSetsByName[alnCollection.name] = alnCollection.chosenSet()
        return self._alignmentSetsByName.get(name, None)

    def __iter__(self):
        return iter(self.samples.values())



class Sample(object):
    def __init__(self, name, bamPath=None):
        self.name = name

        self.singleEnded = False
        self.orientations = None
        self.searchDistance = None

        self.bamPath = bamPath
        self.bam = pysam.Samfile(self.bamPath, "rb") if self.bamPath else None

        self.readStatistics = None
        self.insertSizePlot = None

        self.reset()


    def __getstate__(self):
        """ allows pickling of Samples()s """
        state = self.__dict__.copy()
        del state["bam"]
        del state["reads"]
        return state

    def reset(self):
        self.reads = []
        self.alnCollections = []
        self.tracks = collections.OrderedDict()


    def chosenSets(self, choice):
        thisChoice = []
        for alnCollection in self.alnCollections:
            if alnCollection.choice == choice:
                thisChoice.append(alnCollection.chosenSet())
        return thisChoice

