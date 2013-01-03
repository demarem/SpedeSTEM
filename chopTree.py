class ChopTree:
    def __init__(self, origFilename, newFilename='genetrees.tre', maxNumTrees=20, numTrees=5):
        self.linePointer = 0
        self.maxNumTrees = maxNumTrees
        self.numTrees = numTrees
        self.origTreeFile = open(origFilename, "r")
        self.newFilename = newFilename

    def chopTree(self):
        # get to the correct line in origTreefile
        for i in range(self.linePointer):
            self.origTreeFile.readline()

        treeFile = open(self.newFilename, "w")
        for i in range(self.numTrees):
            treeFile.write(self.origTreeFile.readline())
        treeFile.close()

        self.linePointer += self.maxNumTrees - self.numTrees

    def __del__(self):
        self.origTreeFile.close()

if __name__ == '__main__':

    # testing
    testMaster = open('testMaster', 'w')
    testMaster.write('1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n12\n13\n14\n15\n16\n17' + \
                   '\n18\n19\n20\n21\n22\n23\n24\n25\n26\n27\n28\n29\n30\n31' + \
                   '\n32\n33\n34\n35\n36\n37\n38\n39\n40\n41\n42\n43\n44\n45' + \
                   '\n46\n47\n48\n49\n50\n')
    testMaster.close()
    for x in [5, 10, 15]:
        ct = ChopTree('testMaster', "testOut", 15, x)
        for w in range(2):
            print 'numTrees = ', x, ' & chopNumber = ', w + 1
            ct.chopTree()
            readTest = open('testOut', 'r')
            for line in readTest:
                print line.strip()
