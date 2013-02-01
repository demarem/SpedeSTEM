import sys, StringIO, os
import re

class StemParse:
    def __init__ (self, allelesName='settings', groupsName=None):
        self.groups = {}
        self.alleles = {}
        self.header = ""
        self.currentLikelihood = ''
        self.currentTree = ''

        allelesFile = open(allelesName, "r")
        self.getHeader(allelesFile)
        self.getSettings(allelesFile, self.alleles)
        allelesFile.close()

        if groupsName:
            try:
                groupsFile = open(groupsName, "r")
                self.getSettings(groupsFile, self.groups)
                groupsFile.close()
            except IOError:
                print "ERROR: Could not open associations file '" + groupsName + "'"
                sys.exit()

            # check that species from both files match up
            # determine all species from both files
            groupSpecies = []
            alleleSpecies = []
            for group in self.groups:
                species = re.split(r"\s*,\s*", self.groups[group])
                for sp in species:
                    groupSpecies.append(sp)

            for species in self.alleles:
                alleleSpecies.append(species)

            # check if every species in associations is in settings
            for sp in groupSpecies:
                if sp not in alleleSpecies:
                    print "\nASSOCIATIONS ERROR: Species '" + sp + "' was found in associations file but not in settings file"
                    sys.exit()

            # check if every species in settings is in associations
            for sp in alleleSpecies:
                if sp not in groupSpecies:
                    print "\nASSOCIATIONS ERROR: Species '" + sp + "' was found in settings file but not in associations file"
                    sys.exit()



    def getHeader(self, groupsFile):
        line = groupsFile.readline()
        while line.strip() not in {"species:", ""}:
            self.header += line
            line = groupsFile.readline()
        if line.strip() == "":
            raise sys.exit("ERROR: Expected 'species:' before list.")
        self.header += line

    def getSettings(self, settingsFile, newDict):
        for line in settingsFile:
            splits = line.split(":")
            key = splits[0].strip()
            values = splits[1].strip()
            newDict[key] = values

    def buildHeader(self, theta):
        self.header = "properties:\n" + \
                        "    run: 1\t\t\t#0=user-tree, 1=MLE, 2=search\n" + \
                        "    theta: " + str(theta) + "\n" + \
                        "    num_saved_trees: 15\n" + \
                        "    beta: 0.0005\n" + \
                        "species:"

    def generateSettings(self, popToAlleles, settings='settings'):
        ''' 
        Writes the settings file with popToAlleles in the form of str to str.
        '''
        settingsFile = open(settings, 'w')
        settingsFile.write(self.header)
        for name in popToAlleles.keys() :
            settingsFile.write("\t" + name + ": " + popToAlleles[name] + "\n")
        settingsFile.close()

        self.currentLikelihood = ''
        self.currentTree = ''

    def parseOutput(self, output):
        buf = StringIO.StringIO(output)
        line = buf.readline()
        while line:
            if "Species Tree" in line:
                line = buf.readline()
                treeLine = buf.readline().strip()
                self.currentTree = treeLine.replace(';', '')

            elif "log likelihood" in line:
                self.currentLikelihood = line.split(":")[1].strip()
                break
            line = buf.readline()

        # remove superfluous
        os.remove('mle.tre')
        os.remove('boot.tre')

