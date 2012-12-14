'''
Description: Stem step-up speciation processor
Created on Dec 13, 2012

HOW TO RUN: in same directory, include: trees, settings
WILL CREATE: results, trees.orig, settings.orig
'''

import shutil
import subprocess

def debug(message):
    print message

class StepUp:
    def __init__(self, origTreeFile=None, numTrees=None, numRuns=1):
        self.speciesToAlleles = {}
        self.intToSpecies = {}  # enum of int to species
        self.settingsHeader = ""  # set first time settings is read
        self.numSpecies = 0  # for current epoch
        self.treeFile = origTreeFile  # extract numTrees from this file
        self.numTrees = numTrees
        self.treeLine = 0  # line in original tree file
        self.output = ''
        self.numRuns = numRuns

    def buildSpeciesDictAndList(self, file):
        ''' creates a dictionary of the form [species] : [list_of_alleles] and
        dict of int to species for enumeration list from 'settings' file '''

        if self.settingsHeader == '':  # settings header not yet set
            line = file.readline()
            while line.strip() != "species:":
                self.settingsHeader = self.settingsHeader + line
                line = file.readline()
            self.settingsHeader = self.settingsHeader + line
        else:  # settings header already set, ignore it
            while file.readline().strip() != "species:":
                pass  # do nothings

        # build both dicts
        numSpecies = 0
        for line in file:
            line = line.strip()
            if len(line) > 0:
                parts = line.split(':')
                sp = parts[0]
                alleles = parts[1]
                sp = sp.strip()
                alleles = alleles.strip()
                self.speciesToAlleles[sp] = alleles
                self.intToSpecies[numSpecies] = sp
            numSpecies += 1

        # set numSpecies for this epoch
        self.numSpecies = len(self.intToSpecies)


    def makeSpeciesGroups(self, speciesToCombine):
        ''' creates a list of sets for each collapsed species '''

        groups = []
        groups.append(set(speciesToCombine[0]))  # add first sp to first group
        for x, y in speciesToCombine:
            foundXGroup = -1
            foundYGroup = -1
            for i in range(len(groups)):
                if x in groups[i]:
                    foundXGroup = i
                    groups[i].add(y)
                elif y in groups[i]:
                    foundYGroup = i
                    groups[i].add(x)
                else:
                    groups.append(set(x, y))

            # combine if a common pair spans two groups (transitive)
            if foundXGroup != -1 and foundYGroup != -1:
                groups[foundXGroup] += groups[foundYGroup]
                del groups[foundYGroup]

        return groups


    def updateSpeciesDictAndList(self, groups):
        for group in groups:
            newName = ""
            newAlleles = ""
            for member in group:
                # build new name
                oldName = self.intToSpecies[member]
                if newName == "":
                    newName = oldName
                else:
                    newName = newName + '_' + oldName
                if len(newAlleles) == 0:
                    newAlleles = self.speciesToAlleles[oldName]
                else:
                    newAlleles = newAlleles + ", " + self.speciesToAlleles[oldName]
                self.speciesToAlleles.pop(oldName)
            self.speciesToAlleles[newName] = newAlleles


    def parseMatrix(self, file):
        strMatrix = []
        numSpecies = 0
        # process output into a list of strings
        for line in file:
            line = line.strip()
            if len(line) > 0 and line[0] == '[':
                numSpecies += 1  # count the number of species
                matrixRow = line.replace('[', ' ')
                matrixRow = matrixRow.replace(']', ' ')
                strMatrix.extend(matrixRow.split(' '))

        dblMatrix = []
        for i in strMatrix:
            if i not in ('', '\n'):
                dblMatrix.append(float(i))

        return dblMatrix, numSpecies


    def findMinElements(self, matrix, numSpecies):
        # find all with min, store in list of tuples
        row = 0
        col = 0
        minFound = matrix[1]
        for x in matrix:
            if col > row and x < minFound:
                minFound = x
            col += 1
            if col > numSpecies - 1:
                col = 0
                row += 1

        row = 0
        col = 0
        species = []
        for x in matrix:
            if x == minFound:  # maybe should be some tolerance
                species.append((row, col))
            col += 1
            if col > numSpecies - 1:
                col = 0
                row += 1

        return species


    def printNewSettings(self, file):
        numSpecies = 0
        self.intToSpecies.clear()
        file.write(self.settingsHeader)
        for sp in self.speciesToAlleles:
            self.intToSpecies[numSpecies] = sp
            numSpecies += 1
            file.write('  ' + sp + ': ' + self.speciesToAlleles[sp] + '\n')


    def doStep(self):
        settings = open('settings', 'r')
        self.buildSpeciesDictAndList(settings)
        settings.close()

        # call java stuff here
        # os.system("java -jar stem.jar > output")
        # os.system("cat output")
        self.output = subprocess.check_output(["java", "-jar", "stem.jar"])
        print self.output

        output = open('output', 'r')
        matrix, numSpecies = self.parseMatrix(output)
        output.close()

        speciesToCombine = self.findMinElements(matrix, numSpecies)

        groups = self.makeSpeciesGroups(speciesToCombine)

        self.updateSpeciesDictAndList(groups)

        newSettings = open('settings', 'w')
        self.printNewSettings(newSettings)
        newSettings.close()

        return len(self.intToSpecies)

    def chopTree(self):
        newTreeFile = open('genetrees.tre', 'w')
        origTreeFile = open('tree', 'r')

        # get to the correct line in 'tree' file
        for i in range(self.treeLine):
            origTreeFile.readline()
        # add the next numTrees lines and put them into genetrees.tre
        for i in range(self.numTrees):
            newTreeFile.write(origTreeFile.readline())

        self.treeLine += self.numTrees
        newTreeFile.close()
        origTreeFile.close()

    def run(self):
        for i in range(self.numRuns):
            self.chopTree()
            numSp = self.doStep()
            while numSp > 2:
                numSp = self.doStep()


if __name__ == '__main__':

    # copy files
    shutil.copyfile("settings", "settings.orig")
    shutil.copyfile("tree", "tree.orig")

    # execute one
    run = StepUp()
    run.run()

