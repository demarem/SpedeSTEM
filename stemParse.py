import sys, StringIO

class StemParse:
    def __init__ (self, allelesName='settings', groupsName=None):
        self.groups = {}
        self.alleles = {}
        self.header = ""
        self.popToAlleles = {}
        self.currentLikelihood = ''
        self.currentTree = ''

        allelesFile = open(allelesName, "r")
        self.getHeader(allelesFile)
        self.getSettings(allelesFile, self.alleles)
        allelesFile.close()

        if groupsName:
            groupsFile = open(groupsName, "r")
            self.getSettings(groupsFile, self.groups)
            groupsFile.close()

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

    def generateSettings(self, popToAlleles, settings='settings'):
        ''' 
        Writes the settings file with popToAlleles in the form of str to str.
        '''
        settingsFile = open(settings, 'w')
        settingsFile.write(self.header)
        for name in popToAlleles.keys() :
            settingsFile.write(name + ": " + popToAlleles[name] + "\n")
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
                self.currentLiklihood = line.split(":")[1].strip()
                break
            line = buf.readline()

        # throw exception if tree or likelihood were not found
        if self.currentLikelihood == '' or self.currentTree == '':
            raise IOError("ParseError")

