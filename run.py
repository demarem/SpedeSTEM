#!/usr/bin/env python -O -t -W all

import argparse

# todo:
#    - determine defualt values of arguments
#    - actually run the scripts
#    - determine which combinations of arguments are required with others
#    - ability to handle multiple types of settings files/associations files

def parseArgs():
    parser = argparse.ArgumentParser(\
        description='A STEM wrapper for discovery and validation analysis.', \
        epilog='For additional help see [this website]')

    subparsers = parser.add_subparsers(help='commands', dest='command')

    # discovery analysis mode
    discovery_parser = subparsers.add_parser('discovery', help='discovery analysis')
    discovery_parser.add_argument('-i', '--iterations', metavar='numTimes', type=int, nargs=1, \
                                  help='execute the complete discovery analysis numTimes times,' +
                                  'taking numTimes samples of the tree file, DEFAULT: 1',
                                  default=1)
    discovery_parser.add_argument('-t', '--tree', metavar='N', type=int, nargs='+',
                                  help='specify tree file(s), DEFAULT: genetrees.tre')
    discovery_parser.add_argument('-s', '--settings', metavar='settingsFile', type=file, nargs=1, \
                                  help='specify settings file relative path, DEFAULT: settings')
    discovery_parser.add_argument('-n', '--numtrees', metavar='numTree', type=int, nargs='+', \
                                  help='the list of numbers of trees to be sampled from tree files' + \
                                  'DEFAULT: all trees in tree file')

    # validation analysis mode
    validation_parser = subparsers.add_parser('validation', help='validation analysis')
    validation_parser.add_argument('-i', '--iterations', metavar='numTimes', type=int, nargs=1, \
                                  help='execute the complete discovery analysis numTimes times,' +
                                  'taking numTimes samples of the tree file')
    validation_parser.add_argument('-t', '--tree', metavar='N', type=int, nargs='+',
                                  help='specify tree file(s)')
    validation_parser.add_argument('-s', '--settings', metavar='settingsFile', type=file, nargs=1, \
                                  help='specify settings file relative path, DEFAULT: settings')
    validation_parser.add_argument('-a', '--associations', metavar='associationsFile', type=file, nargs=1, \
                                   help='specify associations file relative path, DEFAULT: associations')
    validation_parser.add_argument('-th', '--theta', metavar='theatValue', type=float, nargs=1, \
                                   help='settings theta value')
    validation_parser.add_argument('-n', '--numtrees', metavar='numTree', type=int, nargs='+', \
                                  help='the list of numbers of trees to be sampled from tree files' + \
                                  'DEFAULT: all trees in tree file')

    # cleanup
    cleanup_parser = subparsers.add_parser('cleanup', help='restore initial configuration, ' + \
                                           'WARNING: all results in project folder will be lost, ' + \
                                           'move files out of this directory to save them.')

    args = parser.parse_args()
    print args
    return args

def main():
    args = parseArgs()
    if args.command == 'discovery':
        print '---DISCOVERY ANALYSIS---'

    if args.command == 'validation':
        print '---VALIDATION ANALYSIS---'
    if args.command == 'cleanup':
        print 'Cleaning...'

if __name__ == '__main__':
    main()
