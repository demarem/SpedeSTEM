#!/usr/bin/env python -O -t -W all

import shutil
import re
import sys

TREEFINDER = r"\([^\b]+;"
ZEROFINDER = r"(:0.0|:0)(?=[,);])"
SCINOTATIONFINDER = r"([0-9.]+e[+-][0-9]+)"

class CleanTrees:
    def __init__(self, treeFileList, prefixes, sigfigs=8):
        self.SIGFIGS = sigfigs
        self.treeFileList = treeFileList
        self.ZEROREPLACEMENT = ':0.' + '0' * (self.SIGFIGS - 1) + '1'

        # build the list of scaling factor
        if prefixes:
            self.prefixList = self.parsePrefixFile(prefixes)

            if len(self.prefixList) != len(self.treeFileList):
                print 'Number of tree files must match number of scaling factors ' + \
                'in scaling factor file'
                sys.exit()
        else:
            self.prefixList = ['[1.0]'] * len(self.treeFileList)

        for tree, scale in zip(treeFileList, self.prefixList):
            # clean all trees and rename cleaned.[old name]
            self.clean(scale, tree, 'cleaned.' + tree)

    def nexusClean(self, scaler, origTree='genetrees.tre', newTree='genetrees.tre'):
        print 'Cleaning Nexus Tree...'
        origTreeFile, newTreeFile = self.preserveOrig(origTree, newTree)
        line = origTreeFile.readline()
        while line.strip() != 'begin trees;':
            line = origTreeFile.readline()

        line = origTreeFile.readline()
        while line.strip() not in {'', 'end;'}:

            treeList = re.findall(TREEFINDER, line)
            tree = treeList[0]

            newTree = re.sub(ZEROFINDER, self.ZEROREPLACEMENT, tree)
            newTree = scaler + self.replaceSciNotation(newTree) + '\n'

            newTreeFile.write(newTree)
            line = origTreeFile.readline()

    def phylipClean(self, scaler, origTree='genetrees.tre', newTree='genetrees.tre'):
        print 'Cleaning Phylip tree...'
        origTreeFile, newTreeFile = self.preserveOrig(origTree, newTree)
        line = origTreeFile.readline()
        while line.strip() != '':

            treeList = re.findall(TREEFINDER, line)
            tree = treeList[0]

            newTree = re.sub(ZEROFINDER, self.ZEROREPLACEMENT, tree)
            newTree = scaler + self.replaceSciNotation(newTree) + '\n'

            newTreeFile.write(newTree)
            line = origTreeFile.readline()

    def preserveOrig(self, origTree, newTree):
        try:
            if origTree == 'genetree.tree':
                shutil.copyfile(origTree, origTree + '.orig')
                origTreeFile = open(origTree + '.orig', 'r')
            else:
                origTreeFile = open(origTree, 'r')
            newTreeFile = open(newTree, 'w')

            return origTreeFile, newTreeFile
        except IOError:
            print "ERROR: Could not open tree files '" + origTree + "' and '" + newTree + "'"

    def replaceSciNotation(self, line):
        def sub(matchobj):
            m = matchobj.group()
            converted = float(m)
            return ("%.20f" % converted)[:self.SIGFIGS + 2]
        return re.sub(SCINOTATIONFINDER, sub, line)


    def clean(self, scaler, origTree='genetrees.tre', newTree='genetrees.tre'):
        try:
            origTreeFile = open(origTree, 'r')
            line = origTreeFile.readline().strip()
            origTreeFile.close()
        except IOError:
            print "ERROR: Could not open tree file '" + origTree + "'"
            sys.exit()
        if line == "#NEXUS":
            self.nexusClean(scaler, origTree, newTree)
        elif line.strip()[0] == '(':
            self.phylipClean(scaler, origTree, newTree)
        elif line.strip()[0] == '[':
            print "Cannot clean trees with scaling factors..."
        else:
            print "Unrecognized original tree format..."

    def parsePrefixFile(self, prefixes):

        prefixList = []

        try:
            prefixFile = open(prefixes, 'r')
        except IOError:
            print "ERROR: Could not open scaling factors file."
            exit()

        for line in prefixFile:
            # check scaling formatting
            if not re.search(r'\[\d*\.\d*\]', line):
                print "ERROR: Each line in tree scaling file must be formatted as: '[scalingFactor]', " + \
                        "where scalingFactor is a floating point number."
                sys.exit()

            prefix = line.strip()
            prefixList.append(prefix)

        return prefixList

if __name__ == '__main__':
    print "No default functionality"


