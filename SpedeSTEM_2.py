#!/usr/bin/env python -O -t -W all

import argparse
from src.setupCommand import SetupCommand
from src.discoveryCommand import DiscoveryCommand
from src.validationCommand import ValidationCommand
from src.subsamplingCommand import SubsamplingCommand
from src.testingCommand import TestingCommand

def setupMode(subparsers):
    setup_parser = subparsers.add_parser('setup', help='prepare tree and settings files for analysis')
    setup_parser.add_argument('-c', '--clean', metavar='treeFile', nargs='+', \
                              help='prepare tree file(s) for analysis')
    setup_parser.add_argument('-s', '--scalingFile', metavar='scalingFile', nargs=1, \
                              help='provide a text file with each scaling factor on a new line ' + \
                              'in the format: [scalingFactor]. Values prefixed in the order that ' + \
                              'trees appear after the clean command, DEFAULT: [1.0] for each', default=None)
    setup_parser.add_argument('-p', '--prefix', metavar='filePrefix', nargs=1, \
                              help="prefix every generated tree with the supplied string " \
                              "(use only [a-zA-Z_-]), DEFAULT: no prefix")
    setup_parser.add_argument('-t', '--traits', metavar='traitsFile', nargs=1,
                              help='read in traits file as Beast format')
    setup_parser.add_argument('-bt', '--theta', type=float, metavar="thetaValue",
                              help='set theta value for Beast formatted traits files, DEFAULT: 1.0', nargs=1, \
                              default=[1.0])
    setup_parser.add_argument('-d', '--distribute', metavar='treeFile', nargs='+', help='create new tree file ' + \
                              'with one tree from each of the specified files')

    return setup_parser

def discoveryMode(subparsers):
    discovery_parser = subparsers.add_parser('discovery', help='discovery analysis')
    discovery_parser.add_argument('-t', '--tree', metavar='treeFile', nargs=1, \
                                  help='specify tree file')
    discovery_parser.add_argument('-d', '--directory', metavar='treeDirectory', nargs=1, \
                                  help='relative directory of tree files (.tre)')
    discovery_parser.add_argument('-s', '--settings', metavar='settingsFile', nargs=1, required=True, \
                                  help='specify settings file in STEM format')
    discovery_parser.add_argument('-v', '--verbose', action="store_true", help='execute in verbose mode, DEFAULT: off',
                                   default=False)
    discovery_parser.add_argument('-q', '--quiet', action="store_true", help='turn off overwrite errors, DEFAULT: not quiet',
                                   default=False)

    return discovery_parser

def validationMode(subparsers):
    validation_parser = subparsers.add_parser('validation', help='validation analysis')
    validation_parser.add_argument('-t', '--tree', metavar='treeFile', nargs=1, \
                                  help='specify tree file')
    validation_parser.add_argument('-d', '--directory', metavar='treeDirectory', nargs=1, \
                                  help='relative directory of tree files(.tre)')
    validation_parser.add_argument('-s', '--settings', metavar='settingsFile', nargs=1, required=True, \
                                  help='specify settings file in STEM format')
    validation_parser.add_argument('-a', '--associations', metavar='associationsFile', nargs=1, required=True, \
                                   help='specify associations file in STEM format')
    validation_parser.add_argument('-v', '--verbose', action="store_true", help='execute in verbose mode, DEFAULT: off'
                                   , default=False)
    validation_parser.add_argument('-q', '--quiet', action="store_true", help='turn off overwrite errors, DEFAULT: not quiet',
                                   default=False)

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
    testing_parser.add_argument('-q', '--quiet', action="store_true", help='turn off overwrite errors, DEFAULT: not quiet',
                                   default=False)

    return testing_parser

def parseArgs():
    parser = argparse.ArgumentParser(\
        description='SpedeSTEM 2, a python package for species delimitation.')

    subparsers = parser.add_subparsers(help='commands', dest='command')

    setup_parser = setupMode(subparsers)
    discovery_parser = discoveryMode(subparsers)
    validation_parser = validationMode(subparsers)
    subsampling_parser = subsamplingMode(subparsers)
    testing_parser = testingMode(subparsers)

    args = parser.parse_args()

    # debugging argument parsing
    # print args

    # catch invalid option configurations (sanity checks)
    if args.command == 'setup' and args.scalingFile and not args.clean:
        setup_parser.error('Scaling factors specified without tree file, ' + \
                           'add --clean or remove --scalingFile')
    if args.command == 'setup' and not args.clean and not args.traits and not args.distribute:
        setup_parser.error("SpedeSTEM_2 setup: error: No options specified. Try '-h' for help")
    if args.command == 'testing' and args.validation and not args.associations:
        testing_parser.error('Validation mode specified without associations file, ' + \
                           'add -a/--associations argument')
    if args.command == 'testing' and args.associations and not args.validation:
        testing_parser.error('Associations file specified while in discovery mode, ' + \
                           'change to -val/--validation mode or remove -a/--associations argument')
    if (args.command == 'discovery' or args.command == 'validation') and args.tree and args.directory:
        testing_parser.error('Specify only one of --tree and --directory, ' + \
                           'remove either --tree or --directory')
    if (args.command == 'discovery' or args.command == 'validation') and not args.tree and not args.directory:
        testing_parser.error('Must specify either --validation or --discovery, ' + \
                           'add either --tree or --directory')
    return args

def main():
    setup = SetupCommand()
    discover = DiscoveryCommand()
    validate = ValidationCommand()
    subsample = SubsamplingCommand()
    test = TestingCommand()

    commands = {'setup': setup, 'discovery': discover, 'validation': validate,
                'subsampling': subsample, 'testing': test}

    args = parseArgs()
    commands[args.command].execute(args)

if __name__ == '__main__':
    main()
