import sys
import os
import glob
import src.iterator as iterator
import src.processStemOut as processStemOut

class ValidationCommand:
    def __init__(self):
        pass
    def execute(self, args):
        print '\n#################################'
        print '###### VALIDATION ANALYSIS ######'
        print '#################################\n'

        if args.tree:
            validation = iterator.Iterator([args.tree], numRuns=1, \
                                          numTrees=None, settings=args.settings[0], maxTrees=None, \
                                          verbose=args.verbose, isValidation=True, associations=args.associations[0], \
                                          quietWarnings=args.quiet)
            validation.printSettings()
            validation.run()
        elif args.directory:
            directory = args.directory[0]
            if not os.path.isdir(directory):
                print "ERROR: directory '" + directory + "' not found in SpedeSTEM directory.\n"
                sys.exit()

            print "Reading files from '" + directory + "' directory...\n"
            treeList = []
            for tree in glob.glob(directory + "/" + "*.tre"):
                treeList.append([tree])

            validation = iterator.Iterator(treeList, numRuns=1, \
                                          numTrees=None, settings=args.settings[0], maxTrees=None, \
                                          verbose=args.verbose, isValidation=True, associations=args.associations[0], \
                                          quietWarnings=args.quiet)
            validation.printSettings()
            validation.run()


        # process the stem output
        print "Completing Analysis...",
        processor = processStemOut.ProcessStemOut()
        processor.rawOutput()
        processor.calculateWilik()
        print "See 'results.txt' and 'itTable.txt' files\n"
