

from parsing import *
import unittest


def charP(c):
    def func(s):
        return s == c
    return Pred(func)

class TestParsing(unittest.TestCase):

    def test_basic(self):

        parser = Seq(charP("a"),charP("b"),charP("c"))

        ret = parser.parse("abc",0)
        self.assertEqual(Success(["a","b","c"],3),ret)

        ret = parser.parse("abe",0)
        self.assertEqual(Failure(2),ret)


    def test_add(self):

        parser = charP("a") + charP("b") + charP("c")

        ret = parser.parse("abc",0)
        self.assertEqual(Success(["a","b","c"],3),ret)

        ret = parser.parse("abe",0)
        self.assertEqual(Failure(2),ret)


    def test_or1(self):

        parser = charP("a") | charP("b") |  charP("c")

        ret = parser.parse("abc",0)
        self.assertEqual(Success("a",1),ret)

        ret = parser.parse("bbb",0)
        self.assertEqual(Success("b",1),ret)

        ret = parser.parse("ccc",0)
        self.assertEqual(Success("c",1),ret)
        
        ret = parser.parse("ebe",0)
        self.assertEqual(Failure(0),ret)


    def test_many1(self):

        parser = (charP("a") | charP("b") |  charP("c"))[3]

        ret = parser.parse("abc",0)
        self.assertEqual(Success(["a","b","c"],3),ret)

        ret = parser.parse("bbb",0)
        self.assertEqual(Success(["b","b","b"],3),ret)

        ret = parser.parse("ccc",0)
        self.assertEqual(Success(["c","c","c"],3),ret)
        
        ret = parser.parse("abe",0)
        self.assertEqual(Failure(2),ret)


    def test_many2(self):

        parser = (charP("a") | charP("b") |  charP("c"))[...]

        ret = parser.parse("abc",0)
        self.assertEqual(Success(["a","b","c"],3),ret)

        ret = parser.parse("bbb",0)
        self.assertEqual(Success(["b","b","b"],3),ret)

        ret = parser.parse("ccc",0)
        self.assertEqual(Success(["c","c","c"],3),ret)
        
        ret = parser.parse("abe",0)
        self.assertEqual(Success(["a","b"],2),ret)

        

    def test_action(self):

        parser = ((charP("a") >> str.upper) + 
                  (charP("b") >> str.upper) + 
                  (charP("c") >> str.upper))
                 
        ret = parser.parse("abc",0)
        self.assertEqual(Success(["A","B","C"],3),ret)

        ret = parser.parse("abe",0)
        self.assertEqual(Failure(2),ret)
        

    def test_recursive(self):

        expr = Recursive()
        
        item = charP("1")
        expr <<= item + charP("+") + expr | item

        ret = expr.parse("1+1+1",0)
        self.assertEqual(Success(["1","+",["1","+","1"]],5),ret)

    def test_strP1(self):

        parser = strP("abc")

        ret = parser.parse("abc",0)
        self.assertEqual(Success("abc",3),ret)

        ret = parser.parse("abe",0)
        self.assertEqual(Failure(0),ret)


    def test_strP2(self):

        parser = strP("abc") + strP("def")

        ret = parser.parse("abcdef",0)
        self.assertEqual(Success(["abc","def"],6),ret)

        ret = parser.parse("abcxxx",0)
        self.assertEqual(Failure(3),ret)


    def test_regexpP1(self):

        parser = regexpP("abc")

        ret = parser.parse("abc",0)
        self.assertEqual(Success("abc",3),ret)

        ret = parser.parse("abe",0)
        self.assertEqual(Failure(0),ret)


    def test_regexpP2(self):

        parser = regexpP("abc") + regexpP("def")

        ret = parser.parse("abcdef",0)
        self.assertEqual(Success(["abc","def"],6),ret)

        ret = parser.parse("abcxxx",0)
        self.assertEqual(Failure(3),ret)

        
        
        
if __name__ == "__main__":
    unittest.main()

    
    

    
