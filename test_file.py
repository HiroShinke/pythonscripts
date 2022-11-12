


import unittest
import os

blist = [
    b"aaaaaa",
    b"bbbbbb",    
    b"cccccc"
]

bincontents_lf   = b"".join( l + b"\n"   for l in blist )
bincontents_crlf = b"".join( l + b"\r\n" for l in blist )

tlist = [ str(b,"cp932") for b in blist ]

textcontents_lf   = "".join( l + "\n"   for l in tlist )
textcontents_crlf = "".join( l + "\r\n" for l in tlist )

class TestCases(unittest.TestCase):

    def assertFileEqual(self,p,q):
        with open(p,"rb") as fh: contp = fh.read()
        with open(q,"rb") as fh: contq = fh.read()
        self.assertEqual(contp,contq)
    
    def setUp(self):
    
        with open("testlf.txt","wb") as fh:
            fh.write(bincontents_lf)
        with open("testcrlf.txt","wb") as fh:
            fh.write(bincontents_crlf)

    def tearDown(self):
        os.unlink("testlf.txt")
        os.unlink("testcrlf.txt")

    def test_readbin(self):
        with open("testlf.txt","rb") as fh:
            lines = fh.readlines()
            self.assertEqual(bincontents_lf, b"".join(lines))

    def test_readlines_text_lf(self):
        with open("testlf.txt","r") as fh:
            lines = fh.readlines()
            self.assertEqual(textcontents_lf, "".join(lines))

    def test_readlines_text_crlf1(self):
        with open("testcrlf.txt","r") as fh:
            lines = fh.readlines()
            self.assertFalse(textcontents_crlf == "".join(lines))

    def test_readlines_text_crlf2(self):
        with open("testcrlf.txt","r",newline="\r\n") as fh:
            lines = fh.readlines()
            self.assertEqual(textcontents_crlf, "".join(lines))

    def test_read_text_lf1(self):
        with open("testlf.txt","r") as fh:
            contents = fh.read()
            self.assertEqual(textcontents_lf, contents)

    def test_read_splitlines_lf(self):
        with open("testlf.txt","r") as fh:
            contents = fh.read()
            lines = contents.splitlines()
            self.assertEqual(tlist,lines)

    def test_read_splitlines_crlf(self):
        with open("testcrlf.txt","r") as fh:
            contents = fh.read()
            lines = contents.splitlines()
            self.assertEqual(tlist,lines)

    def test_write_lines_lf(self):
        with open("tmpxxx.txt","w") as fh:
            fh.write(textcontents_lf)

        self.assertFileEqual("testlf.txt","tmpxxx.txt")
        os.unlink("tmpxxx.txt")

    def test_write_lines_crlf1(self):
        with open("tmpxxx.txt","w") as fh:
            fh.write(textcontents_crlf)

        self.assertFileEqual("testcrlf.txt","tmpxxx.txt")
        os.unlink("tmpxxx.txt")

    def test_write_lines_crlf2(self):
        with open("tmpxxx.txt","w",newline="\r\n") as fh:
            fh.write(textcontents_lf)

        self.assertFileEqual("testcrlf.txt","tmpxxx.txt")
        os.unlink("tmpxxx.txt")

    def test_print_lines_lf(self):
        with open("tmpxxx.txt","w") as fh:
            for l in tlist:
                print(l,file=fh)

        self.assertFileEqual("testlf.txt","tmpxxx.txt")
        os.unlink("tmpxxx.txt")

    def test_print_lines_crlf1(self):
        with open("tmpxxx.txt","w") as fh:
            for l in tlist:
                print(l,file=fh,end="\r\n")

        self.assertFileEqual("testcrlf.txt","tmpxxx.txt")
        os.unlink("tmpxxx.txt")

    def test_print_lines_crlf2(self):
        with open("tmpxxx.txt","w",newline="\r\n") as fh:
            for l in tlist:
                print(l,file=fh)

        self.assertFileEqual("testcrlf.txt","tmpxxx.txt")
        os.unlink("tmpxxx.txt")
        
            
if __name__ == "__main__":
    unittest.main()

    
