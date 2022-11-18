


import argparse
import unittest
import io
import re

class ArgParseTests(unittest.TestCase):

    def test_keyword1(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-f",type=str,action="store")
        args = parser.parse_args(["-f","xxx"])
        self.assertEqual("xxx",args.f)

    def test_keyword2(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-f")
        args = parser.parse_args(["-f","xxx"])
        self.assertEqual("xxx",args.f)

    def test_keyword3(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--form", "-f")
        args = parser.parse_args(["-f","xxx"])
        self.assertEqual("xxx",args.form)

    def test_keyword4(self):
        def splitComma(s): return re.split(r",",s)
        parser = argparse.ArgumentParser()
        parser.add_argument("--form", "-f", type=splitComma)
        args = parser.parse_args(["-f","10,20,30"])
        self.assertEqual(["10","20","30"],args.form)

    def test_append(self):
        def splitComma(s): return re.split(r",",s)
        parser = argparse.ArgumentParser()
        parser.add_argument("--form", "-f", action="append")
        args = parser.parse_args("-f 10 -f 20 -f 30".split())
        self.assertEqual(["10","20","30"],args.form)

    def test_const(self):
        def splitComma(s): return re.split(r",",s)
        parser = argparse.ArgumentParser()
        parser.add_argument("--form", "-f", action="store_true")
        args = parser.parse_args(["-f"])
        self.assertEqual(True,args.form)

    def test_shortoptions(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-f", action="store_true")
        parser.add_argument("-g", action="store_true")
        parser.add_argument("-i", action="store_true")
        args = parser.parse_args(["-fgi"])
        self.assertEqual(True,args.f)
        self.assertEqual(True,args.g)
        self.assertEqual(True,args.i)

    def test_help1(self):
        parser = argparse.ArgumentParser( prog = "abc",
                                          description = "test for description",
                                          epilog = "test for epilog"
                                         )
        parser.add_argument("-f",type=str,action="store")
        sout = io.StringIO()
        args = parser.print_help(file=sout)
        help_message = """\
usage: abc [-h] [-f F]

test for description

options:
  -h, --help  show this help message and exit
  -f F

test for epilog
"""
        self.assertEqual(help_message,sout.getvalue())


    def test_help2(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--from_file", "-f", type=str,action="store")
        sout = io.StringIO()
        args = parser.print_help(file=sout)
        help_message = """\
usage: test_argparse.py [-h] [--from_file FROM_FILE]

options:
  -h, --help            show this help message and exit
  --from_file FROM_FILE, -f FROM_FILE
"""
        self.assertEqual(help_message,sout.getvalue())


        
if __name__ == "__main__":
    unittest.main()

