import unittest
import cStringIO
from repVariationFinder import RepVariationFinder


class Test_write(unittest.TestCase):
    def setUp(self):
        self.rvf = RepVariationFinder()

    def test_noDiffs(self):
        matrix = '''
begin data
[tree 1]
Matrix

sp1 AACTGC
sp2 AACTGC
sp3 AACTGC
;
begin data
[tree 2]
Matrix

sp1 TCGA
sp2 TCGA
sp3 TCGA
;
begin data
[tree 3]
Matrix

sp1 CGTCAA
sp2 CGTCAA
sp3 CGTCAA
;
'''

        matrix2 = '''
[Variable Sites: 0]
begin data
[tree 1]
Matrix

sp1 AACTGC
sp2 AACTGC
sp3 AACTGC
;
[Variable Sites: 0]
begin data
[tree 2]
Matrix

sp1 TCGA
sp2 TCGA
sp3 TCGA
;
[Variable Sites: 0]
begin data
[tree 3]
Matrix

sp1 CGTCAA
sp2 CGTCAA
sp3 CGTCAA
;
'''

        contents_in = cStringIO.StringIO(matrix)
        contents_out = cStringIO.StringIO()
        self.rvf.read(contents_in)
        self.rvf.write(contents_out)

        contents_out.seek(0)
        results = contents_out.read()

        # self.assertEqual(results, matrix)
        self.assertMultiLineEqual(results, matrix2)

    def test_severalDiffs(self):
        matrix = '''
begin data
[tree 1]
Matrix

sp1 ATCTGC
sp2 AACTGC
sp3 AACTGC
;
begin data
[tree 2]
Matrix

sp1 TCGA
sp2 GACA
sp3 TCGT
;
begin data
[tree 3]
Matrix

sp1 CGTCAG
sp2 CGTCAA
sp3 TGTCCA
;
'''

        matrix2 = '''
[Variable Sites: 4]
begin data
[tree 2]
Matrix

sp1 TCGA
sp2 GACA
sp3 TCGT
;
[Variable Sites: 3]
begin data
[tree 3]
Matrix

sp1 CGTCAG
sp2 CGTCAA
sp3 TGTCCA
;
[Variable Sites: 1]
begin data
[tree 1]
Matrix

sp1 ATCTGC
sp2 AACTGC
sp3 AACTGC
;
'''

        contents_in = cStringIO.StringIO(matrix)
        contents_out = cStringIO.StringIO()
        self.rvf.read(contents_in)
        self.rvf.write(contents_out)

        contents_out.seek(0)
        results = contents_out.read()

        self.assertMultiLineEqual(results, matrix2)

    def test_ignoreOutsideMatrix(self):
        file_in = '''this should be ignored

begin data
[tree 1]
Matrix

sp1 ATCTGC
sp2 AACTGC
sp3 AACTGC
;
; some stuff
more stuff
begin data
[tree 2]
Matrix

sp1 TCGA
sp2 GACA
sp3 TCGT
;
; This should be ok too: MATRIX
begin data
[tree 3]
Matrix

sp1 CGTCAG
sp2 CGTCAA
sp3 TGTCCA
;
more crap at the end
'''
        file_out = '''this should be ignored

[Variable Sites: 4]
begin data
[tree 2]
Matrix

sp1 TCGA
sp2 GACA
sp3 TCGT
;
; This should be ok too: MATRIX
[Variable Sites: 3]
begin data
[tree 3]
Matrix

sp1 CGTCAG
sp2 CGTCAA
sp3 TGTCCA
;
more crap at the end
[Variable Sites: 1]
begin data
[tree 1]
Matrix

sp1 ATCTGC
sp2 AACTGC
sp3 AACTGC
;
; some stuff
more stuff
'''
        contents_in = cStringIO.StringIO(file_in)
        contents_out = cStringIO.StringIO()
        self.rvf.read(contents_in)
        self.rvf.write(contents_out)

        contents_out.seek(0)
        results = contents_out.read()

        self.assertEqual(self.rvf._startByte, 23)
        self.assertMultiLineEqual(results, file_out)


