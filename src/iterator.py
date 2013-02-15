import shutil
import os, sys
import chopTree
import stemUp, stemGroup

class Iterator:
    def __init__(self, masterTreeList, numRuns=5, numTrees=5, maxTrees=20, jarFile='stem-hy.jar',
                 settings='settings.txt', associations='associations.txt', results='results.txt', log='stemOut.txt',
                 isValidation=False, verbose=False, quietWarnings=False):
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
        try:
            if settings == 'settings':
                shutil.copy(settings, settings + '.save')
                self.masterSettings = settings + '.save'
            else:
                shutil.copy(settings, self.currentSettings)
        except IOError:
                print "ERROR: Settings file '" + settings + "' not found"
                sys.exit()

        # make sure nothing in masterTreeList is named genetrees.tre
        for i in range(len(self.masterTreeList)):
            trees = self.masterTreeList[i]
            for j in range(len(trees)):
                tree = trees[j]
                if tree == 'genetrees.tre':
                    try:
                        shutil.copy(tree, tree + '.save')
                        self.masterTreeList[i][j] = tree + '.save'
                    except IOError:
                        print "ERROR: Tree file '" + tree + "' not found"
                        sys.exit()

        # remove old stem log if it's present
        if os.path.exists(self.log) and not quietWarnings:
            print "\n--------------------- CAUTION -----------------------"
            print "Log file '" + self.log + "' is about to be deleted. ", \
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

        if os.path.exists(self.log) and quietWarnings:
            try:
                os.remove(self.log)
                print self.log + " was quietly removed.\n"
            except OSError:
                pass

        # count number of trees if numTrees is None
        if not self.numTrees:
            try:
                treeFile = open(self.masterTreeList[0][0])
            except IOError:
                print "ERROR: Tree File '" + self.masterTreeList[0][0] + "' not found."
                sys.exit()
            numLines = 0
            for line in treeFile:
                if line.strip() != '':
                    numLines += 1
            self.numTrees = numLines
            self.maxTrees = numLines


    def printSettings(self):
        print '--------------------- SETTINGS ----------------------'
        print "In Varification Mode: ", self.isValidation
        print "Tree File: ", self.masterTreeList
        print "Settings File: ", self.masterSettings
        print "Associations File: ", self.associations
        print "Number of loci sampled each replicate: ", self.numTrees
        print "Number of replicates: ", self.numRuns
        print "In Verbose Mode: ", self.verbose
        print '-------------------- END SETTINGS --------------------\n'

    def run(self):
        print '--------------------- EXECUTION ----------------------'
        treeSizes = [(x + 1) * self.numTrees for x in range(self.maxTrees / self.numTrees)]
        runCounter = 0
        totalRuns = len(treeSizes) * self.numRuns * len(self.masterTreeList)
        for tree in self.masterTreeList:
            for treeSize in treeSizes:
                print "Sampling %d loci from master tree file %s..." % (treeSize, tree[0])
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
                    try:
                        shutil.copy(self.masterSettings, self.currentSettings)
                    except IOError:
                        print "ERROR: Settings file '" + self.masterSettings + "' could not be found"
                        sys.exit()

                    # Print progress
                    print "\tCompleted %d of %d replicates..." % (runCounter, totalRuns)
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
