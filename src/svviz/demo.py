import logging
import os
import sys
import tempfile
import urllib
import zipfile

def downloadDemos():
    try:
        downloadDir = tempfile.mkdtemp()
        archivePath = "{}/svviz-data.zip".format(downloadDir)

        logging.info("Downloading...")
        urllib.urlretrieve("https://github.com/svviz/svviz-data/archive/master.zip", archivePath)

        logging.info("Decompressing...")
        archive = zipfile.ZipFile(archivePath)
        archive.extractall()
    except Exception as e:
        print "error downloading and decompressing example data: {}".format(e)
        return False

    if not os.path.exists("svviz-data-master"):
        print "error finding example data after download and decompression"
        return False
    return True

    
def checkForDemos():
    if not os.path.exists("svviz-data-master"):
        choice = raw_input("Couldn't find example data in current working directory (svviz-data-master). Shall I download it and decompress it into the current working directory? y/n:")
        if choice.lower() in ["y", "yes"]:
            return downloadDemos()
        else:
            return False
    else:
        return True


def loadDemo(which="example1"):
    if not checkForDemos():
        sys.exit(1)

    demodir = "svviz-data-master/{}".format(which)
    info = open("{}/info.txt".format(demodir))
    cmd = None
    for line in info:
        if line.startswith("#"):
            continue
        cmd = line.strip().split()
        cmd = [c.format(data=demodir) for c in cmd]
        break

    return cmd