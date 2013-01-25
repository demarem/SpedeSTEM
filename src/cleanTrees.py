#!/usr/bin/env python -O -t -W all

import shutil, re, argparse

TREEFINDER = r"\([^\b]+;"
ZEROFINDER = r"(:0.0|:0)(?=[,);])"
SCINOTATIONFINDER = r"([0-9.]+e[+-][0-9]+)"

class CleanTrees:
    def __init__(self, treeFileList, prefixes, sigfigs=8):
        self.SIGFIGS = sigfigs
        self.treeFileList = treeFileList
        self.ZEROREPLACEMENT = ':0.' + '0' * (self.SIGFIGS - 1) + '1'

        if prefixes:
            self.prefixList = self.parsePrefixFile(prefixes)

            assert len(self.prefixList) == len(self.treeFileList), \
                'Number of tree files must match number of scaling factors ' + \
                'in scaling factor file'
        else:
            self.prefixList = ['[1.0]'] * len(self.treeFileList)

        for tree, scale in zip(treeFileList, self.prefixList):
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
            newTree = '[' + scaler + ']' + self.replaceSciNotation(newTree) + '\n'

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
            newTree = '[' + scaler + ']' + self.replaceSciNotation(newTree) + '\n'

            newTreeFile.write(newTree)
            line = origTreeFile.readline()

    def preserveOrig(self, origTree, newTree):
        if origTree == 'genetree.tree':
            shutil.copyfile(origTree, origTree + '.orig')
            origTreeFile = open(origTree + '.orig', 'r')
        else:
            origTreeFile = open(origTree, 'r')
        newTreeFile = open(newTree, 'w')

        return origTreeFile, newTreeFile

    def replaceSciNotation(self, line):
        def sub(matchobj):
            m = matchobj.group()
            converted = float(m)
            return ("%.20f" % converted)[:self.SIGFIGS + 2]
        return re.sub(SCINOTATIONFINDER, sub, line)


    def clean(self, scaler, origTree='genetrees.tre', newTree='genetrees.tre'):
        origTreeFile = open(origTree, 'r')
        line = origTreeFile.readline().strip()
        origTreeFile.close()
        if line == "#NEXUS":
            self.nexusClean(scaler, origTree, newTree)
        elif line.strip()[0] == '(':
            self.phylipClean(scaler, origTree, newTree)
        else:
            print "Unrecognized original tree format..."

    def parsePrefixFile(self, prefixes):

        prefixList = []

        try:
            prefixFile = open(prefixes, 'r')
        except IOError:
            print "Error opening scaling factors file."
            exit()

        for line in prefixFile:
            # check scaling formatting
            assert re.search(r'\[\d*\.\d*\]', line), \
                'Each line in tree scaling file must be formatted as: [scalingFactor], ' + \
                'where scalingFactor is a floating point number.'
            prefix = line.strip()
            prefixList.append(prefix)

        return prefixList


# def main():
#    parser = argparse.ArgumentParser(\
#            description='Clean trees with Nexus and Phylip formatting.')
#    parser.add_argument('trees', metavar='TREE', nargs='*', \
#                   help='trees to be cleaned')
#    parser.add_argument('-t', '--test', action="store_true", \
#                   help='execute unit testing mode')
#    parser.add_argument('--nexus', action="store_true", \
#                   help='force nexus clean')
#    parser.add_argument('--phylip', action="store_true", \
#                   help='force phylip clean')
#    parser.add_argument('--scalingList', metavar='scalingFactor', type=float, nargs='+', \
#                   help='list scaling values')
#    parser.add_argument('--scalingFile', metavar='scalingFile', nargs=1, \
#                   help='list scaling values')
#    parser.add_argument('--scalingAll', metavar='scalingFactor', type=float, nargs=1, \
#                   default=1.0, help='apply scalingFactor to all trees, DEFAULT: 1.0')
#    args = parser.parse_args()
#    print args
#
#    if args.scalingList:
#        assert len(args.scalingList) == len(args.trees), \
#            'number of scalingFactors must equal the number of tree files'
#        scaler = [str(x) for x in args.scalingList]
#    else:
#        scaler = [str(args.scalingAll)] * len(args.trees)
#
#    if args.test:
#        print "testing"
#    elif args.nexus:
#        for tree, scale in zip(args.trees, scaler):
#            self.nexusClean(scale, tree, 'cleaned.' + tree)
#    elif args.phylip:
#        for tree, scale in zip(args.trees, scaler):
#            self.phylipClean(scale, tree, 'cleaned.' + tree)
#    else:
#        for tree, scale in zip(args.trees, scaler):
#            self.clean(scale, tree, 'cleaned.' + tree)

def test():
    print 'TESTING:'


if __name__ == '__main__':
    test = CleanTrees(['blah', 'blah'], None)


