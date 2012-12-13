'''
Description: Stem step-up speciation processor
Created on Dec 13, 2012
'''

speciesToAlleles = {}
intToSpecies = {}  # enum of int to species

def buildSpeciesDictAndList(file):
    ''' creates a dictionary of the form [species] : [list_of_alleles] '''
    while file.readline().strip() != "species:":
        None  # do nothings

    numSpecies = 0
    for line in file:
        line = line.strip()
        if len(line) > 0:
            sp = line[0]  # could be more than one character (fix this)
            rest = line[1:]
            rest = rest.replace(':', '')
            rest = rest.strip()
            speciesToAlleles[sp] = rest
            intToSpecies[numSpecies] = sp
        numSpecies += 1

def makeSpeciesGroups(speciesToCombine):
    groups = []
    groups.append(set(speciesToCombine[0]))
    for x, y in speciesToCombine:
        for i in range(len(groups)):
            if x in groups[i]:
                groups[i].add(y)
            elif y in groups[i]:
                groups[i].add(x)
            else:
                groups.append(set(x, y))

    # TODO: might need to look through the groups to verify that they don't share common
    # members
    return groups


def updateSpeciesDictAndList(groups):
    for group in groups:
        newName = ""
        newAlleles = ""
        for member in group:
            # build new name
            oldName = intToSpecies[member]
            newName = newName + oldName
            if len(newAlleles) == 0:
                newAlleles = speciesToAlleles[oldName]
            else:
                newAlleles = newAlleles + ", " + speciesToAlleles[oldName]
            speciesToAlleles.pop(oldName)
        speciesToAlleles[newName] = newAlleles
        print speciesToAlleles


def parseMatrix(file):
    strMatrix = []
    numSpecies = 0
    # process output into a list of strings
    for line in file:
        line = line.strip()
        if len(line) > 0 and line[0] == '[':
            numSpecies += 1  # count the number of species
            matrixRow = line.replace('[', ' ')
            matrixRow = matrixRow.replace(']', ' ')
            strMatrix.extend(matrixRow.split(' '))

    dblMatrix = []
    for i in strMatrix:
        if i not in ('', '\n'):
            dblMatrix.append(float(i))

    return dblMatrix, numSpecies


def findMinElements(matrix, numSpecies):
    # find all with min, store in list of tuples
    row = 0
    col = 0
    minFound = matrix[1]
    for x in matrix:
        if col > row and x < minFound:
            minFound = x
        col += 1
        if col > numSpecies - 1:
            col = 0
            row += 1

    row = 0
    col = 0
    species = []
    for x in matrix:
        if x == minFound:  # maybe should be some tolerance
            species.append((row, col))
        col += 1
        if col > numSpecies - 1:
            col = 0
            row += 1

    return species

if __name__ == '__main__':
    output = open('output', 'r')
    matrix, numSpecies = parseMatrix(output)
    output.close()

    settings = open('settings', 'r')
    buildSpeciesDictAndList(settings)
    settings.close()

    print intToSpecies
    print speciesToAlleles

    speciesToCombine = findMinElements(matrix, numSpecies)

    for x, y in speciesToCombine:
        print intToSpecies[x], intToSpecies[y]

    groups = makeSpeciesGroups(speciesToCombine)

    updateSpeciesDictAndList(groups)
