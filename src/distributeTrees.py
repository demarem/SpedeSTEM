import os

class DistributeTrees:
    def __init__(self, cleanedTreeList, numOutputFiles=None, prefix=None):

        if prefix == None:
            prefix = ""
        else:
            prefix = prefix + "."

        self.cleanedTreeList = cleanedTreeList
        self.distributeTrees(prefix, numOutputFiles)

    def distributeTrees(self, prefix, numOutputTrees=None):
        sourceTreeFiles = []
        destTreeFiles = []

        for trees in self.cleanedTreeList:
            sourceTreeFiles.append(open(trees, 'r'))

        if numOutputTrees == None:
            numOutputTrees = -1
        stillReading = True

        counter = 1
        while stillReading and numOutputTrees:
            newTreeFile = open(prefix + "replicateTree_" + str(counter) + ".tre", 'w')
            destTreeFiles.append(newTreeFile)

            for treeFile in sourceTreeFiles:
                line = treeFile.readline()
                if not line:
                    stillReading = False
                    newTreeFile.close()
                    os.remove(newTreeFile.name)
                    break
                else:
                    newTreeFile.write(line)
            numOutputTrees -= 1
            counter += 1

        for f in destTreeFiles:
            f.close()

if __name__ == "__main__":
    import cleanTrees
    cleanTrees.CleanTrees(["Sa135.tre", "Sa163.tre", "Sa297.tre",
                                     "Sa302.tre", "Sa323.tre", "Sa4.tre",
                                     "Sa405.tre", "cpDNA.tre"], "rubrscale.txt")
    DistributeTrees(["cleaned.Sa135.tre", "cleaned.Sa163.tre", "cleaned.Sa297.tre",
                            "cleaned.Sa302.tre", "cleaned.Sa323.tre", "cleaned.Sa4.tre",
                            "cleaned.Sa405.tre", "cleaned.cpDNA.tre"])
