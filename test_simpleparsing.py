


from simpleparsing import *
import unittest

class SimpleTest(unittest.TestCase):

    def test1(self):

        expr = Recursive()
        term = Recursive()
        atom = Recursive()
        
        digit  = regexpp("\d+")
        addop =  regexpp("[+-]")
        mulop = regexpp("[*/]")

        expr.defined(Seq(term, Many( Seq(addop, term) )))
        term.defined(Seq(atom, Many( Seq(mulop, atom) )))                         
        atom.defined(Or(digit,
                        Seq( regexpp(r"\("),
                             expr,
                             regexpp(r"\)") )))

        ret = expr.parse("1+2*3",0)
        self.assertEqual(Success([["1",[]],[["+",["2",[["*", "3"]]]]]],5),
                         ret)


    def test2(self):

        expr = Recursive()
        term = Recursive()
        atom = Recursive()

        rep = token
        
        digit = rep(r"\d+")
        addop = rep("[+-]")
        mulop = rep("[*/]")

        expr.defined(Seq(term, Many( Seq(addop, term) )))
        term.defined(Seq(atom, Many( Seq(mulop, atom) )))                         
        atom.defined(Or(digit,
                        Seq( rep(r"\("),
                             expr,
                             rep(r"\)") )))

        logicalop = Or( rep("AND"), rep("OR") )
        bincondop =  Seq( Opt(rep("NOT")), rep("<|>|<=|=<|>=|=>|=") )
        unarycondop = Seq( Opt(rep("IS")), Opt(rep("NOT")),
                           Or(rep("NUMERIC"),rep("ALPHANUMERIC")))

        condexpr = Recursive()
        condterm = Recursive()
        condatom = Recursive()

        condexpr.defined(Seq(condterm, Many( Seq(logicalop, condterm) )))
        condterm.defined(Or(Seq(expr, bincondop, expr),
                            Seq(expr, unarycondop),
                            expr,
                            Seq(rep("\("), condexpr, rep("\)"))))

        ret = condexpr.parse("1+2*3 = 4",0)
        print(f"ret = {ret}")
        ret = condexpr.parse("1+2*3 = 4 AND 5 = 1",0)
        print(f"ret = {ret}")
        ret = condexpr.parse("(1+2*3 = 4 OR 1 = 5) AND 1 = 1",0)
        print(f"ret = {ret}")
        ret = condexpr.parse("1+2*3 IS NUMERIC AND 5 = 1",0)
        print(f"ret = {ret}")

        

if __name__ == "__main__":
    unittest.main()

    
