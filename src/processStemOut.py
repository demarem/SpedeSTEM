#!/usr/bin/env python -O -t -W all

''' 
Parse stem raw output and write either simple ';' delineated, average by
number of tips, or average by tree configuration.
'''

import cStringIO
import re

class ProcessStemOut:
    def __init__(self, log='stemOut', results='results'):
        self.logFile = open(log, 'r')
        self.resultsFile = open(results, 'w')
        self.runs = []

    def parseLog(self):
        singleOutput = ''
        for line in self.logFile:
            singleOutput += line
            if line.strip() == '****************** Done ****************':
                self.runs.append(self.parseSingleOutput(singleOutput))
                singleOutput = ''

    def parseSingleOutput(self, singleOutput):
        ''' returns a 3-tuple of (tree, numTips, likelihood) '''
        self.parseLog()

        outputBuffer = cStringIO.StringIO(singleOutput)

        likelihood = ''
        tree = ''
        numSpecies = ''

        for line in outputBuffer:
            if line.strip() == "Maximum Likelihood Species Tree (Newick format):":
                outputBuffer.readline()
                tree = outputBuffer.readline().strip().replace(';', '')

            elif "The settings file contained" in line.strip():
                SPECIESFINDER = r'The settings file contained ([0-9]*) species.*'
                numSpecies = re.findall(SPECIESFINDER, line.strip())[0]
                numTips = int(numSpecies) - 1

            elif "log likelihood for tree: " in line.strip():
                likelihood = float(line.split(": ")[1].strip())
                assert likelihood < 0, 'Found a positive log likelihood'

        return (tree, numTips, likelihood)

    def averageOutputByTips(self):
        tipsToNumAndSum = {}
        for run in self.runs:
            numTips = run[1]
            likelihood = run[2]

            if tipsToNumAndSum.has_key(numTips):
                oldNumAndSum = tipsToNumAndSum[numTips]
                newNumAndSum = (oldNumAndSum[0] + 1, oldNumAndSum[1] + likelihood)
                tipsToNumAndSum[numTips] = newNumAndSum
            else:
                tipsToNumAndSum[numTips] = (1, likelihood)

        for tips in tipsToNumAndSum.keys():
            # avg / num
            self.resultsFile.write(str(tips) + ": " + \
                    str(tipsToNumAndSum[tips][1] / tipsToNumAndSum[tips][0]))

    def averageOutputByTrees(self, numPerms):
        self.parseLog()
        configs = [[] for x in xrange(numPerms)]

        lineNumber = 0
        for run in self.runs:
            configs[lineNumber % numPerms].append(run)
            lineNumber += 1

        for config in configs:
            tree = ""
            sumLike = 0
            for run in config:
                if tree == '':
                    tree = run[0]
                numTips = run[1]
                likelihood = run[2]

                sumLike += likelihood

            self.resultsFile.write(tree + '; ' + str(numTips) + '; ' +
                    str(sumLike / len(config)) + '; ' + str(len(config)) + '\n')
