#!/usr/local/bin/python2.7
# encoding: utf-8

import sys
import argparse
import operator

DEBUG = False


class RepVariationFinder(object):
    '''
    Tools for counting the variations in each replicate of a Nexus file.

    Attributes:
        verbose: Boolean indicating amount of messaging to produce to stdout
        replicateToCount: Dictionary mapping replicate number to the number of
            variations in that replicate
        replicateToLocation: Dictionary mapping replicate number to the
            location (byte) that it can be found in the nexus file.
            Example: {2: (34, 55)}, contents of replicate 2 are [34, 55]
        inFile: Nexus formatted file to be read from for counting variation and
            to construct a new outFile
    '''

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.replicateToCount = {}
        self.replicateToLocation = {}
        self.inFile = None
        self._startByte = 0

    def read(self, nexusFile):
        """ Determine variation in each matrix of a Nexus file.

        Resets the replicateToCount dictionary populates it based on each
        matrix in file.

        Args:
           nexusFile: An open nexus file

        """
        self.inFile = nexusFile
        self.replicateToCount.clear()
        self._totalLines = 0
        replicate = 0
        currentPos = nexusFile.tell()
        line = nexusFile.readline()
        while line:
            if all(x in line.lower() for x in {'begin', 'data'}):
                # determine location of each replicate
                if replicate > 0:
                    previousRange = self.replicateToLocation[replicate - 1]
                    self.replicateToLocation[replicate - 1] = \
                        (previousRange[0], currentPos - 1)
                self.replicateToLocation[replicate] = (currentPos, -1)

                # determine count of each replicate
                self.replicateToCount[replicate] = \
                    self.countVariationInMatrix(nexusFile, self.verbose)

                if replicate == 0:
                    # determine the last character in the header
                    self._startByte = currentPos - 1

                replicate += 1
            currentPos = nexusFile.tell()
            line = nexusFile.readline()

        previousRange = self.replicateToLocation[replicate - 1]
        self.replicateToLocation[replicate - 1] = \
            (previousRange[0], nexusFile.tell() - 1)

    def write(self, nexusFile):
        """
        Rewrite a nexus formatted file according to the variation of columns.

        Args:
           newNexusFile: An open (write) nexus file. File will have the same
               content as origNexusFile, but reordered by number of variable
               columns. Each locus will also have a comment indicating number.

        """
        assert self.inFile != None, 'Read must occur before write.'
        assert not self.inFile.closed, 'File used for read must not be closed.'

        # sort (replicate, count) into a list from most counts to least
        sorted_counts = sorted(self.replicateToCount.iteritems(),
                               key=operator.itemgetter(1), reverse=True)

        # write the header of the original nexus file
        self.inFile.seek(0)
        nexusFile.write(self.inFile.read(self._startByte))

        # write slices of original nexus file in order of count
        for count in sorted_counts:
            start, stop = self.replicateToLocation[count[0]]

            # add commenting to nexus file to display number of
            # variable sites in each matrix
            comment = '\n[Variable Sites: {0}]'.format(count[1])
            nexusFile.write(comment)
            self.inFile.seek(start - 1)
            nexusFile.write(self.inFile.read(stop - start + 1))

        # write one last character from the final matrix
        nexusFile.write(self.inFile.read(1))

    def countVariationInMatrix(self, nexusFile, verbose=False):
        """ Counts the number of columns with variation.

        Reads from a file, starting at a line with the keywords 'begin' ,'data.
        Parses lines of matrix for nucleotide sequences (ATGC). Counts each
        column with more than one nucleotide. Stops reading when ';' is
        reached. Note: Each sequence must have the same length.

        Args:
           nexusFile: An open nexus file positioned with current line
               containing 'matrix' keyword.

        Returns:
            An integer count of the number of columns with more than one
            nucleotide.
        """
        # read until matrix keyword
        line = nexusFile.readline()
        while line.lower().strip() != 'matrix':
            line = nexusFile.readline()

        seqs = []
        # parse to find sequence string
        line = nexusFile.readline()
        while line:
            if verbose:
                print line
            parts = line.strip().split()
            if len(parts) >= 2:
                seqs.append(parts[1])
            if ';' in line:
                break
            line = nexusFile.readline()

        if verbose:
            print 'seqs:\n', seqs

        numDifferent = 0
        # compare each column of each sequence string
        for i in range(len(seqs[0])):
            seen = seqs[0][i]
            for j in seqs:
                if j[i] != seen:
                    numDifferent += 1
                    break

        if verbose:
            print 'numDifferent', numDifferent
        return numDifferent


def main(): # IGNORE:C0111
    # Setup argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', type=argparse.FileType('rb'),
                        help='input file')
    parser.add_argument('outfile', type=argparse.FileType('w'),
                        help='output file')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='include verbose messages')

    # Process arguments
    args = parser.parse_args()

    inFile = args.infile
    outFile = args.outfile
    verbose = args.verbose

    rvf = RepVariationFinder(verbose)
    rvf.read(inFile)
    rvf.write(outFile)

if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-v")
    main()
