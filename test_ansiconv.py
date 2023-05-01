


import unittest
from ansiconv import *
import io

class TestCase(unittest.TestCase):

    def test_basic1(self):

        idata1 = b"\x0c"
        idata2 = b"ABCDEF\x0a"
        idata3 = b"GHIJKL\x0a"
        fh = io.BytesIO(idata1 + idata2 + idata3)

        odata1 = b"1" + b" "*30
        odata2 = b"+" + b"ABCDEF" + b" "*24
        odata3 = b" " + b"GHIJKL" + b" "*24        
        odata4 = b" " + b" "*30

        initialize(30)
        ret = get_record(fh)
        self.assertEqual(odata1,ret)
        ret = get_record(fh)
        self.assertEqual(odata2,ret)
        ret = get_record(fh)
        self.assertEqual(odata3,ret)
        ret = get_record(fh)
        self.assertEqual(odata4,ret)
        ret = get_record(fh)
        self.assertEqual(None,ret)

    def test_basic2(self):

        fh = io.BytesIO(b"")
        initialize(30)
        ret = get_record(fh)
        self.assertEqual(None,ret)
        ret = get_record(fh)
        self.assertEqual(None,ret)
        
    def test_basic3(self):

        idata1 = b"\x0c"
        idata2 = b"ABCDEF\x0a"
        idata3 = b"\x0c"
        idata4 = b"GHIJKL\x0a"
        
        fh = io.BytesIO(idata1 + idata2 + idata3 + idata4)

        odata1 = b"1" + b" "*30
        odata2 = b"+" + b"ABCDEF" + b" "*24
        odata3 = b" " + b" "*30
        odata4 = b"1" + b" "*30
        odata5 = b"+" + b"GHIJKL" + b" "*24        
        odata6 = b" " + b" "*30

        initialize(30)
        ret = get_record(fh)
        self.assertEqual(odata1,ret)
        ret = get_record(fh)
        self.assertEqual(odata2,ret)
        ret = get_record(fh)
        self.assertEqual(odata3,ret)
        ret = get_record(fh)
        self.assertEqual(odata4,ret)
        ret = get_record(fh)
        self.assertEqual(odata5,ret)
        ret = get_record(fh)
        self.assertEqual(odata6,ret)
        ret = get_record(fh)
        self.assertEqual(None,ret)
        
if __name__ == "__main__":
    unittest.main()
