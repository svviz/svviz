import logging
import os
import requests
import shutil
import sys
import tempfile
# import urllib
import zipfile

logging.getLogger("requests").setLevel(logging.WARNING)

def downloadWithProgress(link, outpath):
    print "Downloading %s" % link
    response = requests.get(link, stream=True)
    total_length = response.headers.get('content-length')

    with open(outpath, "wb") as outf:
        sys.stdout.write("\rDownload progress: [{}]".format(' '*50))
        sys.stdout.flush()

        if total_length is None: # no content length header
            outf.write(response.content)
        else:
            dl = 0
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=1024):
                dl += len(data)
                outf.write(data)
                done = int(50 * dl / total_length)
                sys.stdout.write("\rDownload progress: [{}{}]".format('='*done, ' '*(50-done)))
                sys.stdout.flush()
    sys.stdout.write("\n")
    outf.close()

def downloadDemo(which):
    try:
        downloadDir = tempfile.mkdtemp()
        archivePath = "{}/svviz-data.zip".format(downloadDir)

        # logging.info("Downloading...")
        # urllib.urlretrieve("https://github.com/svviz/svviz-data/archive/master.zip", archivePath)

        # downloadWithProgress("https://github.com/svviz/svviz-data/archive/{}.zip".format(which), archivePath)
        downloadWithProgress("http://web.stanford.edu/~nspies/svviz/examples/{}.zip".format(which), archivePath)
        
        logging.info("Decompressing...")
        archive = zipfile.ZipFile(archivePath)
        archive.extractall("{}".format(downloadDir))

        # import subprocess
        # subprocess.call("ls {}/svviz-data-{}".format(downloadDir, which), shell=True)
        # subprocess.call("ls {temp}/svviz-data-{which}/{which}".format(temp=downloadDir, which=which), shell=True)

        if not os.path.exists("svviz-examples"):
            os.makedirs("svviz-examples/")

        shutil.move("{temp}/{which}".format(temp=downloadDir, which=which), "svviz-examples/")
    except Exception as e:
        print "error downloading and decompressing example data: {}".format(e)
        return False

    if not os.path.exists("svviz-examples"):
        print "error finding example data after download and decompression"
        return False
    return True

    
def checkForDemo(which, autoDownload):
    if not os.path.exists("svviz-examples/{}".format(which)):
        if autoDownload:
            choice = "y"
        else:
            choice = raw_input("""Couldn't find example data in current working directory (svviz-examples/{}). """
                """Shall I download it and decompress it into the current working directory? Y/n:""".format(which))
        if choice.lower() in ["y", "yes", ""]:
            return downloadDemo(which)
        else:
            return False
    else:
        return True


def loadDemo(which="example1", autoDownload=False):
    if not checkForDemo(which, autoDownload):
        sys.exit(1)

    demodir = "svviz-examples/{}".format(which)
    info = open("{}/info.txt".format(demodir))
    cmd = None
    for line in info:
        if line.startswith("#"):
            continue
        cmd = line.strip().split()
        cmd = [c.format(data=demodir) for c in cmd]
        break

    return cmd