class Test_read(unittest.TestCase):
    ''' Test for file input RepVariationFinder.read '''
    def setUp(self):
        self.rvf = RepVariationFinder()

    def test_initialConfig(self):
        self.assertEquals(len(self.rvf.replicateToCount), 0)

    def test_byteCount(self):
        matrix = '''begin data
        Matrix

            sp1 AACTGC
            sp2 AACTGC
            sp3 AACTGC
            ;

            begin data
            Matrix

            sp1 TCGA
            sp2 TCGA
            sp3 TCGA
            ;
            begin data
            Matrix

            sp1 CGTCAA
            sp2 CGTCAA
            sp3 CGTCAA
            ;
            '''
        contents = cStringIO.StringIO(matrix)
        self.rvf.read(contents)
        self.assertEquals(contents.tell() - 1,
                          self.rvf.replicateToLocation[2][1])

    def test_noDiffs(self):
        matrix = '''
        begin data
        Matrix

            sp1 AACTGC
            sp2 AACTGC
            sp3 AACTGC
            ;
        begin data
            Matrix

            sp1 TCGA
            sp2 TCGA
            sp3 TCGA
            ;
        begin data
            Matrix

            sp1 CGTCAA
            sp2 CGTCAA
            sp3 CGTCAA
            ;
            '''
        contents = cStringIO.StringIO(matrix)
        self.rvf.read(contents)

        compare = {0: 0, 1: 0, 2: 0}
        self.assertDictEqual(self.rvf.replicateToCount, compare)

    def test_severalDiffs(self):
        matrix = '''
        begin data
        Matrix

            sp1 ATCTGC
            sp2 AACTGC
            sp3 AACTGC
            ;
        begin data
            Matrix

            sp1 TCGA
            sp2 GACA
            sp3 TCGT
            ;
        begin data
            Matrix

            sp1 CGTCAG
            sp2 CGTCAA
            sp3 TGTCCA
            ;
            '''
        contents = cStringIO.StringIO(matrix)
        self.rvf.read(contents)

        compare = {0: 1, 1: 4, 2: 3}
        self.assertDictEqual(self.rvf.replicateToCount, compare)

    def test_ignoreOutsideMatrix(self):
        matrix = ''' this should be ignored
        begin data
        blah blah

        Matrix

            sp1 ATCTGC
            sp2 AACTGC
            sp3 AACTGC
            ;
            ; some stuff
            more stuff

        begin data
        blah2 blah2

            Matrix

            sp1 TCGA
            sp2 GACA
            sp3 TCGT
            ;
            ; This should be ok too: MATRIX

        begin data
        blah3 blah3

            Matrix

            sp1 CGTCAG
            sp2 CGTCAA
            sp3 TGTCCA
            ;
            more crap at the end
            '''
        contents = cStringIO.StringIO(matrix)
        self.rvf.read(contents)

        compare = {0: 1, 1: 4, 2: 3}
        self.assertDictEqual(self.rvf.replicateToCount, compare)


class Test_countVariationInMatrix(unittest.TestCase):
    ''' Test for file input to RepVariationFinder.countVariationInMatrix() '''
    def setUp(self):
        self.rvf = RepVariationFinder()

    def test_noDiff(self):
        matrix = '''
            matrix

            sp1 AACTGC
            sp2 AACTGC
            sp3 AACTGC
            ;
            '''
        contents = cStringIO.StringIO(matrix)
        count = self.rvf.countVariationInMatrix(contents)

        self.assertEquals(count, 0)

    def test_oneDiff(self):
        matrix = '''
            matrix

            sp1 AACTGC
            sp2 ACCTGC
            sp3 AACTGC
            ;
            '''
        contents = cStringIO.StringIO(matrix)
        count = self.rvf.countVariationInMatrix(contents)

        self.assertEquals(count, 1)

    def test_allDiff(self):
        matrix = '''
            matrix

            sp1 AACCCC
            sp2 ACCTGT
            sp3 TAGTGC
            ;
            '''
        contents = cStringIO.StringIO(matrix)
        count = self.rvf.countVariationInMatrix(contents)

        self.assertEquals(count, 6)

    def test_remainderAfterCount(self):
        matrix = '''
            this shouldn't matter
            matrix

            sp1 AACCCC
            sp2 ACCTGT
            sp3 TAGTGC
            ;
            This should be preserved
            '''

        contents = cStringIO.StringIO(matrix)
        self.rvf.countVariationInMatrix(contents)

        self.assertEquals('This should be preserved', contents.read().strip())


if __name__ == "__main__":
    unittest.main()
