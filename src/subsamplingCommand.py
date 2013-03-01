import src.sample as sample

class SubsamplingCommand:
    def __init__(self):
        pass
    def execute(self, args):
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
