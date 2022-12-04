

import unittest
from pathlib import Path
import subprocess
import os
import shutil

def makeFile(p,*lines):
    Path(p).parent.mkdir(exist_ok=True,parents=True)
    with open(p,"w") as fh:
        fh.write("\n".join(lines))

def makeFiles(files):
    for p,*c in files: makeFile(p,*c)
        
class TestAnalyzer(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        shutil.rmtree("testanalyze")

    def test_basic(self):

        FILES = [
            ("testanalyze/base/a",
             "call b",
             "call c"
             ),
            ("testanalyze/base/b",
             "call b1",
             "call d lib"
             ),
            ("testanalyze/lib/c",
             "call c1",
             "call d"
             ),
            ("testanalyze/base/d",
             ),
            ("testlist.txt",
             "type1 a lib",
             "type1 b"
             )
        ]

        makeFiles(FILES)

        ret = subprocess.call( "python3 analyzer.py "
                               "--src testanalyze "
                               "--out testout.txt "
                               "--start testlist.txt".split(" "))
        self.assertEqual(0,ret)
        
        CONTENTS = """\
Start: type1,a,lib -> testanalyze/base/a
Rel: testanalyze/base/a -> ('call', 'b', Env())
Rel: testanalyze/base/a -> ('call', 'c', Env())
Start: call,b,lib -> testanalyze/base/b
Rel: testanalyze/base/b -> ('call', 'b1', Env())
Rel: testanalyze/base/b -> ('call', 'd', Env('lib'))
Start: call,b1,lib -> None
Start: call,d,lib;lib -> testanalyze/base/d
Start: call,c,lib -> testanalyze/lib/c
Rel: testanalyze/lib/c -> ('call', 'c1', Env())
Rel: testanalyze/lib/c -> ('call', 'd', Env())
Start: call,c1,lib -> None
Start: call,d,lib -> testanalyze/base/d
Start: type1,b, -> testanalyze/base/b
Rel: testanalyze/base/b -> ('call', 'b1', Env())
Rel: testanalyze/base/b -> ('call', 'd', Env('lib'))
Start: call,b1, -> None
"""
        self.maxDiff = 2000
        
        with open("testout.txt") as fh:
            self.assertEqual(CONTENTS,fh.read())
        
if __name__ == "__main__":
    unittest.main()
            
