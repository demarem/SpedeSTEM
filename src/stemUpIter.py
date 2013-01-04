import shutil
import chopTree
import stemUp

class StemUpIter:
    def __init__(self, masterTreeList, numRuns=5, numTrees=5, maxTrees=20, jarFile='stem-hy.jar',
                 settings='settings', results='results',
                 log='log'):
        self.numRuns = numRuns
        self.numTrees = numTrees
        self.maxTrees = maxTrees
        self.jarFile = jarFile
        self.masterSettings = settings
        self.currentSettings = settings
        self.masterTreeList = masterTreeList
        self.results = results
        self.log = log

        # check values
        assert self.maxTrees % self.numTrees == 0, \
            'maxTrees must be divisible by numTrees'

        # make copy of original settings
        if settings == 'settings':
            shutil.copy(settings, settings + '.save')
            self.masterSettings = settings + '.save'

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
                print "Sampling %d trees from master tree file %s..." % (treeSize, tree)
                chopper = chopTree.ChopTree(tree, maxNumTrees=self.maxTrees, numTrees=treeSize)
                for run in range(self.numRuns):
                    runCounter += 1

                    chopper.chop()
                    stepper = stemUp.StemUp(self.jarFile, self.log, self.currentSettings, verbose=False)
                    stepper.doMaxSteps()

                    # reset the settings file
                    shutil.copy(self.masterSettings, self.currentSettings)

                    # organize the results
                    oldResults = open('results', 'r')
                    newResults = open(self.results + '.' + tree + '.' + str(treeSize), 'a')
                    for line in oldResults:
                        newResults.write(line)

                    # Print a progress
                    print "Completed %d of %d runs..." % (runCounter, totalRuns)
        print 'All runs completed'

if __name__ == '__main__':
    tester = StemUpIter(['cleaned.shallow.tre', 'cleaned.med.tre', 'cleaned.deep.tre'])
    tester.run()
