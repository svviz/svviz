import cPickle as pickle
import filecmp
import json
import os
import shutil
import sys
import time

from svviz import app
from svviz import utilities

class MockArgs(object):
    def __getattr__(self, attr):
        return None


timings = {}

for testName in ["mei", "inv", "ins_moleculo", "ins_pacbio", "del_chr1", "translocation"]:
    print ">", testName, "<"

    exportPath = "tests/export_{}_new.svg".format(testName)
    originalPath = "tests/export_{}_original.svg".format(testName)

    dataHub = pickle.load(open("tests/{}.pickle".format(testName)))

    dataHub.args = MockArgs()
    dataHub.args.thicker_lines = False
    dataHub.args.export = exportPath

    t0 = time.time()
    app.renderSamples(dataHub)
    app.ensureExportData(dataHub)    
    app.runDirectExport(dataHub)
    t1 = time.time()
    timings[testName] = t1-t0

    if not os.path.exists(originalPath):
        print "  first time running; nothing to compare against"
        shutil.copy(exportPath, originalPath)
    else:
        if filecmp.cmp(originalPath, exportPath, shallow=False):
            print "  files identical!"
        else:
            for a, b in zip(open(originalPath).readlines(), open(exportPath).readlines()):
                if a != b:
                    print "FILES DIFFER! First line that differs:"
                    print "Original:", a.strip()
                    print "New:     ", b.strip()
                    print "..."

                    time.sleep(3)
                    utilities.launchFile(exportPath)
                    utilities.launchFile(originalPath)

                    break


timingsPath = "tests/renderTimings.json.txt"
regenerateTimings = False
try:
    oldTimings = json.load(open(timingsPath))
    print "{:<20}{:>20}{:>20}".format("Test Name", "Previous", "New")
    for testName in sorted(timings):
        try:
            remark = "ok"
            if timings[testName] > oldTimings[testName] * 1.1:
                remark = "** slower! **"
            print "{:<20}{:>19.2f}s{:>19.2f}s\t{}".format(testName, oldTimings[testName], timings[testName], remark)
        except KeyError:
            print "{:<20}{:>20}s{:>19.2f}s".format(testName, "", timings[testName])
            regenerateTimings = True

except IOError:
    print "unable to load previous timings..."

if not os.path.exists(timingsPath) or regenerateTimings:
    print "overwriting previous timings..."
    json.dump(timings, open(timingsPath, "w"))
    