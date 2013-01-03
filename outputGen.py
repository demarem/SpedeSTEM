class OutputGen:
    def __init__(self, results='results'):
        self.outputFile = open(results, 'w')

    def generateOutput(self, tree, likelihood, numSpecies):
        self.outputFile.write(str(numSpecies - 1))
        self.outputFile.write("; " + tree + "; ")
        self.outputFile.write(likelihood + "\n")

    def __del__(self):
        self.outputFile.close()
