'''
Description: Stem step-up speciation processor
Created on Dec 13, 2012
'''

import os
import shutil
import re

def debug(message):
    print message

class StepUp:
    def __init__(self):
        self.speciesToAlleles = {}
        self.intToSpecies = {}  # enum of int to species
        self.settingsHeader = ""



    def buildSpeciesDictAndList(self, file):
        ''' creates a dictionary of the form [species] : [list_of_alleles] '''

        if self.settingsHeader == '':
            line = file.readline()
            while line.strip() != "species:":
                self.settingsHeader = self.settingsHeader + line
                line = file.readline()
            self.settingsHeader = self.settingsHeader + line
        else:
            while file.readline().strip() != "species:":
                None  # do nothings

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

    def makeSpeciesGroups(self, speciesToCombine):
        groups = []
        groups.append(set(speciesToCombine[0]))
        for x, y in speciesToCombine:
            for i in range(len(groups)):
                if x in groups[i]:
                    groups[i].add(y)
                elif y in groups[i]:
                    groups[i].add(x)
                else:
                    groups.append(set(x, y))

        # TODO: might need to look through the groups to verify that they don't share common
        # members
        return groups


    def updateSpeciesDictAndList(self, groups):
        for group in groups:
            newName = ""
            newAlleles = ""
            for member in group:
                # build new name
                oldName = self.intToSpecies[member]
                newName = newName + oldName
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
        print self.intToSpecies
        print self.speciesToAlleles
        print self.settingsHeader

    def step(self):
        settings = open('settings', 'r')
        self.buildSpeciesDictAndList(settings)
        settings.close()

        # call java stuff here
        os.system("java -jar stem.jar > output")
        os.system("cat output")

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


if __name__ == '__main__':

    # copy file to preserve settings
    shutil.copyfile("settings", "settings.orig")

    # execute once
    run = StepUp()

    run.step()
    run.step()
    run.step()

#    numSp = run.stepUp()
#    while numSp > 2:
#        numSp = run.stepUp()

