import logging
import numpy
import time

def scoreAlignmentSetCollection(alnCollection, isd, minInsertSizeScore=0, expectedOrientations="any"):
    for name, alignmentSet in alnCollection.sets.iteritems():
        alignmentSet.evidences["insertSizeScore"] = isd.score(len(alignmentSet))
        alignmentSet.evidences["alignmentScore"] = sum(aln.score for aln in alignmentSet.getAlignments())
        alignmentSet.evidences["orientation"] = alignmentSet.orientation()

        alignmentSet.evidences["valid"] = (True, )

        if alignmentSet.evidences["insertSizeScore"] <= minInsertSizeScore:
            alignmentSet.evidences["valid"] = (False, "insertSizeScore")
        if not checkOrientation(alignmentSet.evidences["orientation"], expectedOrientations):
            alignmentSet.evidences["valid"] = (False, "orientation")
        if not alignmentSet.allSegmentsWellAligned():
            alignmentSet.evidences["valid"] = (False, "alignmentScore")

def checkOrientation(orientation, expectedOrientations):
    if expectedOrientations in ["any", None]:
        return True
    if orientation in expectedOrientations:
        return True
    return False

def disambiguate(alnCollection, insertSizeLogLikelihoodCutoff=1.0):
    def choose(which, why):
        alnCollection.choose(which, why)
        return which

    # check the validity of the alignment sets (see scoreAlignmentSetCollection())
    if alnCollection["alt"].evidences["valid"][0] and not alnCollection["ref"].evidences["valid"][0]:
        return choose("alt", alnCollection["ref"].evidences["valid"][1])
    if alnCollection["ref"].evidences["valid"][0] and not alnCollection["alt"].evidences["valid"][0]:
        return choose("ref", alnCollection["alt"].evidences["valid"][1])
    if not alnCollection["ref"].evidences["valid"][0] and not alnCollection["alt"].evidences["valid"][0]:
        return choose("amb", str(alnCollection["ref"].evidences["valid"][1])+"_"+str(alnCollection["alt"].evidences["valid"][1]))

    if alnCollection["alt"].evidences["alignmentScore"] > alnCollection["ref"].evidences["alignmentScore"]:
        return choose("alt", "alignmentScore")
    if alnCollection["ref"].evidences["alignmentScore"] > alnCollection["alt"].evidences["alignmentScore"]:
        return choose("ref", "alignmentScore")

    logRatio = numpy.log2(alnCollection["alt"].evidences["insertSizeScore"] / alnCollection["ref"].evidences["insertSizeScore"])
    if logRatio > insertSizeLogLikelihoodCutoff:
        return choose("alt", "insertSizeScore")
    if logRatio < -insertSizeLogLikelihoodCutoff:
        return choose("ref", "insertSizeScore")

    return choose("amb", "same scores")

def batchDisambiguate(alnCollections, isd, expectedOrientations):
    t0 = time.time()

    for alnCollection in alnCollections:
        scoreAlignmentSetCollection(alnCollection, isd, 0, expectedOrientations)

    for alnCollection in alnCollections:
        disambiguate(alnCollection)

    t1 = time.time()
    logging.info("Time for disambiguation: {:.2f}s".format(t1-t0))