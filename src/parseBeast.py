import shutil

class ParseBeast:
    def __init__ (self, settings='settings', theta=1.0):
        self.speciesToTraits = {}
        self.header = ''

        settingsFile = open(settings, "r")
        self.getSettings(settingsFile)
        self.buildHeader(theta)
        shutil.copy(settings, settings + '.save')
        self.generateSettings(self.speciesToTraits, settings)
        settingsFile.close()

    def getSettings(self, settingsFile):
        ''' format is "traits    species" '''
        settingsFile.readline()
        for line in settingsFile:
            splits = line.split("\t")
            species = splits[1].strip()
            if self.speciesToTraits.has_key(species):
                updatedTraits = self.speciesToTraits[species] + [splits[0].strip()]
                self.speciesToTraits[species] = updatedTraits
            else:
                self.speciesToTraits[species] = [splits[0].strip()]

    def buildHeader(self, theta):
        self.header = "properties:\n" + \
                        "    run: 1\t\t\t#0=user-tree, 1=MLE, 2=search\n" + \
                        "    theta: " + str(theta) + "\n" + \
                        "    num_saved_trees: 15\n" + \
                        "    beta: 0.0005\n" + \
                        "species:\n"

    def generateSettings(self, speciesToTraits, settings='settings'):
        ''' 
        Writes the settings file with speciesToTraits in the form of str to str.
        '''
        settingsFile = open(settings, 'w')
        settingsFile.write(self.header)
        for name in speciesToTraits.keys() :
            settingsFile.write("\t" + name + ": ")
            counter = 1
            for trait in speciesToTraits[name]:
                if counter < len(speciesToTraits[name]):
                    settingsFile.write(trait + ", ")
                else:
                    settingsFile.write(trait + "\n")
                counter += 1
        settingsFile.close()

if __name__ == "__main__":
    tester = ParseBeast(theta=2.0)
    print tester.speciesToTraits

