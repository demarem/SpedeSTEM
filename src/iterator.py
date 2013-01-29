import shutil
import os
import chopTree
import stemUp, stemGroup

class Iterator:
    def __init__(self, masterTreeList, numRuns=5, numTrees=5, maxTrees=20, jarFile='stem-hy.jar',
                 settings='settings.txt', associations='associations.txt', results='results.txt', log='stemOut.txt',
                 isValidation=False, verbose=False):
        self.numRuns = numRuns
        self.numTrees = numTrees
        self.maxTrees = maxTrees
        self.jarFile = jarFile
        self.masterSettings = settings
        self.currentSettings = 'settings'
        self.masterTreeList = masterTreeList
        self.results = results
        self.log = log
        self.associations = associations
        self.isValidation = isValidation
        self.verbose = verbose

        # check values
        if self.numTrees:
            assert self.maxTrees % self.numTrees == 0, \
                'maxTrees must be divisible by numTrees'

        # make copy of original settings if necessary or make 'settings' file
        if settings == 'settings':
            shutil.copy(settings, settings + '.save')
            self.masterSettings = settings + '.save'
        else:
            shutil.copy(settings, self.currentSettings)

        # make sure nothing in masterTreeList is named genetrees.tre
        for i in range(len(self.masterTreeList)):
            trees = self.masterTreeList[i]
            for j in range(len(trees)):
                tree = trees[j]
                if tree == 'genetrees.tre':
                    shutil.copy(tree, tree + '.save')
                    self.masterTreeList[i][j] = tree + '.save'

        # remove old stem log if it's present
        if os.path.exists(self.log):
            print "\n--------------------- CAUTION -----------------------"
            print self.log, "is about to be deleted. ", \
                "If you would like to preserve it, remove it from this directory."
            choice = raw_input('Are you ready to continue? (y/n): ')
            if choice.strip() != 'y':
                print '\nExiting...\n'
                exit()
            try:
                os.remove(self.log)
            except OSError:
                pass
            print "-----------------------------------------------------\n"

        # count number of trees if numTrees is None
        if not self.numTrees:
            treeFile = open(self.masterTreeList[0][0])
            numLines = 0
            for line in treeFile:
                if line.strip() != '':
                    numLines += 1
            self.numTrees = numLines
            self.maxTrees = numLines


    def printSettings(self):
        print '--------------------- SETTINGS ----------------------'
        print "In Varification Mode: ", self.isValidation
        print "Tree File(s): ", self.masterTreeList
        print "Settings File: ", self.masterSettings
        if self.isValidation:
            print "Associations File: ", self.associations
        print "Number of trees sampled each run: ", self.numTrees
        print "Number of runs: ", self.numRuns
        print "In Verbose Mode: ", self.verbose
        print '-------------------- END SETTINGS --------------------\n'

    def run(self):
        print '--------------------- EXECUTION ----------------------'
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

                    if self.isValidation:
                        varifier = stemGroup.StemGroup(self.currentSettings, \
                                                       self.associations, self.jarFile, \
                                                       self.log, verbose=self.verbose)
                        varifier.run()
                    else:
                        stepper = stemUp.StemUp(self.jarFile, self.log, self.currentSettings, verbose=self.verbose)
                        stepper.doMaxSteps()


                    # reset the settings file
                    shutil.copy(self.masterSettings, self.currentSettings)

                    # Print progress
                    print "\tCompleted %d of %d runs..." % (runCounter, totalRuns)
        print '\n+++++++++++++++ All analysis completed! +++++++++++++++\n'

if __name__ == '__main__':
    tester = Iterator(\
                        [['cleaned.cpDNA.sub.1.tre', \
                        'cleaned.Sa4.sub.1.tre', \
                        'cleaned.Sa135.sub.1.tre', \
                        'cleaned.Sa144.sub.1.tre', \
                        'cleaned.Sa297.sub.1.tre', \
                        'cleaned.Sa302.sub.1.tre', \
                        'cleaned.Sa323.sub.1.tre', \
                        'cleaned.Sa405.sub.1.tre']], \
                        numRuns=100, numTrees=1, maxTrees=1, isVarification=True)
    tester.run()
