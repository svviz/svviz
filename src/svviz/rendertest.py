import cPickle as pickle
import os
import sys

from svviz import app
from svviz import utilities

class MockArgs(object):
    def __getattr__(self, attr):
        return None

for i in range(1000):
    exportPath = "tests/export{:03d}.pdf".format(i)
    if not os.path.exists(exportPath):
        break

dataHub = pickle.load(open(sys.argv[1]))

dataHub.args = MockArgs()
dataHub.args.thicker_lines = False
dataHub.args.export = exportPath


app.renderSamples(dataHub)
app.ensureExportData(dataHub)
app.runDirectExport(dataHub)

utilities.launchFile(dataHub.args.export)