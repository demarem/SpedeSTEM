import re
import subprocess
import src.stemParse as stemParse
import sys

def debug(message, verbose):
    if verbose:
        print str(message)

class StemUp:
    def __init__(self, jarFile='stem.jar', log='log', settings='settings', verbose=True):
        self.jarFile = jarFile
        self.verbose = verbose
        self.logFile = open(log, 'a')

        # parse setting the first time
        self.parser = stemParse.StemParse(settings)
        self.speciesToAlleles = self.parser.alleles
        self.numSpecies = len(self.speciesToAlleles)

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

        debug("minSisters: " + str(minSisters), self.verbose)
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

        debug("Added new combined species: " + str(self.speciesToAlleles), self.verbose)

        # delete both old species
        del self.speciesToAlleles[sis_1]
        del self.speciesToAlleles[sis_2]

        debug("Removed old species: " + str(self.speciesToAlleles), self.verbose)

        self.numSpecies = len(self.speciesToAlleles)
        debug("number of species: " + str(self.numSpecies), self.verbose)


    def doOneStep(self):
        ''' mutates self.speciesToAlleles '''

        # call java
        try:
            output = subprocess.check_output(["java", "-jar", self.jarFile])
            self.logFile.write(output)
            debug(output, self.verbose)
        except subprocess.CalledProcessError, e:
            print e.output
            self.logFile.write(e.output)
            debug(e.output, self.verbose)
            print "-------STEM ERROR------"
            print "STEM calculation failed. Last STEM message has been printed above and logged in 'stemOut.txt'"
            sys.exit()


        # pass output to parser for new tree and likelihood
        self.parser.parseOutput(output)
        tree = self.parser.currentTree

        # determine the two sister species to collapse
        minSisters = self.findMinSisters(tree)

        # use the two sister species to collapse the species in dict
        self.updateSpeciesDict(minSisters)

        # print the new settings file
        self.parser.generateSettings(self.speciesToAlleles)

        return self.numSpecies

    def doMaxSteps(self):
        ''' mutates self.speciesToAlleles until only one species'''

        numRemaining = self.doOneStep()
        while numRemaining > 1:
            debug("NumberRemaining: " + str(numRemaining), self.verbose)
            numRemaining = self.doOneStep()

if __name__ == '__main__':
    stepper = StemUp(jarFile='stem-hy.jar')
    stepper.doMaxSteps()
