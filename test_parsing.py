

from parsing import *
import unittest
import operator
import re


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

        parser = strp("abc")

        ret = parser.parse("abc",0)
        self.assertEqual(Success("abc",3),ret)

        ret = parser.parse("abe",0)
        self.assertEqual(Failure(0),ret)


    def test_strP2(self):

        parser = strp("abc") + strp("def")

        ret = parser.parse("abcdef",0)
        self.assertEqual(Success(["abc","def"],6),ret)

        ret = parser.parse("abcxxx",0)
        self.assertEqual(Failure(3),ret)


    def test_regexpP1(self):

        parser = regexpp("abc")

        ret = parser.parse("abc",0)
        self.assertEqual(Success("abc",3),ret)

        ret = parser.parse("abe",0)
        self.assertEqual(Failure(0),ret)


    def test_regexpP2(self):

        parser = regexpp("abc") + regexpp("def")

        ret = parser.parse("abcdef",0)
        self.assertEqual(Success(["abc","def"],6),ret)

        ret = parser.parse("abcxxx",0)
        self.assertEqual(Failure(3),ret)

        
    def test_splicing(self):

        expr = Recursive()
        
        item = charP("1")
        expr <<= (item + charP("+") + expr).splicing() | item

        ret = expr.parse("1+1+1",0)
        self.assertEqual(Success(["1","+","1","+","1"],5,True),ret)

        ret = expr.parse("1+1+1+1",0)
        self.assertEqual(Success(["1","+","1","+","1","+","1"],7,True),ret)


    def test_expr(self):

        expr = Recursive()
        term = Recursive()
        
        item = charP("1")
        term <<= (item + charP("*") + term).splicing() | item
        expr <<= (term + charP("+") + expr).splicing() | term

        ret = expr.parse("1+1*1+1",0)
        self.assertEqual(Success(["1","+","1","*","1","+","1"],7,True),ret)

        expr = Recursive()
        term = Recursive()

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
        term <<= ( (item + regexpp(r"[*/]") + term) >> applyOp |
                   item >> applyOp )
        term2 = term >> evalMult
        expr <<= ( (term2 + regexpp(r"[\+\-]") + expr) >> applyOp  |
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
            
        item = ( regexpp(r"\d+") | 
                 (charP("(") + expr2 + charP(")"))(1) )

        term <<= ( (item + regexpp(r"[*/]") + term) >> applyOp |
                    item >> applyInit
                  )
        term2 = term >> evalMult

        expr <<= ( (term2 + regexpp(r"[\+\-]") + expr) >> applyOp  |
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
            return (lambda acc,op2: cont(op2(acc,int(m)),op) )

        def applyInit(m): return (lambda acc,op2: op2(acc,int(m)))
        
        def evalMult(f): return f(1,operator.mul)
        def evalAdd(f): return f(0,operator.add)

        addOp = ( strp("+") >> (lambda _: operator.add)| 
                  strp("-") >> (lambda _: operator.sub) )

        mulOp = ( strp("*") >> (lambda _: operator.mul) | 
                  strp("/") >> (lambda _: operator.truediv) )
        
        item = ( regexpp(r"\d+") | 
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

    def test_left_recursion1(self):

        expr = Recursive()
        
        addOp = ( strp("+") >> (lambda _: operator.add)| 
                  strp("-") >> (lambda _: operator.sub) )

        def func1(x,op,t): return op(x,int(t))
        def func2(tstr): return int(tstr)

        term = regexpp(r"\d+")
        expr <<= ((expr + addOp + term) >> func1 |
                  term >> func2
                  )

        ret = expr.parse("1+1+1+1",0)
        self.assertEqual(Success(4,7),ret)
        ret = expr.parse("1-1+1+1",0)
        self.assertEqual(Success(2,7),ret)


    def test_left_recursion2(self):

        expr = Recursive()
        term = Recursive()
        
        addOp = ( strp("+") >> constAction(operator.add)|
                  strp("-") >> constAction(operator.sub) )

        mulOp = ( strp("*") >> constAction(operator.mul) | 
                  strp("/") >> constAction(operator.truediv) )

        def func1(x,op,t): return op(x,t)
        def func2(tstr): return int(tstr)

        item = ( regexpp(r"\d+") >> func2 | 
                 (charP("(") + expr + charP(")"))(1) )

        term <<= ((term + mulOp + item) >> func1 |
                  item
                  )
        expr <<= ((expr + addOp + term) >> func1 |
                  term
                  )

        ret = expr.parse("1+1*1+1",0)
        self.assertEqual(Success(3,7),ret)

        ret = expr.parse("1-1*1+1",0)
        self.assertEqual(Success(1,7),ret)

        ret = expr.parse("1-(1+1)+1",0)
        self.assertEqual(Success(0,9),ret)

        ret = expr.parse("(1+2)*(3+4)",0)
        self.assertEqual(Success(21,11),ret)
                

    def test_left_recursion3(self):

        expr = Recursive()
        term = Recursive()
        
        def func1(x,op,t): return [x,op,t]

        addOp = strp("+") |  strp("-")                   
        mulOp = strp("*") |  strp("/") 

        item = ( regexpp(r"\d+") | 
                 (charP("(") + expr + charP(")"))(1) )

        term <<= ((term + mulOp + item) >> func1 |
                  item
                  )
        expr <<= ((expr + addOp + term) >> func1 |
                  term
                  )

        ret = expr.parse("1+1*1+1",0)
        self.assertEqual(Success([["1","+",["1","*","1"]],"+","1"],7),ret)

        ret = expr.parse("1-1*1+1",0)
        self.assertEqual(Success([["1","-",["1","*","1"]],"+","1"],7),ret)

        ret = expr.parse("1-(1+1)+1",0)
        self.assertEqual(Success([["1","-",["1","+","1"]],"+","1"],9),ret)

        ret = expr.parse("(1+2)*(3+4)",0)
        self.assertEqual(Success([["1","+","2"],"*",["3","+","4"]],11),ret)


    def test_left_recursion4(self):

        expr = Recursive()
        term = Recursive()
        
        addOp = strp("+") |  strp("-")                   
        mulOp = strp("*") |  strp("/") 

        item = ( regexpp(r"\d+") | 
                 (charP("(") + expr + charP(")"))(1) )

        term <<= (term + mulOp + item |
                  item
                  )
        expr <<= (expr + addOp + term |
                  term
                  )

        ret = expr.parse("1+1*1+1",0)
        self.assertEqual(Success([["1","+",["1","*","1"]],"+","1"],7),ret)

        ret = expr.parse("1-1*1+1",0)
        self.assertEqual(Success([["1","-",["1","*","1"]],"+","1"],7),ret)

        ret = expr.parse("1-(1+1)+1",0)
        self.assertEqual(Success([["1","-",["1","+","1"]],"+","1"],9),ret)

        ret = expr.parse("(1+2)*(3+4)",0)
        self.assertEqual(Success([["1","+","2"],"*",["3","+","4"]],11),ret)
        


    def test_select_list(self):

        expr = Recursive()
        term = Recursive()

        def kw(str): return regexpp(rf"\s*({str})",group=1,flags=re.I)
        
        word = regexpp(r"\s*(\w+)",group=1)
        column = word  + ~(kw("AS") +  word)
        selectList = column  + ( kw(",") + column )[...]
        selectStatement = kw("SELECT") + selectList + kw("FROM") + word
        
        ret = selectStatement.parse("select x,y,z,w from t",0)
        self.assertEqual(Success(["select",["x",None,
                                            [[",",["y",None]],
                                             [",",["z",None]],
                                             [",",["w",None]]]],
                                  "from",
                                  "t"],
                                 21),
                         ret)


    def test_select_list_splicing(self):

        expr = Recursive()
        term = Recursive()

        def kw(str): return regexpp(rf"\s*({str})",group=1,flags=re.I)
        
        word = regexpp(r"\s*(\w+)",group=1)
        column = (word  + ~(kw("AS") +  word)).splicing()
        selectList = column  + ( kw(",") + column )[...].splicing()
        selectStatement = kw("SELECT") + selectList + kw("FROM") + word
        
        ret = selectStatement.parse("select x,y,z,w from t",0)
        self.assertEqual(Success(["select",["x",None,
                                            [",","y",None],
                                            [",","z",None],
                                            [",","w",None]],
                                  "from",
                                  "t"],
                                 21),
                         ret)

    def test_select_list_splicing2(self):

        expr = Recursive()
        term = Recursive()

        def kw(str): return regexpp(rf"\s*({str})",group=1,flags=re.I)
        
        word = regexpp(r"\s*(\w+)",group=1)
        column = (word  + ~(kw("AS") +  word)).splicing()
        selectList = (column  + ( kw(",") + column )[...].splicing()).splicing()
        selectStatement = kw("SELECT") + selectList + kw("FROM") + word
        
        ret = selectStatement.parse("select x,y,z,w from t",0)
        self.assertEqual(Success(["select","x",None,
                                  [",","y",None],
                                  [",","z",None],
                                  [",","w",None],
                                  "from",
                                  "t"],
                                 21),
                         ret)


    def test_select_list_skip(self):

        expr = Recursive()
        term = Recursive()

        def kw(str): return regexpp(rf"\s*({str})",group=1,flags=re.I)
        
        word = regexpp(r"\s*(\w+)",group=1)
        column = (word  + ~(kw("AS") +  word)).splicing()
        selectList = (column  + ( Skip(kw(",")) + column )[...].splicing()).splicing()
        selectStatement = kw("SELECT") + selectList + kw("FROM") + word
        
        ret = selectStatement.parse("select x,y,z,w from t",0)
        self.assertEqual(Success(["select","x",None,
                                  ["y",None],
                                  ["z",None],
                                  ["w",None],
                                  "from",
                                  "t"],
                                 21),
                         ret)


    def test_select_list_option_splicing(self):

        expr = Recursive()
        term = Recursive()

        def kw(str): return regexpp(rf"\s*({str})",group=1,flags=re.I)
        
        word = regexpp(r"\s*(\w+)",group=1)
        column = (word  + (~(kw("AS") +  word)).splicing()).splicing()
        selectList = (column  + ( Skip(kw(",")) + column )[...].splicing()).splicing()
        selectStatement = kw("SELECT") + selectList + kw("FROM") + word
        
        ret = selectStatement.parse("select x,y,z,w from t",0)
        self.assertEqual(Success(["select","x",
                                  ["y"],
                                  ["z"],
                                  ["w"],
                                  "from",
                                  "t"],
                                 21),
                         ret)


    def test_select_list_full_splicing(self):

        expr = Recursive()
        term = Recursive()

        def kw(str): return regexpp(rf"\s*({str})",group=1,flags=re.I)
        
        word = regexpp(r"\s*(\w+)",group=1)
        column = (word  + (~(kw("AS") +  word)).splicing()).splicing()
        selectList = (column  + ((Skip(kw(",")) + column )).splicing()[...].splicing()).splicing()
        selectStatement = kw("SELECT") + selectList + kw("FROM") + word
        
        ret = selectStatement.parse("select x,y,z,w from t",0)
        self.assertEqual(Success(["select","x",
                                  "y",
                                  "z",
                                  "w",
                                  "from",
                                  "t"],
                                 21),
                         ret)
        
if __name__ == "__main__":
    unittest.main()




    
