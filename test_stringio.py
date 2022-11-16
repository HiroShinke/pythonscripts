

import io
import unittest
import sys

class XXXXX(unittest.TestCase):

    def test_stringio_print1(self):
        with io.StringIO() as fh:
            print("xxxxx",file=fh)
            self.assertEqual("xxxxx\n",fh.getvalue())

    def test_stringio_print2(self):
        with io.StringIO(newline="\r\n") as fh:
            print("xxxxx",file=fh)
            self.assertEqual("xxxxx\r\n",fh.getvalue())

    def test_stringio_print3(self):
        with io.StringIO(newline="\r\n") as fh:
            sys.stdout = fh
            print("xxxxx")
            self.assertEqual("xxxxx\r\n",fh.getvalue())
        sys.stdout = sys.__stdout__

    def test_stringio_write1(self):
        with io.StringIO() as fh:
            fh.write("xxxxx\n")
            self.assertEqual("xxxxx\n",fh.getvalue())

    def test_stringio_write2(self):
        with io.StringIO(newline="\r\n") as fh:
            fh.write("xxxxx\n")
            self.assertEqual("xxxxx\r\n",fh.getvalue())
            
    def test_stringio_read1(self):
        text = "aaaaaa\nbbbbb\nccccc\n"
        with io.StringIO(text) as fh:
            text2 = fh.read()
            self.assertEqual(text,text2)

    def test_stringio_read1_1(self):
        text = "aaaaaa\nbbbbb\nccccc\n"
        textcrlf = "aaaaaa\r\nbbbbb\r\nccccc\r\n"        
        with io.StringIO(text,newline="\r\n") as fh:
            text2 = fh.read()
            self.assertEqual(textcrlf,text2)
            
    def test_stringio_read2(self):
        textcrlf = "aaaaaa\r\nbbbbb\r\nccccc\r\n"
        with io.StringIO(textcrlf) as fh:
            text2 = fh.read()
            self.assertEqual(textcrlf,text2)

    def test_stringio_read3(self):
        textcrlf = "aaaaaa\r\nbbbbb\r\nccccc\r\n"
        with io.StringIO(textcrlf,newline="\n") as fh:
            text2 = fh.read()
            self.assertEqual(textcrlf,text2)

    def test_bytesio_write1(self):
        with io.BytesIO() as fh:
            fh.write(b"xxxxx\n")
            self.assertEqual(b"xxxxx\n",fh.getvalue())

    def test_bytesio_write1(self):
        with io.BytesIO() as fh:
            fh.write(b"xxxxx\r\n")
            self.assertEqual(b"xxxxx\r\n",fh.getvalue())

    def test_bytesio_read1(self):
        bseq = b"aaaaaa\nbbbbb\nccccc\n"
        with io.BytesIO(bseq) as fh:
            bseq2 = fh.read()
            self.assertEqual(bseq,bseq2)

if __name__ == "__main__":
    unittest.main()






    



