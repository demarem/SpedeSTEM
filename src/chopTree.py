class ChopTree:
    def __init__(self, origFilenames, newFilename='genetrees.tre', maxNumTrees=20, numTrees=5):
        self.linePointer = 0
        self.maxNumTrees = maxNumTrees
        self.numTrees = numTrees
        self.origTreeFiles = []
        for f in origFilenames:
            self.origTreeFiles.append(open(f, 'r'))
        self.newFilename = newFilename

    def chop(self):
        # open new treefile
        treeFile = open(self.newFilename, 'w')

        # get to the correct line in origTreefile
        for f in self.origTreeFiles:
            for i in range(self.linePointer):
                f.readline()

            for i in range(self.numTrees):
                treeFile.write(f.readline())
        treeFile.close()

        self.linePointer += self.maxNumTrees - self.numTrees


    def __del__(self):
        for f in self.origTreeFiles:
            f.close()

def test1():
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
            ct.chop()
            readTest = open('testOut', 'r')
            for line in readTest:
                print line.strip()

def test2():
    testMaster1 = open('testMaster1', 'w')
    testMaster1.write('1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n12\n13\n14\n15\n16\n17' + \
                   '\n18\n19\n20\n21\n22\n23\n24\n25\n26\n27\n28\n29\n30\n31' + \
                   '\n32\n33\n34\n35\n36\n37\n38\n39\n40\n41\n42\n43\n44\n45' + \
                   '\n46\n47\n48\n49\n50\n')
    testMaster2 = open('testMaster2', 'w')
    testMaster2.write('1a\n2a\n3a\n4a\n5a\n6a\n7a\n8a\n9a\n10a\n11a\n12a\n13a\n14a\n15a\n16\n17' + \
                   '\n18\n19\n20\n21\n22\n23\n24\n25\n26\n27\n28\n29\n30\n31' + \
                   '\n32\n33\n34\n35\n36\n37\n38\n39\n40\n41\n42\n43\n44\n45' + \
                   '\n46\n47\n48\n49\n50\n')
    testMaster1.close()
    testMaster2.close()
    ct = ChopTree(['testMaster1', 'testMaster2'], "testOut", 1, 1)
    for i in range(100):
        ct.chop()
        readTest = open('testOut', 'r')
        for line in readTest:
            print line.strip()

if __name__ == '__main__':
    test2()
