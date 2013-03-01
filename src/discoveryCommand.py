import glob
import os
import sys
import src.iterator as iterator
import src.processStemOut as processStemOut

class DiscoveryCommand:
    def __init__(self):
        pass
    def execute(self, args):
        print '\n################################'
        print '###### DISCOVERY ANALYSIS ######'
        print '################################\n'

        if args.tree:
            # check here for settings file, tree files, maybe scan the files for correct formatting
            discovery = iterator.Iterator([args.tree], numRuns=1, \
                                          numTrees=None, settings=args.settings[0], maxTrees=None, \
                                          verbose=args.verbose, quietWarnings=args.quiet)
            discovery.printSettings()
            discovery.run()

        elif args.directory:
            directory = args.directory[0]
            if not os.path.isdir(directory):
                print "ERROR: directory '" + directory + "' not found in SpedeSTEM directory.\n"
                sys.exit()

            print "Reading files from '" + directory + "' directory...\n"
            treeList = []
            for tree in glob.glob(directory + "/" + "*.tre"):
                treeList.append([tree])

            discovery = iterator.Iterator(treeList, numRuns=1, \
                                          numTrees=None, settings=args.settings[0], maxTrees=None, \
                                          verbose=args.verbose, quietWarnings=args.quiet)
            discovery.printSettings()
            discovery.run()

        # process the stem output
        print "Completing Analysis...",
        processor = processStemOut.ProcessStemOut()
        processor.rawOutput()
        processor.calculateWilik()
        print "See 'results.txt' and 'itTable.txt' files\n"
