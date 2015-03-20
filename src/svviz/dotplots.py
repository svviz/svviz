import logging
import os
import shutil

try:
    import numpy
    from scipy import misc
    import tempfile

    def dotplot(s1, s2, wordsize=5, overlap=5, verbose=1):
        """ verbose = 0 (no progress), 1 (progress if s1 and s2 are long) or
        2 (progress in any case) """
        doProgress = False
        if verbose > 1 or len(s1)*len(s2) > 1e6:
            doProgress = True

        mat = numpy.ones(((len(s1)-wordsize)/overlap+2, (len(s2)-wordsize)/overlap+2))

        for i in range(0, len(s1)-wordsize, overlap):
            if i % 1000 == 0 and doProgress:
                logging.info("  dotplot progress: {} of {} rows done".format(i, len(s1)-wordsize))
            word1 = s1[i:i+wordsize]

            for j in range(0, len(s2)-wordsize, overlap):
                word2 = s2[j:j+wordsize]

                if word1 == word2 or word1 == word2[::-1]:
                    mat[i/overlap, j/overlap] = 0
        
        imgData = None
        tempDir = tempfile.mkdtemp()
        try:
            path = os.path.join(tempDir, "dotplot.png")
            misc.imsave(path, mat)
            imgData = open(path).read()
        except Exception, e:
            logging.error("Error generating dotplots:'{}'".format(e))
        finally:
            shutil.rmtree(tempDir)
        return imgData

except ImportError:
    def dotplot(*args, **kwdargs):
        logging.error("dotplots requires the python librarys scipy and PIL")
        return None