
# TODO: save settings

import re
import StringIO
import subprocess

def debug(message):
    print str(message)

class stemTree:
    def __init__(self, settings):
        self.speciesToAlleles = {}  # persistent list of species
        self.settingsHeader = ""  # set first time settings is read
        self.numSpecies = 0  # for current epoch

        # build dict the first time, don't need this any other time
        settingsFile = open(settings, 'r')
        self.buildSpeciesDict(settingsFile)
        settingsFile.close()

    def buildSpeciesDict(self, settingsFile):
        ''' creates a dictionary of the form [species] : [list_of_alleles]
        from settings file'''

        if self.settingsHeader == '':  # settings header not yet set
            line = settingsFile.readline()
            while line.strip() != "species:":
                self.settingsHeader = self.settingsHeader + line
                line = settingsFile.readline()
            self.settingsHeader = self.settingsHeader + line
        else:  # settings header already set, ignore it
            while settingsFile.readline().strip() != "species:":
                pass  # do nothings

        # build dict for sp : alleles part of settings
        numSpecies = 0
        for line in settingsFile:
            line = line.strip()
            if len(line) > 0:
                parts = line.split(':')
                sp = parts[0]
                alleles = parts[1]
                sp = sp.strip()
                alleles = alleles.strip()
                self.speciesToAlleles[sp] = alleles
            numSpecies += 1

        # set numSpecies for this epoch
        self.numSpecies = numSpecies
        debug("number of species: " + str(numSpecies))

    def findMinSisters(self, tree):
        # get a list of the sisters in tree
        sisterFinder = r"\([^()]*\)"
        sisters = re.findall(sisterFinder, tree)

        # capture the three parts of each sister, groups(1-3): al1, weight, al2
        parseSister = r"\((.+):(\d*.\d+),(.*):.*\)"
        m = re.match(parseSister, sisters[0])
        minWeight = float(m.group(2))
        minSisters = (m.group(1), m.group(3))
        for sis in sisters:
            m = re.match(parseSister, sis)
            testWeight = float(m.group(2))
            if testWeight < minWeight:
                minSisters = (m.group(1), m.group(3))

        debug(minSisters)
        return minSisters

    def updateSpeciesDict(self, minSisters):
        # sisters to be combined
        sis_1 = minSisters[0]
        sis_2 = minSisters[1]

        # alleles to be combined
        alleles_1 = self.speciesToAlleles[sis_1]
        alleles_2 = self.speciesToAlleles[sis_2]

        # make new species with both species and both sets of alleles
        self.speciesToAlleles[minSisters[0] + minSisters[1]] = \
            alleles_1 + ", " + alleles_2

        debug("Added new combined species: " + str(self.speciesToAlleles))

        # delete both old species
        del self.speciesToAlleles[sis_1]
        del self.speciesToAlleles[sis_2]

        debug("Removed old species: " + str(self.speciesToAlleles))

        self.numSpecies = len(self.speciesToAlleles)
        debug("number of species: " + str(self.numSpecies))

    def captureTreeAndAppendResults(self, outputStr, resultsFile):
        logLikelihood = ""
        treeLine = ""
        buf = StringIO.StringIO(outputStr)
        resultsFile.write(str(self.numSpecies - 1))
        line = buf.readline()
        while line:
            if "Species Tree" in line:
                line = buf.readline()
                treeLine = buf.readline().strip()
                treeLine = treeLine.replace(';', '')
                resultsFile.write("; " + treeLine + "; ")

            elif "log likelihood" in line:
                logLikelihood = line.split(":")[1].strip()
                resultsFile.write(logLikelihood + "\n")
                break
            line = buf.readline()

        return treeLine

    def printSettings(self, settingsFile):
        settingsFile.write(self.settingsHeader)
        for sp in self.speciesToAlleles:
            settingsFile.write('  ' + sp + ': ' + self.speciesToAlleles[sp] + '\n')

    def doOneStep(self, settings, jarFile, results):
        ''' mutates self.speciesToAlleles '''

        # call java
        output = subprocess.check_output(["java", "-jar", jarFile])
        debug(output)

        # find tree and print the results of the last run
        resultsFile = open(results, 'a')
        tree = self.captureTreeAndAppendResults(output, resultsFile)
        resultsFile.close()

        # determine the two sister species to collapse
        minSisters = self.findMinSisters(tree)

        # use the two sister species to collapse the species in dict
        self.updateSpeciesDict(minSisters)

        # print the new settings file
        settingsFile = open(settings, 'w')
        self.printSettings(settingsFile)
        settingsFile.close()

        return self.numSpecies

    def doMaxSteps(self, settings, jarFile, results):
        ''' mutates self.speciesToAlleles '''

        numRemaining = self.doOneStep(settings, jarFile, results)
        while numRemaining > 1:
            numRemaining = self.doOneStep(settings, jarFile, results)

if __name__ == '__main__':
    stepper = stemTree('settings')
    stepper.doMaxSteps('settings', 'stem.jar', 'results')
