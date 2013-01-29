import math
import sys
import collections
import argparse

class WiLik:
    def __init__(self, inputName, outputName):
        self.inputName = inputName
        self.outputName = outputName
        self.inputFile = None
        self.outputFile = None

        self.total = 0
        self.blockSize = 1

        self.inputList = []
        self.kToLnList = {}
        self.singleCalcWi = []
        self.meanDict = {}
        self.dataList = []

        self.InputTuple = collections.namedtuple('inputTuple', ['k', 'ln'])
        self.DataTuple = collections.namedtuple('DataTuple', \
                ['k', 'ln', 'AIC', 'delta', 'modelLik', 'wi'])

        self.WiTuple = collections.namedtuple('WiTuple', \
                ['ln', 'AIC', 'delta', 'modelLik', 'wi'])



    def checkOpen(self, fileName, flags):
        try:
            return open(fileName, flags)
        except IOError:
            print "Could not open: " + fileName
            sys.exit()

    def openFiles(self):
        self.inputFile = self.checkOpen(self.inputName, "r")
        self.outputFile = self.checkOpen(self.outputName, "w")

    def closeFiles(self):
        self.inputFile.close()
        self.outputFile.close()

    def reset(self):

        self.total = 0

    def readKLog(self, newInputFile=None, delim=";", blockSize=5):
        self.blockSize = blockSize
        if newInputFile:
            inputFile = newInputFile
        else:
            inputFile = self.inputFile

        klnList = []

        linNum = 0
        blockCount = 0

        for line in inputFile:
            linNum += 1
            blockCount += 1

            splits = line.split(delim)

            if len(splits) >= 3:
                try:
                    k = int(splits[1].strip())
                    ln = float(splits[2].strip())
                    inputTuple = self.InputTuple(k, ln)
                    klnList.append(inputTuple)
                    if k in self.kToLnList:
                        self.kToLnList[k].append(ln)
                    else:
                        self.kToLnList[k] = [ln]
                except ValueError :
                    print "Conversion error in line: " + str(linNum)
            else:
                print "bad format. Check separators in line: " + str(linNum)
            if(blockCount == blockSize):
                self.inputList.append(klnList)
                blockCount = 0
                klnList = []

        if klnList:
            self.inputList.append(klnList)

        self.total = len(klnList)

    def computeOnce(self, kLnList=None):

        AICList = []
        for kln in kLnList:
            AIC = -2 * kln.ln + 2 * kln.k
            AICList.append(AIC)

        deltaList = []
        AICmin = min(AICList)
        for AIC in AICList:
            delta = AIC - AICmin
            deltaList.append(delta)

        modelLikList = []
        for delta in deltaList :
            modelLik = math.exp(-0.5 * delta)
            modelLikList.append(modelLik)

        wiList = []
        sumLik = sum(modelLikList)
        for modelLik in modelLikList:
            wi = modelLik / sumLik
            wiList.append(wi)

        dataTupleList = []
        dataDict = {}
        for kln, AIC, delta, modelLik, wi \
                in zip(kLnList, AICList, deltaList, modelLikList, wiList):
            dataDict[kln.k] = self.WiTuple(kln.ln, AIC, delta, modelLik, wi)

        return dataDict

    def computeAll(self, blockSize=1):
        kLnMeanList = self.meanLn()
        self.singleCalcWi = self.computeOnce(kLnMeanList)

        for klnList in self.inputList:
            dataDict = self.computeOnce(klnList)
            self.dataList.append(dataDict)
        self.meanWiCalc()


    def writeMeans(self):
        self.outputFile.write("Single AIC calculation\n")
        self.outputFile.write("k, ln, AIC, delta, modelLik, wi\n")
        for k in self.singleCalcWi.keys():

            # print '%d, %f, ' % (inputTuple.k, inputTuple.ln),
            # print '%f, %f, %.20f, %.20f' \
            # % (calcTuple.AIC, calcTuple.delta, \
            # calcTuple.modelLik, calcTuple.wi)
            wiTuple = self.singleCalcWi[k]

            self.outputFile.write('%d, %f, '
                    % (k, wiTuple.ln))
            self.outputFile.write('%f, %f, %.20f, %.20f\n' \
                % (wiTuple.AIC, wiTuple.delta, \
                wiTuple.modelLik, wiTuple.wi))

        self.outputFile.write("Multiple AIC calculations\n")
        self.outputFile.write("k, ln, AIC, delta, modelLik, wi\n")
        for k in self.meanDict.keys() :
            wiTuple = self.meanDict[k]
            self.outputFile.write('%d, %f, '
                    % (k, wiTuple.ln))
            self.outputFile.write('%f, %f, %.20f, %.20f\n' \
                % (wiTuple.AIC, wiTuple.delta, \
                wiTuple.modelLik, wiTuple.wi))



    def countLines(self, fileName):
        mFile = self.checkOpen(fileName, "r")

        count = 0
        for line in mFile:
            count += 1

        mFile.close()
        return count


    def meanLn(self):
        # tupleList is a list of tuples
        kLnMeanList = []
        for k in self.kToLnList.keys():
            lnList = self.kToLnList[k]
            if lnList :
                lnMean = sum(lnList) / len(lnList)
                inputTuple = self.InputTuple(k, lnMean)
                kLnMeanList.append(inputTuple)
        return kLnMeanList

    def meanWiCalc(self):
        kDict = {}
        for k in self.dataList[0].keys():
            for kToWi in self.dataList:
                if k in kDict:
                    kDict[k].append(kToWi[k])
                else:
                    kDict[k] = [kToWi[k]]
        # self.meanDict = {}
        for k in kDict.keys():
            meanAIC = self.meanOfTupleList(mapfunc=self.getAIC, \
                    tList=kDict[k])
            meanLn = self.meanOfTupleList(mapfunc=self.getLn, \
                    tList=kDict[k])
            meanDelta = self.meanOfTupleList(mapfunc=self.getDelta, \
                    tList=kDict[k])
            meanML = self.meanOfTupleList(mapfunc=self.getModelLik, \
                    tList=kDict[k])
            meanWi = self.meanOfTupleList(mapfunc=self.getWi, \
                    tList=kDict[k])
            wiTuple = self.WiTuple(meanLn, meanAIC, meanDelta, meanML, meanWi)
            self.meanDict[k] = wiTuple


    def meanOfTupleList(self, mapfunc, tList):
        # tList is a list of tuples
        if tList:
            average = sum(map(mapfunc, tList))\
                    / len(tList)

            return average
        else:
            return None

    def getLn(self, mTuple):
        return mTuple.ln

    def getAIC(self, mTuple):
        return mTuple.AIC

    def getDelta(self, mTuple):
        return mTuple.delta
    def getModelLik(self, mTuple):
        return mTuple.modelLik

    def getWi(self, mTuple):
        return mTuple.wi


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="input file or directory")
    parser.add_argument("-o", "--output", help="output file")
    parser.add_argument("-n", "--numrep", help="number of replicates", type=int)
    args = parser.parse_args()

    if args.numrep:
        numRep = args.numrep
    else:
        numRep = 1

    if args.input:
        inputName = args.input
    else:
        inputName = "input.result"

    if args.output:
        outputName = args.output
    else:
        outputName = "output.wi"


    wl = WiLik(inputName, outputName)
    lineCount = wl.countLines(wl.inputName)
    blockSize = lineCount / numRep

    wl.openFiles()

    wl.readKLog(blockSize=blockSize)
    wl.computeAll()
    wl.writeMeans()
    wl.closeFiles()
