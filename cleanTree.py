#!/usr/bin/env python -O -t -W all

import shutil, re, argparse

SIGFIGS = 8
TREEFINDER = r"\([^\b]+;"
ZEROFINDER = r"(:0.0|:0)(?=[,);])"
SCINOTATIONFINDER = r"([0-9.]+e[+-][0-9]+)"
ZEROREPLACEMENT = ':0.' + '0' * (SIGFIGS - 1) + '1'
TREEPREFIX = '[1.0]'

def nexusClean(origTree='genetrees.tre', newTree='genetrees.tre'):
    print 'Cleaning Nexus Tree...'
    origTreeFile, newTreeFile = preserveOrig(origTree, newTree)
    line = origTreeFile.readline()
    while line.strip() != 'begin trees;':
        line = origTreeFile.readline()

    line = origTreeFile.readline()
    while line.strip() not in {'', 'end;'}:

        treeList = re.findall(TREEFINDER, line)
        tree = treeList[0]

        newTree = re.sub(ZEROFINDER, ZEROREPLACEMENT, tree)
        newTree = TREEPREFIX + replaceSciNotation(newTree) + '\n'

        newTreeFile.write(newTree)
        line = origTreeFile.readline()

def phylipClean(origTree='genetrees.tre', newTree='genetrees.tre'):
    print 'Cleaning Phylip tree...'
    origTreeFile, newTreeFile = preserveOrig(origTree, newTree)
    line = origTreeFile.readline()
    while line.strip() != '':

        treeList = re.findall(TREEFINDER, line)
        tree = treeList[0]

        newTree = re.sub(ZEROFINDER, ZEROREPLACEMENT, tree)
        newTree = TREEPREFIX + replaceSciNotation(newTree) + '\n'

        newTreeFile.write(newTree)
        line = origTreeFile.readline()

def preserveOrig(origTree, newTree):
    if origTree == 'genetree.tree':
        shutil.copyfile(origTree, origTree + '.orig')
        origTreeFile = open(origTree + '.orig', 'r')
    else:
        origTreeFile = open(origTree, 'r')
    newTreeFile = open(newTree, 'w')

    return origTreeFile, newTreeFile

def replaceSciNotation(line):
    def sub(matchobj):
        m = matchobj.group()
        converted = float(m)
        return ("%.20f" % converted)[:SIGFIGS + 2]
    return re.sub(SCINOTATIONFINDER, sub, line)


def clean(origTree='genetrees.tre', newTree='genetrees.tre'):
    origTreeFile = open(origTree, 'r')
    line = origTreeFile.readline().strip()
    origTreeFile.close()
    if line == "#NEXUS":
        nexusClean(origTree, newTree)
    elif line.strip()[0] == '(':
        phylipClean(origTree, newTree)
    else:
        print "Unrecognized original tree format..."

def test():
    print 'TESTING:'

def main():
    parser = argparse.ArgumentParser(\
            description='Clean trees with Nexus and Phylip formatting.')
    parser.add_argument('-t', '--test', action="store_true", \
                   help='execute unit testing mode')
    parser.add_argument('--nexus', action="store_true", \
                   help='force nexus clean')
    parser.add_argument('--phylip', action="store_true", \
                   help='force phylip clean')
    parser.add_argument('trees', metavar='TREE', nargs='*', \
                   help='trees to be cleaned')
    args = parser.parse_args()
    if args.test:
        print "testing"
    elif args.nexus:
        for tree in args.trees:
            nexusClean(tree, 'cleaned.' + tree)
    elif args.phylip:
        for tree in args.trees:
            phylipClean(tree, 'cleaned.' + tree)
    else:
        for tree in args.trees:
            clean(tree, 'cleaned.' + tree)



if __name__ == '__main__':
    main()


