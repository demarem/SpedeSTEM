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
    parser.add_argument("reqFiles", metavar="file", help="user files necessary" +
        "for running SpedeSTEM" , nargs='+')
    parser.add_argument("--zip", metavar="zipFile",
                help="Name of folder process will run in and name of zip file after",
                nargs=1, required=True)

    args, rest = parser.parse_known_args()
    # debugging argument parsing
    # print args

    return args.reqFiles, args.zip[0] + '.zip', rest

def generateChild(ID, files):
    try :
        origDir = os.getcwd()

        tempDir = tempfile.mkdtemp()
        os.chdir(tempDir)

        spedeLoc = os.path.join(origDir, SPEDE)
        stemLoc = os.path.join(origDir, STEM)
        srcLoc = os.path.join(origDir, SRC)
        zipLoc = os.path.join(origDir, ID)

        for f in files:
            if not os.path.isabs(f):
               path = os.path.join(origDir, f)
            os.rename(path, os.path.basename(f))

        # print orgDir, tempDir, spedeLoc, stemLoc, srcLoc

        os.symlink(spedeLoc, SPEDE)
        os.symlink(stemLoc, STEM)
        os.symlink(srcLoc, SRC)

    except Exception:
        cleanup(tempDir, origDir)
        print "Error creating temporary directory"
        exit()

    return {"tempDir": tempDir, "origDir": origDir, "zipLoc": zipLoc}

def captureSpede(spedeArgs, paths):
    call = ["python", SPEDE]
    spedeArgs = call + spedeArgs
    subprocess.call(spedeArgs)

    zf = zipfile.ZipFile(TEMPZIP, mode='w')
    try:
        for f in glob.glob("*.txt"):
            zf.write(f)
    finally:
        zf.close()
        os.rename(TEMPZIP, paths["zipLoc"])
        cleanup(paths["tempDir"], paths["origDir"])

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
    files, zipFile, args = parseArgs()
    paths = generateChild(zipFile, files)

    # working directory is now tempdir
    captureSpede(args, paths)

if __name__ == '__main__':
    main()
