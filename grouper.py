'''
Generates settings files based on groups of populations and their alleles.
'''

def debug(message):
    print str(message)

class Grouper:
    def __init__(self, settings='settings', associations='associations', jarFile='stem.jar', results='results'):
        import parseSettings
        self.parser = parseSettings.ParseSettings(settings, associations)
        self.alleles = self.parser.alleles
        self.groups = self.parser.groups
        self.jarFile = jarFile
        self.settings = settings

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
                    alleles = self.alleles[pop]
                else:
                    alleles += ", " + self.alleles[pop]

            popToAlleles[spName] = alleles
        return popToAlleles

    def run(self):
        import subprocess
        import stemOut
        outLog = open('output', 'w')

        for setting in self.nextCombination():
            settingDict = self.mapAlleles(setting)
            self.parser.generateSettings(settingDict, self.settings)
            # call java
            output = subprocess.check_output(["java", "-jar", self.jarFile])
            outLog.write(output)

            # write results
            res = stemOut.StemOut()
            res.captureTreeAndAppendResults(output, resultsFile)
            debug(output)

        outLog.close()
        resultsFile.close()

    def test(self):
        test = Grouper()
        print 'testing settings parsing: ', test.alleles, test.groups
        print test.groupPartitions([1, 2, 3, 4])
        print test.buildAllPartitions()
        for x in test.nextCombination():
            print x
        test.run()

if __name__ == '__main__':
    run = Grouper()
    run.run()
