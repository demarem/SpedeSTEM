import random
import argparse
import glob
import os
import sys
import re

class randomChooser:
    def __init__(self, inputName, outputName, assocName, commandName, rootAllele=False):
       self.popToSpec = {}
       self.popToLines = {}
       self.header = ""
       self.footer=""

       self.inputName = inputName
       self.outputName = outputName
       self.assocName = assocName

       self.inputFile = None
       self.outputFile = None
       self.assocFile = None
       self.commandName = commandName
    
       self.rootAlleleLine = ""
       self.rootAllele = rootAllele
       self.numPop = 0
       self.numPerPop = 0

    def openWithCheck(self, filename, flags):
        try:
            return open(name=filename, mode=flags)
        except IOError as e:
            print "no such file: " + filename 
            sys.exit()
            return None

    def openFiles(self):
        # self.openWithCheck(self.inputFile, self.inputName, "r")
        # self.openWithCheck(self.assocFile, self.assocName, "r")
        # self.openWithCheck(self.outputFile, self.outputName, "a")
        count = 0 
        fileList = [self.inputName, self.assocName, self.outputName]
        try:
            self.inputFile = open(self.inputName, "r")
            count+=1
            self.assocFile = open(self.assocName, "r")
            count+=1
            self.outputFile = open(self.outputName, "a")
        except IOError as e:
            print "no such file: " + fileList[count] 
            sys.exit()

        if self.commandName:
            try: 
                self.settingsFile = open(self.commandName)
            except IOError as e:
                self.settingsFile = None
                print "no settings file for " + self.inputName
        else:
            self.settingsFile = None
        
        # if self.withSettings:
        #     try: 
        #         self.settingsFile = open(self.matchName(self.inputName))
        #     except IOError as e:
        #         self.settingsFile = None
        #         print "no settings file for " + self.inputName
        # else:
        #     self.settingsFile = None

    def reset(self):
       self.popToSpec = {}
       self.popToLines = {}
       self.header = ""
       self.footer=""
       self.inputFile.close()
       self.outputFile.close()
       self.assocFile.close()

    def choose_and_remove(self, items):
        # pick an item index
        if items:
            index = random.randrange( len(items) )
            return items.pop(index)
        # nothing left!
        return None
    def writeHeader(self, nexus=False, numPerPop=1, root=False):
        if nexus:
            self.outputFile.write("#NEXUS\n")
        numAlleles = 0
        for pop in self.popToLines.keys():
            if numPerPop < len(self.popToLines[pop]):
                numAlleles += numPerPop
            else:
                numAlleles += len(self.popToLines[pop])

        # numAlleles = self.numPop * numPerPop 

        if self.rootAllele:
            numAlleles += 1
        self.header = re.sub(r"NTAX=\d+", "NTAX=" + str(numAlleles), self.header)
        self.outputFile.write(self.header)

    def writeFooter(self, outputFile=None, settingsFile=None):

        outputFile.write(self.footer) 
        outputFile.write("\n")

        if settingsFile:
            line = settingsFile.readline()
            while line:
                outputFile.write(line)
                line = settingsFile.readline()
            outputFile.write("\n\n")

    def matchName(self, nexusName, nexusExten=".nexus", commandExten=".txt"):
        return nexusName.replace(nexusExten, commandExten) 

    def buildPopToLines(self, newInputFile=None):
        if newInputFile:
            inputFile = newInputFile
        else:
            inputFile = self.inputFile

        line = "" 
        count = 0
        while count<10000 and line.strip() != "MATRIX":
            line = inputFile.readline()
            if not "NEXUS" in line:
                self.header += line
            count+=1
        if count == 10000:
            print "MATRIX was not found"
            return
        if self.rootAllele: 
            self.rootAlleleLine = inputFile.readline()
        while line:
            line = inputFile.readline()
            if(";" in line):
                self.footer += line
                while line:
                    line = inputFile.readline()
                    self.footer += line
                break
            lineSplits = line.strip().split()
            if len(lineSplits) >= 2: 
                speciesName = lineSplits[0]
                speciesAllele = lineSplits[1] 
            else:
                speciesName = None

            for pop, specList in self.popToSpec.items():
                if speciesName in specList: 
                    if pop in self.popToLines: 
                        self.popToLines[pop].append(line) 
                    else:
                        self.popToLines[pop] = [line] 
                     
        self.numPop = len(self.popToLines)
        
    def buildPopToSpec(self, newAssocFile=None):
        if newAssocFile:
            assocFile = newAssocFile
        else:
            assocFile = self.assocFile

        for line in assocFile:
            splits = line.strip().split()
            if len(splits)>=2:
                spec = splits[0]
                pop = splits[1]
                if pop in self.popToSpec: 
                    self.popToSpec[pop].append(spec) 
                else:
                    self.popToSpec[pop] = [spec] 


    def randomOutput(self, newOutputFile=None, newSettingsFile=None, numPerPop=1, nexus=False):
        if newOutputFile:
            outputFile = newOutputFile 
        else:
            outputFile = self.outputFile

        # outputFile.write(self.header)

        self.writeHeader(nexus=nexus, numPerPop = numPerPop)


        self.rootAlleleLine = re.sub("\s+", "   ", self.rootAlleleLine) 
        outputFile.write(self.rootAlleleLine + "\n")

        for pop in self.popToLines.keys():
            if numPerPop < len(self.popToLines[pop]):
                numRuns = numPerPop
            else:
                numRuns = len(self.popToLines[pop])


            for a in range(numRuns): 
                randomEl = self.choose_and_remove(self.popToLines[pop])
                lineSplits = randomEl.strip().split()
                newPopName = pop + "_" + str(a+1)
                alleleName = lineSplits[1] 
                outputFile.write(newPopName) 

                for el in lineSplits[1:]: 
                    outputFile.write("   " + el) 

                outputFile.write("\n") 

        self.writeFooter(outputFile, self.settingsFile)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", help="output file")
    parser.add_argument("-r", "--rootallele", help="always include first allele", type=bool)
    parser.add_argument("-c", "--command", help="append a settings file")
    parser.add_argument("-np", "--numperpop", help="number of alleles per population", type=int)
    parser.add_argument("-nr", "--numrep", help="number of replicates", type=int)
    parser.add_argument("-a", "--assoc", help="association file")
    parser.add_argument("-i", "--input", help="input file or directory")

    args = parser.parse_args()

    if args.numperpop:
        numPerPop = args.numperpop
    else:
        numPerPop = 1
    if args.numrep:
        numRep = args.numrep
    else:
        numRep = 20
    if args.assoc:
        assocName = args.assoc
    else:
        assocName = "assoc.txt" 

    if args.output:
        outputName = args.output
    else:
        outputName = 'output.nexus' 

    if args.command:
        commandName = args.command
    else:
        commandName = None 

    if args.input:
        if os.path.isdir(args.input):
            nexList = glob.glob(args.input + "/*.nexus") 
        else:
            nexList = [args.input]
    else:
        nexList = glob.glob("nexus/*.nexus") 

    if not nexList:
        print "no input files found"
        sys.exit()

    for nexName in nexList:
        for a in range(numRep):
            nexus = a==0

            rc = randomChooser(inputName = nexName,\
                    outputName=outputName, assocName=assocName, \
                    commandName=commandName, rootAllele=args.rootallele)
            rc.openFiles()
            rc.buildPopToSpec()
            if not rc.popToSpec:
                print "association file is empty"
            rc.buildPopToLines()
            if not rc.popToLines:
                print "Warning: no species found. Check the input files"
                break
            rc.randomOutput(numPerPop=numPerPop, nexus=nexus)
            rc.reset()
