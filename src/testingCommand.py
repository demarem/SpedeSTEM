import src.iterator as iterator
import src.processStemOut as processStemOut

class TestingCommand:
    def __init__(self):
        pass
    def execute(self, args):
        print '\n#################################'
        print '######### POWER TESTING #########'
        print '#################################\n'

        associations = ""
        if args.associations:
            associations = args.associations[0]
        # check for settings, tree files, associations, etc.
        validation = iterator.Iterator([args.tree], numRuns=args.replicates[0], \
                                      numTrees=args.loci[0], settings=args.settings[0], maxTrees=args.loci[0], \
                                      verbose=args.verbose, isValidation=args.validation, associations=associations, quietWarnings=args.quiet)
        validation.printSettings()
        validation.run()

        # process the stem output
        print "Completing Analysis...",
        processor = processStemOut.ProcessStemOut()
        processor.rawOutput()
        processor.calculateWilik(args.replicates[0])
        print "See 'results.txt' and 'itTable.txt' files\n"

        occurrences = processStemOut.ProcessStemOut(results="occurrenceResults.txt")
        occurrences.averageHighestLikelihoodByTips()
