#!/usr/bin/env python -O -t -W all

import argparse
import src.iterator as iterator
import src.processStemOut as processStemOut
import src.parseBeast as parseBeast
import src.cleanTrees as cleanTrees
import src.sample as sample

def setupMode(subparsers):
    setup_parser = subparsers.add_parser('setup', help='prepare tree and settings files for analysis')
    setup_parser.add_argument('-c', '--clean', metavar='treeFile', nargs='+', \
                              help='prepare tree file(s) for analysis')
    setup_parser.add_argument('-s', '--scalingFile', metavar='scalingFile', nargs=1, \
                              help='provide a text file with each scaling factor on a new line ' + \
                              'in the format: [scalingFactor]. Values prefixed in the order that ' + \
                              'trees appear after the clean command, DEFAULT: [1.0] for each', default=None)
    setup_parser.add_argument('-t', '--traits', metavar='traitsFile', nargs=1,
                              help='read in traits file as Beast format')
    setup_parser.add_argument('-bt', '--theta', type=float, metavar="thetaValue",
                              help='set theta value for Beast formatted traits files, DEFAULT: 1.0', nargs=1, \
                              default=[1.0])

    return setup_parser

def discoveryMode(subparsers):
    discovery_parser = subparsers.add_parser('discovery', help='discovery analysis')
    discovery_parser.add_argument('-t', '--tree', metavar='treeFile', nargs=1, required=True, \
                                  help='specify tree file')
    discovery_parser.add_argument('-s', '--settings', metavar='settingsFile', nargs=1, required=True, \
                                  help='specify settings file in STEM format')
    discovery_parser.add_argument('-v', '--verbose', action="store_true", help='execute in verbose mode, DEFAULT: off',
                                   default=False)

    return discovery_parser

def validationMode(subparsers):
    validation_parser = subparsers.add_parser('validation', help='validation analysis')
    validation_parser.add_argument('-t', '--tree', metavar='treeFile', nargs=1, required=True, \
                                  help='specify tree file')
    validation_parser.add_argument('-s', '--settings', metavar='settingsFile', nargs=1, required=True, \
                                  help='specify settings file in STEM format')
    validation_parser.add_argument('-a', '--associations', metavar='associationsFile', nargs=1, required=True, \
                                   help='specify associations file in STEM format')
    validation_parser.add_argument('-v', '--verbose', action="store_true", help='execute in verbose mode, DEFAULT: off'
                                   , default=False)

    return validation_parser

def subsamplingMode(subparsers):
    subsampling_parser = subparsers.add_parser('subsampling', help='Subsampling')
    subsampling_parser.add_argument("-i", "--input", metavar="inputFile",
                help="input file or directory", nargs=1, required=True)
    subsampling_parser.add_argument("-o", "--output", metavar="outFile",
                help="output file", nargs=1, required=True)
    subsampling_parser.add_argument("-a", "--assoc", metavar="assocFile",
                help="association file", nargs=1, required=True)
    subsampling_parser.add_argument("-np", "--numperpop", metavar="numAlleles",
                help="number of alleles per population", type=int, nargs=1, required=True)
    subsampling_parser.add_argument("-rp", "--replicates", metavar="numReps",
                help="number of replicates", type=int, nargs=1, required=True)
    subsampling_parser.add_argument("-r", "--rootallele",
                help="always include first allele, DEFAULT: false", action="store_true")
    subsampling_parser.add_argument("-ap", "--append", metavar="settingsFile",
                help="append a settings file", nargs=1)

    return subsampling_parser

def testingMode(subparsers):
    testing_parser = subparsers.add_parser('testing', help='power testing')
    mode = testing_parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('-d', '--discovery', action="store_true", help='run in discovery mode')
    mode.add_argument('-val', '--validation', action="store_true", help='run in validation mode, requires associations file')

    testing_parser.add_argument('-l', '--loci', metavar='numLoci', type=int, nargs=1, required=True, \
                                  help='number of loci to be sampled from tree file each replicate')
    testing_parser.add_argument('-r', '--replicates', metavar='numTimes', type=int, nargs=1, required=True, \
                                  help='execute the complete analysis numTimes times,' +
                                  'taking different samples of the tree file')
    testing_parser.add_argument('-t', '--tree', metavar='treeFile', nargs=1, required=True, \
                                  help='specify tree file')
    testing_parser.add_argument('-s', '--settings', metavar='settingsFile', nargs=1, required=True, \
                                  help='specify settings file in STEM format')
    testing_parser.add_argument('-a', '--associations', metavar='associationsFile', nargs=1, \
                                   help='specify associations file in STEM format')
    testing_parser.add_argument('-v', '--verbose', action="store_true", help='execute in verbose mode, DEFAULT: off', \
                                default=False)

    return testing_parser

