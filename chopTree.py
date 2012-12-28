class ChopTree:
    def __init__(self, origFilename, newFilename, maxNumTrees=5):
        self.linePointer = 0
        self.numRuns = 0
        self.maxNumTrees = maxNumTrees
        self.newFilename = newFilename
        # self.openFiles(origFilename, newFilename)

    def openFiles(self, origFilename, newFilename="genetrees.tre"):
        self.origTreeFile = open(origFilename, "r")
        self.newTreeFile = open(newFilename, "a")

    def check(self):
        # print self.numRuns, self.maxNumRuns
        if self.numTrees >= self.maxNumTrees :
            self.reset()

    def chopTree(self, numTrees=5):
        self.check()

        # get to the correct line in origTreefile
        for i in range(self.linePointer):
            self.origTreeFile.readline()

        for i in range(numTrees):
            self.newTreeFile.write(self.origTreeFile.readline())

        self.adjust(numTrees)

    def adjust(self, numTrees):
        self.linePointer += numTrees
        self.numTrees += numTrees

    def reset(self):
        self.newTreeFile.close()
        open(self.newFilename, 'w').close()
        self.newTreeFile = open(self.newFilename, "a")
        self.numRuns = 0

    def finish(self):
        self.origTreeFile.close()
        self.newTreeFile.close()



if __name__ == '__main__':
    ct = ChopTree("origTree", "newTree", 10)
    ct.reset()
    for i in range(12):
        ct.chopTree(20)
    ct.finish()
