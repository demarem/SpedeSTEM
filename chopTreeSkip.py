class ChopTree:
    def __init__(self, origFilename, newFilename, maxNumTrees=5):
        self.linePointer = 0
        self.maxNumTrees = maxNumTrees
        self.newFilename = newFilename
        self.origFilename = origFilename

    def openFiles(self, origFilename, newFilename="genetrees.tre"):
        self.origTreeFile = open(origFilename, "r")
        self.newTreeFile = open(newFilename, "w")

    def chopTree(self, numTrees=5):
        # get to the correct line in origTreefile
        for i in range(self.linePointer):
            self.origTreeFile.readline()

        for i in range(numTrees):
            self.newTreeFile.write(self.origTreeFile.readline())

        self.adjust()

    def adjust(self):
        self.linePointer += self.maxNumTrees 

    def reset(self):
        self.newTreeFile.close()
        open(self.newFilename, 'w').close()
        self.newTreeFile = open(self.newFilename, "a")
        self.curNumTrees = 0

    def finish(self):
        self.origTreeFile.close()
        self.newTreeFile.close()

if __name__ == '__main__':
    ct = ChopTree("countTree", "newTree", 20)
    ct.openFiles('countTree', "newTree") 
    for i in range(3):
        ct.chopTree(5)
    ct.finish()
