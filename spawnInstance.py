'''
Create a folder of symlinks to the SpedeSTEM source code for running concurrently.
Run SpedeSTEM, then capture results in a .zip file.

Created: March 8, 2013
Author: Matthew Demarest
Version: 1.0
'''

import argparse
import os
import tempfile
import subprocess
import zipfile
import glob

SPEDE = "SpedeSTEM_2.py"
STEM = "stem-hy.jar"
SRC = "src"
TEMPZIP = "tempZip.zip"

def parseArgs():
    parser = argparse.ArgumentParser(\
        description='A utility program for running a single instance of SpedeSTEM')
    parser.add_argument("zip", metavar="zipFile", type=str,
                help="Name of folder process will run in and name of zip file after",
                nargs=1)
    parser.add_argument("spedeArgs", metavar="spedeArgs", help="Arguments to SpedeSTEM.py",
                nargs="+")

    args = parser.parse_args()
    # debugging argument parsing
    # print args

    return args

def generateChild(ID):
    try :
        origDir = os.getcwd()

        tempDir = tempfile.mkdtemp()
        os.chdir(tempDir)

        spedeLoc = os.path.join(origDir, SPEDE)
        stemLoc = os.path.join(origDir, STEM)
        srcLoc = os.path.join(origDir, SRC)
        zipLoc = os.path.join(origDir, ID)

        # print orgDir, tempDir, spedeLoc, stemLoc, srcLoc

        os.symlink(spedeLoc, SPEDE)
        os.symlink(stemLoc, STEM)
        os.symlink(srcLoc, SRC)

        os.system("ls -l " + tempDir)
    except Exception:
        cleanup(tempDir, origDir)

    return {"tempDir": tempDir, "origDir": origDir, "spedeLoc": spedeLoc, "zipLoc": zipLoc}

def captureSpede(spedeArgs, files):
    call = ["python", SPEDE]
    spedeArgs = call + spedeArgs
    subprocess.call(spedeArgs)

    print 'creating archive'
    zf = zipfile.ZipFile(TEMPZIP, mode='w')
    try:
        for f in glob.glob(".txt"):
            zf.write(f)
    finally:
        zf.close()
        os.path.join()
        os.rename(zf, files["zipLoc"])
        cleanup(files["tempDir"], files["origDir"])

def cleanup(tempDir, origDir):
    os.chdir(origDir)

    for f in os.listdir(tempDir):
        path = os.path.join(tempDir, f)
        try:
            os.unlink(path)
        except Exception, e:
            print e

    os.removedirs(tempDir)

def main():
    args = parseArgs()
    files = generateChild(args.zip[0])

    # now in tempdir
    captureSpede(args.spedeArgs, files)

if __name__ == '__main__':
    main()
