

from parsing import *
import unittest
import operator


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

        
    def test_splicing(self):

        expr = Recursive()
        
        item = charP("1")
        expr <<= (item + charP("+") + expr).splicing() | item

        ret = expr.parse("1+1+1",0)
        self.assertEqual(Success(["1","+","1","+","1"],5),ret)

        ret = expr.parse("1+1+1+1",0)
        self.assertEqual(Success(["1","+","1","+","1","+","1"],7),ret)


    def test_expr(self):

        expr = Recursive()
        term = Recursive()
        
        item = charP("1")
        term <<= (item + charP("*") + term).splicing() | item
        expr <<= (term + charP("+") + expr).splicing() | term

        ret = expr.parse("1+1*1+1",0)
        self.assertEqual(Success(["1","+","1","*","1","+","1"],7),ret)

        term <<= item + charP("*") + term | item
        expr <<= term + charP("+") + expr | term

        ret = expr.parse("1+1*1+1",0)
        self.assertEqual(Success(["1","+",[["1","*","1"],"+","1"]],7),ret)


    def test_expr2(self):

        expr = Recursive()
        term = Recursive()

        opdict = {
            "+" : operator.add,
            "-" : operator.sub,            
            "*" : operator.mul,
            "/" : operator.truediv
            }

        def applyOp(v):
            match v:
                case (m,op,cont):
                    def func(acc,op2):
                        func = opdict[op2]
                        acc2 = func(acc,int(m))
                        return cont(acc2,op)
                    return func
                case m:
                    def func(acc,op2):
                        func = opdict[op2]
                        acc2 = func(acc,int(m))
                        return acc2
                    return func

        def evalMult(f):
            return f(1,"*")

        def evalAdd(f):
            return f(0,"+")
        
        item = charP("1")
        term <<= ( (item + regexpP(r"[*/]") + term) >> applyOp |
                   item >> applyOp )
        term2 = term >> evalMult
        expr <<= ( (term2 + regexpP(r"[\+\-]") + expr) >> applyOp  |
                   term2 >> applyOp )
        expr2 = expr >> evalAdd

        ret = expr2.parse("1+1*1+1",0)
        self.assertEqual(Success(3,7),ret)

        ret = expr2.parse("1-1*1+1",0)
        self.assertEqual(Success(1,7),ret)


    def test_expr3(self):

        expr = Recursive()
        term = Recursive()
        expr2 = Recursive()
        
        opdict = {
            "+" : operator.add,
            "-" : operator.sub,            
            "*" : operator.mul,
            "/" : operator.truediv
            }

        def applyOp(v):
            m,op,cont = v
            def helper(acc,op2):
                func = opdict[op2]
                acc2 = func(acc,int(m))
                return cont(acc2,op)
            return helper

        def applyInit(m):
            def helper(acc,op2):
                func = opdict[op2]
                acc2 = func(acc,int(m))
                return acc2
            return helper
        
        def evalMult(f): return f(1,"*")
        def evalAdd(f): return f(0,"+")
            
        item = ( regexpP(r"\d+") | 
                 (charP("(") + expr2 + charP(")"))(1) )

        term <<= ( (item + regexpP(r"[*/]") + term) >> applyOp |
                    item >> applyInit
                  )
        term2 = term >> evalMult

        expr <<= ( (term2 + regexpP(r"[\+\-]") + expr) >> applyOp  |
                    term2 >> applyInit
                  )
        expr2 <<= expr >> evalAdd

        ret = expr2.parse("1+1*1+1",0)
        self.assertEqual(Success(3,7),ret)

        ret = expr2.parse("1-1*1+1",0)
        self.assertEqual(Success(1,7),ret)

        ret = expr2.parse("1-(1+1)+1",0)
        self.assertEqual(Success(0,9),ret)

        ret = expr2.parse("(1+2)*(3+4)",0)
        self.assertEqual(Success(21,11),ret)
        
    def test_expr4(self):

        expr = Recursive()
        term = Recursive()
        expr2 = Recursive()
        
        def applyOp(v):
            m,op,cont = v
            def helper(acc,op2):
                acc2 = op2(acc,int(m))
                return cont(acc2,op)
            return helper

        def applyInit(m):
            def helper(acc,op2):
                acc2 = op2(acc,int(m))
                return acc2
            return helper
        
        def evalMult(f): return f(1,operator.mul)
        def evalAdd(f): return f(0,operator.add)

        addOp = ( strP("+") >> (lambda _: operator.add)| 
                  strP("-") >> (lambda _: operator.sub) )

        mulOp = ( strP("*") >> (lambda _: operator.mul) | 
                  strP("/") >> (lambda _: operator.truediv) )
        
        item = ( regexpP(r"\d+") | 
                 (charP("(") + expr2 + charP(")"))(1) )

        term <<= ( (item + mulOp + term) >> applyOp |
                    item >> applyInit
                  )
        term2 = term >> evalMult

        expr <<= ( (term2 + addOp + expr) >> applyOp  |
                    term2 >> applyInit
                  )
        expr2 <<= expr >> evalAdd

        ret = expr2.parse("1+1*1+1",0)
        self.assertEqual(Success(3,7),ret)

        ret = expr2.parse("1-1*1+1",0)
        self.assertEqual(Success(1,7),ret)

        ret = expr2.parse("1-(1+1)+1",0)
        self.assertEqual(Success(0,9),ret)

        ret = expr2.parse("(1+2)*(3+4)",0)
        self.assertEqual(Success(21,11),ret)
        
                
if __name__ == "__main__":
    unittest.main()

    
    

    
