

import unittest
from ansiconv import *
import io
import argparse
import subprocess
from ctypes import *
import sys
import tempfile
import os

target = None

class TestCase(unittest.TestCase):

    def setUp(self):
        global libansi
        global libc
        if target:
            args = "gcc ansiconv.c -shared -o libansiconv.so".split(" ")
            subprocess.run(args)
            self.libansi = cdll.LoadLibrary("libansiconv.so")
            self.libc    = cdll.LoadLibrary("libSystem.B.dylib") 
    
    def assertEqualRecord(self,idata,odata):
        if target is None:
            fh = io.BytesIO(b"".join(idata))
            initialize(31)
            for od in odata:
                ret = get_record(fh)
                self.assertEqual(od,ret)
        else:
            fname = f"xxxxyyyy"
            with open(fname,"wb") as gh:
                gh.write(b"".join(idata))

            self.libc.fopen.restype = c_void_p
            fnamebuff = create_string_buffer(fname.encode("cp932"))
            ret = self.libc.fopen(fnamebuff,"r")
            filep = c_void_p(ret)
            self.libansi.initialize()
            for od in odata:
                bytesp = create_string_buffer(b" "*31)
                ret = self.libansi.make_record(bytesp,c_ulong(31),filep)
                if ret == 1:
                    self.assertEqual(od,bytesp.value)
                else:
                    self.assertEqual(od,None)
                
            self.libc.fclose(filep)
            os.unlink(fname)

    def test_basic1(self):

        idata = [
            b"\x0c",
            b"ABCDEF\x0a",
            b"GHIJKL\x0a"
        ]

        odata = [
            b"1" + b" "*30,
            b"+ABCDEF" + b" "*24,
            b" " + b"GHIJKL" + b" "*24,
            b" " + b" "*30
        ]

        self.assertEqualRecord(idata,odata)
        

    def test_basic2(self):

        odata = [
            None,
            None
            ]

        self.assertEqualRecord([],odata)
        
    def test_basic3(self):

        idata = [
            b"\x0c",
            b"ABCDEF\x0a",
            b"\x0c",
            b"GHIJKL\x0a"
        ]
        
        odata = [
            b"1" + b" "*30,
            b"+" + b"ABCDEF" + b" "*24,
            b" " + b" "*30,
            b"1" + b" "*30,
            b"+" + b"GHIJKL" + b" "*24,
            b" " + b" "*30
            ]

        self.assertEqualRecord(idata,odata)


    def test_0d1(self):

        idata = [
            b"\x0c\x0d\x0d",
            b"ABCDEF\x0a",
            b"GHIJKL\x0a"
            ]

        odata = [
            b"1" + b" "*30,
            b"+ABCDEF" + b" "*24,
            b" " + b"GHIJKL" + b" "*24,
            b" " + b" "*30
            ]

        self.assertEqualRecord(idata,odata)

    def test_0d2(self):

        idata = [
            b"\x0c",
            b"ABCDEF\x0a\x0d\x0d",
            b"GHIJKL\x0a"
            ]

        odata = [
            b"1" + b" "*30,
            b"+ABCDEF" + b" "*24,
            b" " + b"GHIJKL" + b" "*24,
            b" " + b" "*30
            ]

        self.assertEqualRecord(idata,odata)

    def test_0d3(self):

        idata = [
            b"\x0c",
            b"ABCDEF\x0a",
            b"GHIJKL\x0d\x0d\x0a"
            ]

        odata = [
            b"1" + b" "*30,
            b"+ABCDEF" + b" "*24,
            b" " + b"GHIJKL" + b" "*24,
            b" " + b" "*30
            ]

        self.assertEqualRecord(idata,odata)

    def test_0d4(self):

        idata = [
            b"\x0c",
            b"ABCDEF\x0a",
            b"GHIJKL\x0a\x0d\x0d"
            ]

        odata = [
            b"1" + b" "*30,
            b"+ABCDEF" + b" "*24,
            b" " + b"GHIJKL" + b" "*24,
            b" " + b" "*30
            ]

        self.assertEqualRecord(idata,odata)

    def test_lfcount1(self):

        idata = [
            b"\x0c\x0a",
            b"ABCDEF\x0a",
            b"GHIJKL\x0a"
            ]

        odata = [
            b"1" + b" "*30,
            b" ABCDEF" + b" "*24,
            b" " + b"GHIJKL" + b" "*24,
            b" " + b" "*30
            ]

        self.assertEqualRecord(idata,odata)

    def test_lfcount2(self):

        idata = [
            b"\x0c\x0a\x0a",
            b"ABCDEF\x0a",
            b"GHIJKL\x0a"
            ]

        odata = [
            b"1" + b" "*30,
            b"0ABCDEF" + b" "*24,
            b" " + b"GHIJKL" + b" "*24,
            b" " + b" "*30
            ]

        self.assertEqualRecord(idata,odata)

    def test_lfcount3(self):

        idata = [
            b"\x0c\x0a\x0a\x0a",
            b"ABCDEF\x0a",
            b"GHIJKL\x0a"
            ]

        odata = [
            b"1" + b" "*30,
            b"-ABCDEF" + b" "*24,
            b" " + b"GHIJKL" + b" "*24,
            b" " + b" "*30
            ]

        self.assertEqualRecord(idata,odata)

    def test_lfcount4(self):

        idata = [
            b"\x0c\x0a\x0a\x0a\x0a",
            b"ABCDEF\x0a",
            b"GHIJKL\x0a"
            ]

        odata = [
            b"1" + b" "*30,
            b"-" + b" "*30,
            b" ABCDEF" + b" "*24,
            b" " + b"GHIJKL" + b" "*24,
            b" " + b" "*30
            ]

        self.assertEqualRecord(idata,odata)
        
    def test_lfcount5(self):

        idata = [
            b"\x0c\x0a",
            b"ABCDEF\x0a\x0a",
            b"GHIJKL\x0a"
            ]

        odata = [
            b"1" + b" "*30,
            b" ABCDEF" + b" "*24,
            b"0" + b"GHIJKL" + b" "*24,
            b" " + b" "*30
            ]

        self.assertEqualRecord(idata,odata)


    def test_lfcount6(self):

        idata = [
            b"\x0c\x0a",
            b"ABCDEF\x0a\x0a\x0a",
            b"GHIJKL\x0a"
            ]

        odata = [
            b"1" + b" "*30,
            b" ABCDEF" + b" "*24,
            b"-" + b"GHIJKL" + b" "*24,
            b" " + b" "*30
            ]

        self.assertEqualRecord(idata,odata)

    def test_lfcount7(self):

        idata = [
            b"\x0c\x0a",
            b"ABCDEF\x0a\x0a\x0a\x0a",
            b"GHIJKL\x0a"
            ]

        odata = [
            b"1" + b" "*30,
            b" ABCDEF" + b" "*24,
            b"-" + b" "*30,
            b" " + b"GHIJKL" + b" "*24,
            b" " + b" "*30
            ]

        self.assertEqualRecord(idata,odata)


    def test_lfcount8(self):

        idata = [
            b"\x0c",
            b"ABCDEF\x0a",
            b"GHIJKL\x0a\x0a"
            ]

        odata = [
            b"1" + b" "*30,
            b"+ABCDEF" + b" "*24,
            b" " + b"GHIJKL" + b" "*24,
            b"0" + b" "*30
            ]

        self.assertEqualRecord(idata,odata)

    def test_lfcount9(self):

        idata = [
            b"\x0c",
            b"ABCDEF\x0a",
            b"GHIJKL\x0a\x0a\x0a"
            ]

        odata = [
            b"1" + b" "*30,
            b"+ABCDEF" + b" "*24,
            b" " + b"GHIJKL" + b" "*24,
            b"-" + b" "*30
            ]

        self.assertEqualRecord(idata,odata)

    def test_lfcount10(self):

        idata = [
            b"\x0c",
            b"ABCDEF\x0a",
            b"GHIJKL\x0a\x0a\x0a\x0a"
            ]

        odata = [
            b"1" + b" "*30,
            b"+ABCDEF" + b" "*24,
            b" " + b"GHIJKL" + b" "*24,
            b"-" + b" "*30,
            b" " + b" "*30            
            ]

        self.assertEqualRecord(idata,odata)

        
if __name__ == "__main__":

    print(f"{sys.argv}")
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--target")
    args,not_parsed = parser.parse_known_args()

    target = args.target
    sys.argv = [ sys.argv[0] ] + not_parsed
    
    unittest.main()
