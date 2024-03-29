


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

    def test_keyword31(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-f", "--form")
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


    def test_nargs(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--form", "-f", nargs='*')
        args = parser.parse_args("-f a b c".split())
        self.assertEqual(["a","b","c"],args.form)

    def test_nargs2(self):
        def splitComma(s): return re.split(r",",s)        
        parser = argparse.ArgumentParser()
        parser.add_argument("--form", "-f", type=splitComma, nargs='*')
        args = parser.parse_args("-f a,A b,B c,C".split())
        self.assertEqual([["a","A"],["b","B"],["c","C"]],args.form)
        
    def test_shortoptions1(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-f", action="store_true")
        parser.add_argument("-g", action="store_true")
        parser.add_argument("-i", action="store_true")
        args = parser.parse_args(["-fgi"])
        self.assertEqual(True,args.f)
        self.assertEqual(True,args.g)
        self.assertEqual(True,args.i)

    def test_shortoptions2(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-f")
        parser.add_argument("-g", action="store_true")
        parser.add_argument("-i", action="store_true")
        args = parser.parse_args(["-faaa","-gi"])
        self.assertEqual("aaa",args.f)
        self.assertEqual(True,args.g)
        self.assertEqual(True,args.i)

    def test_shortoptions3(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-f", dest="from_file")
        parser.add_argument("-g", action="store_true")
        parser.add_argument("-i", action="store_true")
        args = parser.parse_args(["-faaa","-gi"])
        self.assertEqual("aaa",args.from_file)
        self.assertEqual(True,args.g)
        self.assertEqual(True,args.i)
        
    def test_positional(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("in_file")
        parser.add_argument("out_file")
        args = parser.parse_args(["a","b"])
        self.assertEqual("a",args.in_file)
        self.assertEqual("b",args.out_file)

        
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