def parseArgs():
    parser = argparse.ArgumentParser(\
        description='SpedeSTEM 2, a python package for species delimitation.', \
        epilog='For additional help see [this website]')

    subparsers = parser.add_subparsers(help='commands', dest='command')

    setup_parser = setupMode(subparsers)
    discovery_parser = discoveryMode(subparsers)
    validation_parser = validationMode(subparsers)
    subsampling_parser = subsamplingMode(subparsers)
    testing_parser = testingMode(subparsers)

    args = parser.parse_args()

    # debugging argument parsing
    print args

    # catch invalid option configurations (sanity checks)
    if args.command == 'setup' and args.scalingFile and not args.clean:
        setup_parser.error('Scaling factors specified without tree file, ' + \
                           'add --clean or remove --scalingFile')
    if args.command == 'setup' and not args.clean and not args.traits:
        setup_parser.error("SpedeSTEM_2 setup: error: No options specified. Try '-h' for help")
    if args.command == 'testing' and args.validation and not args.associations:
        testing_parser.error('Validation mode specified without associations file, ' + \
                           'add -a/--associations argument')
    if args.command == 'testing' and args.associations and not args.validation:
        testing_parser.error('Associations file specified while in discovery mode, ' + \
                           'change to -val/--validation mode or remove -a/--associations argument')

    return args

def executeChoice(args):
    if args.command == 'setup':
        print '\n################################'
        print '####### Performing Setup #######'
        print '################################\n'

        scalingFile = None
        if args.clean:
            if args.scalingFile:
                scalingFile = args.scalingFile[0]
            # clean trees and prefix each with scaling factors if file provided
            cleanTrees.CleanTrees(args.clean, scalingFile, sigfigs=8)

        if args.traits:
            # convert beast formatted traits file to stem settings
            parseBeast.ParseBeast(settingsIn=args.traits[0], theta=args.theta[0])

    elif args.command == 'discovery':
        print '\n################################'
        print '###### DISCOVERY ANALYSIS ######'
        print '################################\n'

        # check here for settings file, tree files, maybe scan the files for correct formatting
        discovery = iterator.Iterator([args.tree], numRuns=1, \
                                      numTrees=None, settings=args.settings[0], maxTrees=None, \
                                      verbose=args.verbose)
        discovery.printSettings()
        discovery.run()

        # process the stem output
        print "Completing Analysis...",
        processor = processStemOut.ProcessStemOut()
        processor.rawOutput()
        processor.calculateWilik()
        print "See 'results.txt' and 'itTable.txt' files\n"

    elif args.command == 'validation':
        print '\n#################################'
        print '###### VALIDATION ANALYSIS ######'
        print '#################################\n'

        # check for settings, tree files, associations, etc.
        validation = iterator.Iterator([args.tree], numRuns=1, \
                                      numTrees=None, settings=args.settings[0], maxTrees=None, \
                                      verbose=args.verbose, isValidation=True, associations=args.associations[0])
        validation.printSettings()
        validation.run()

        # process the stem output
        print "Completing Analysis...",
        processor = processStemOut.ProcessStemOut()
        processor.rawOutput()
        processor.calculateWilik()
        print "See 'results.txt' and 'itTable.txt' files\n"


    elif args.command == 'subsampling':
        print '\n#################################'
        print '########## SUBSAMPLING ##########'
        print '#################################\n'

        append = None
        if args.append:
            append = args.append[0]

        sampleRun = sample.Sample(sampleOutput=args.output[0], sampleInput=args.input[0], \
        sampleCommand=append, assoc=args.assoc[0], \
        rootallele=args.rootallele, numperpop=args.numperpop[0], numrep=args.replicates[0])

        # process subsampling
        print "Executing Subsampling..."
        sampleRun.run()
        print "File '" + args.output[0] + "' has been created."



    elif args.command == 'testing':
        print '\n#################################'
        print '######### POWER TESTING #########'
        print '#################################\n'

        associations = ""
        if args.associations:
            associations = args.associations[0]
        # check for settings, tree files, associations, etc.
        validation = iterator.Iterator([args.tree], numRuns=args.replicates[0], \
                                      numTrees=args.loci[0], settings=args.settings[0], maxTrees=args.loci[0], \
                                      verbose=args.verbose, isValidation=args.validation, associations=associations)
        validation.printSettings()
        validation.run()

        # process the stem output
        print "Completing Analysis...",
        processor = processStemOut.ProcessStemOut()
        processor.rawOutput()
        processor.calculateWilik(args.replicates[0])
        print "See 'results.txt' and 'itTable.txt' files\n"

def main():
    args = parseArgs()
    executeChoice(args)


if __name__ == '__main__':
    main()
