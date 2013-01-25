import re

DIVIDER = r'[\t ]+'
COLUMN_ONE = 'traits'
COLUMN_TWO = 'species'
COLUMN_THREE = 'groups'

class ParseBeast:
    ''' talk about 2 or 3 column file parsing'''

    def __init__ (self, settingsIn='settings', settingsOut='settings.stem', \
                  associations='associations', theta=1.0):
        self.speciesToTraits = {}
        self.groupsToSpecies = {}
        self.header = ''

        assert settingsIn.strip() != settingsOut.strip(), \
            'Input settings file should not equal output settings file'

        try:
            settingsInFile = open(settingsIn, 'r')
            settingsOutFile = settingsOut(settingsOut, 'w')
        except IOError:
            print 'Trouble opening beast formatted trait input and output files.'
            exit()

        self.buildHeader(theta)
        if self.doesIncludeAssociations(settingsInFile):
            self.getSettingsAndAssociations(settingsInFile)

            try:
                associationsFile = open(associations, 'w')
            except IOError:
                print 'Could not open associations file for writing'
                exit()

            self.generateAssociations(associationsFile)

            associationsFile.close()
        else:
            self.getSettingsOnly(settingsInFile)
        self.generateSettings(settingsOutFile)

        try:
            settingsInFile = open(settingsIn, 'r')
            settingsOutFile = settingsOut(settingsOut, 'w')
        except IOError:
            print 'Trouble closing beast formatted trait input and output files.'
            exit()

    def getSettingsOnly(self, settingsFile):
        '''alters: self.speciesToTraits, format of file is "COL_ONE    COL_TWO" '''

        for line in settingsFile:
            splits = re.split(DIVIDER, line)
            species = splits[1].strip()
            if self.speciesToTraits.has_key(species):
                updatedTraits = self.speciesToTraits[species] + [splits[0].strip()]
                self.speciesToTraits[species] = updatedTraits
            else:
                self.speciesToTraits[species] = [splits[0].strip()]

    def getSettingsAndAssociations(self, settingsFile):
        '''alters: self.speciesToTraits, format of file is "COL_ONE    COL_TWO    COL_THREE" '''

        for line in settingsFile:
            splits = re.split(DIVIDER, line)
            species = splits[1].strip()
            group = splits[2].strip()

            # build settings dict
            if self.speciesToTraits.has_key(species):
                updatedTraits = self.speciesToTraits[species] + [splits[0].strip()]
                self.speciesToTraits[species] = updatedTraits
            else:
                self.speciesToTraits[species] = [splits[0].strip()]

            # build associations dict
            if self.groupsToSpecies.has_key(group):
                updatedSpecies = self.groupsToSpecies[group] + species
                self.groupsToSpecies[group] = updatedSpecies
            else:
                self.groupsToSpecies[group] = [species]


    def doesIncludeAssociations(self, settingsFile):
        header = settingsFile.readline()
        parts = re.split(DIVIDER, header)

        assert parts[0].strip().lower() == COLUMN_ONE, 'First column header must be traits keyword'
        assert parts[1].strip().lower() == COLUMN_TWO, 'Second column header must be species keyword'

        if len(parts) == 3:
            assert parts[2].strip().lower() == COLUMN_THREE, 'Third column header must be groups keyword'
            return True
        else:
            return False

    def buildHeader(self, theta):
        self.header = "properties:\n" + \
                        "    run: 1\t\t\t#0=user-tree, 1=MLE, 2=search\n" + \
                        "    theta: " + str(theta) + "\n" + \
                        "    num_saved_trees: 15\n" + \
                        "    beta: 0.0005\n" + \
                        "species:\n"

    def generateSettings(self, settingsOutFile):
        ''' 
        Writes the settings file with speciesToTraits in the form of str to str.
        '''

        settingsOutFile.write(self.header)
        for name in self.speciesToTraits.keys() :
            settingsOutFile.write("\t" + name + ": ")
            counter = 1
            for trait in self.speciesToTraits[name]:
                if counter < len(self.speciesToTraits[name]):
                    settingsOutFile.write(trait + ", ")
                else:
                    settingsOutFile.write(trait + "\n")
                counter += 1

    def generateAssociations(self, associationsFile):
        ''' 
        Writes the associations file with groupsToSpecies in the form of str to str.
        '''

        for name in self.groupsToSpecies.keys() :
            associationsFile.write("\t" + name + ": ")
            counter = 1
            for trait in self.groupsToSpecies[name]:
                if counter < len(self.groupsToSpecies[name]):
                    associationsFile.write(trait + ", ")
                else:
                    associationsFile.write(trait + "\n")
                counter += 1

if __name__ == "__main__":
    tester = ParseBeast(theta=2.0)
    print tester.speciesToTraits

