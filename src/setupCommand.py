import src.cleanTrees as cleanTrees
import src.parseBeast as parseBeast
import src.distributeTrees as distributeTrees

class SetupCommand:
    def __init__(self):
        pass
    def execute(self, args):
        print '\n################################'
        print '####### Performing Setup #######'
        print '################################\n'

        prefix = None
        if args.prefix:
            prefix = args.prefix[0]

        scalingFile = None
        if args.clean:
            if args.scalingFile:
                scalingFile = args.scalingFile[0]
            # clean trees and prefix each with scaling factors if file provided
            cleanTrees.CleanTrees(args.clean, scalingFile, sigfigs=8, prefix=prefix)

        if args.traits:
            # convert beast formatted traits file to stem settings
            parseBeast.ParseBeast(settingsIn=args.traits[0], theta=args.theta[0])

        if args.distribute:
            distributeTrees.DistributeTrees(args.distribute, prefix=prefix)
