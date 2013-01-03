import stem
import shutil
import choptree

class Tester:
    def __init__(self):
        pass
    def maxStepOnNTrees(self, settings='settings', jarFile='stem.jar',
                    results='results', origTree='genetree.tre', numTrees=None):

        if origTree == 'genetree.tree':
            shutil.copyfile(origTree, origTree + '.orig')
            self.ct.openFiles(origTree + '.orig')
        else:
            self.ct.openFiles(origTree)

        self.ct.chopTree(numTrees)
        self.ct.finish()

        self.doMaxSteps(settings, jarFile, results)

    def run(self, settings='settings', jarFile='stem.jar', results='results', \
                    origTree='genetrees.tre', numTrees=None, numTimes=1):
        self.ct = chopTree.ChopTree(origTree, "genetrees.tre", maxNumTrees=20)
        for completeStepUp in range(numTimes):
            debug("Run Number: " + str(completeStepUp))
            self.maxStepOnNTrees(settings, jarFile, results, origTree, numTrees)
            self.reset()
        self.ct.reset()


    def test(self, settings='settings', jarFile='stem.jar', results='results', \
                    listOrigTrees=None, listNumTrees=None, numTimes=1):
        for tree in listOrigTrees:
            for x in listNumTrees:
                if x == None:
                    num = 'all'
                else:
                    num = x
                debug("Tree File: " + tree)
                debug("Number of Trees: " + str(num))
                runOnce = stemTree(settings)
                runOnce.run(settings, jarFile, \
                         results=results + '.' + tree + '.' + str(num), \
                         origTree=tree, numTrees=x, numTimes=numTimes)
                shutil.copy('output', 'output.' + tree + '.' + str(num))
                os.remove('output')
                del runOnce
