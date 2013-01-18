import sys

class OutputGen:
    def __init__(self, results='results'):
        self.outputFile = open(results, 'w')

    def generateOutput(self, tree, likelihood, numSpecies):
        self.outputFile.write(tree)
        self.outputFile.write("; " + str(numSpecies - 1) + "; ")
        self.outputFile.write(likelihood + "\n")

    def __del__(self):
        self.outputFile.close()

# for now, this will analyze offline, but it could be made to do it online







if __name__ == '__main__':
    # averageOutputTips()
    averageOutputByTrees(203)
