'''
Generates settings files based on groups of populations and their alleles.
'''

import stemParse
import outputGen
import subprocess

def debug(message):
    print str(message)

class Grouper:
    def __init__(self, settings='settings', associations='associations', \
                 jarFile='stem.jar', results='results', log='log'):
        self.jarFile = jarFile
        self.settings = settings
        self.logFile = open(log, 'a')

        # parse both settings the first time
        self.parser = stemParse.StemParse(settings, associations)
        self.speciesToAlleles = self.parser.alleles
        self.numSpecies = len(self.speciesToAlleles)
        self.groups = self.parser.groups

        # initialize output generator
        self.outputer = outputGen.OutputGen(results)

    def groupPartitions(self, group):
        ''' group is a list of populations.
        returns the list of all different partitions of group. '''
        import partition
        pIter = partition.Partition(group)
        output = []
        for p in pIter:
            output.append(p)
        return output

    def buildAllPartitions(self):
        allPartitions = {}
        for group in self.groups:
            groupList = self.groups[group].split(',')
            for i in range(len(groupList)):
                groupList[i] = groupList[i].strip()
            allPartitions[group] = self.groupPartitions(groupList)
        return allPartitions

    def nextCombination(self):
        ''' returns an iterator of the next settings list'''
        allPermutations = self.buildAllPartitions().values()
        instances = []
        for group in allPermutations:
            instances.append(len(group))
        cachedIndecies = self.calculatePermutationOrdering(instances)

        for i in range(len(cachedIndecies)):
            setting = []
            for j in range(len(allPermutations)):
                for k in allPermutations[j][cachedIndecies[i][j]]:
                    setting.append(k)
            yield list(setting)

    def calculatePermutationOrdering(self, countList):
        total = 1
        pattern = []
        for count in countList:
            pattern.append(total)
            total *= count
        workingList = [0] * len(countList)
        allLists = [list(workingList)]
        switchList = list(pattern)
        for i in range(total - 1):
            for j in range(len(switchList)):
                switchList[j] -= 1
                if switchList[j] == 0:
                    switchList[j] = pattern[j]
                    workingList[j] += 1
                    if workingList[j] >= countList[j]:
                        workingList[j] = 0
            allLists.append(list(workingList))
        return allLists

    def mapAlleles(self, popList):
        ''' 
        Creates a dictionary of string population to string list of alleles.
        '''
        popToAlleles = {}
        for sp in popList:
            spName = ""
            alleles = ""
            for pop in sp:
                spName += pop
                if alleles == "":
                    alleles = self.speciesToAlleles[pop]
                else:
                    alleles += ", " + self.speciesToAlleles[pop]

            popToAlleles[spName] = alleles
        return popToAlleles

    def run(self):

        for setting in self.nextCombination():
            settingDict = self.mapAlleles(setting)
            self.parser.generateSettings(settingDict, self.settings)

            # call java
            output = subprocess.check_output(["java", "-jar", self.jarFile])

            self.logFile.write(output)
            debug(output)

            # pass output to parser for new tree and likelihood
            self.parser.parseOutput(output)
            tree = self.parser.currentTree
            likelihood = self.parser.currentLikelihood

            # pass tree, likelihood, number of species to output generator
            self.outputer.generateOutput(tree, likelihood, self.numSpecies)

    def test(self):
        test = Grouper()
        print 'testing settings parsing: ', test.speciesToAlleles, test.groups
        print test.groupPartitions([1, 2, 3, 4])
        print test.buildAllPartitions()
        for x in test.nextCombination():
            print x
        test.run()

    def __del__(self):
        self.logFile.close()

if __name__ == '__main__':
    run = Grouper(settings='settings', associations='associations', \
                 jarFile='stem.jar', results='results', log='log')
    run.run()
