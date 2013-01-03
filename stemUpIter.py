import shutil
import chopTree
import stemUp
import os

class StemUpIter:
    def __init__(self, masterTreeList, numRuns=5, numTrees=5, maxTrees=20, jarFile='stem-hy.jar',
                 origSettings='settings', results='results',
                 log='log'):
        self.numRuns = numRuns
        self.numTrees = numTrees
        self.maxTrees = maxTrees
        self.jarFile = jarFile
        self.settings = origSettings
        self.masterTreeList = masterTreeList
        self.results = results
        self.log = log

        # check values
        assert self.numTrees % self.maxTrees == 0, \
            'maxTrees must be divisible by numTrees'

        # make copy of original settings
        if origSettings == 'settings':
            shutil.copy(origSettings, origSettings + '.save')


        # make sure nothing in masterTreeList is named genetrees.tre
        for i in range(len(self.masterTreeList)):
            tree = self.masterTreeList[i]
            if tree == 'genetrees.tre':
                shutil.copy(tree, tree + '.save')
                self.masterTreeList[i] = tree + '.save'


    def run(self):
        treeSizes = [(x + 1) * self.numTrees for x in range(self.maxTrees / self.numTrees)]
        runCounter = 0
        totalRuns = len(treeSizes) * self.numRuns * len(self.masterTreeList)
        for tree in self.masterTreeList:
            for treeSize in treeSizes:
                print "Sampling %d trees from master tree file" % treeSize
                chopper = chopTree.ChopTree(tree, self.maxTrees, treeSize)
                for run in range(self.numRuns):
                    runCounter += 1

                    chopper.chop()
                    stepper = stemUp.StemUp(self.jarFile, self.log, self.settings, verbose=False)
                    stepper.doMaxSteps()

                    # reset the settings file
                    shutil.copy(self.settings, 'settings')

                    # organize the results
                    oldResults = open('results', 'r')
                    newResults = open(self.results + '.' + tree + '.' + str(treeSize), 'a')
                    for line in oldResults:
                        newResults.write(line)

                    # Print a progress
                    print "Completed %d of %d runs" % (runCounter, totalRuns)

if __name__ == '__main__':
    pass
