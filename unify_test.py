

from unittest import TestCase,main
from unify  import *

a = app
v = Var
c = Const

class UnifyTest(TestCase):


    def test_basic1(self):
        subst = unify(v("x"),v("y"),{})
        self.assertEqual({ "x" : v("y") }, subst)

    def test_basic2(self):
        subst = unify(v("x"),c(1),{})
        self.assertEqual({ "x" : c(1) }, subst)

    def test_basic3(self):
        subst = unify(c(1),c(2),{})
        self.assertEqual(None, subst)

    def test_apply1(self):
        subst = unify(a("f",v("x")),a("f",v("y")),{})
        self.assertEqual({ "x" : v("y") }, subst)

    def test_apply2(self):
        subst = unify(a("f",v("x"),v("y")),a("f",v("y"),v("x")),{})
        self.assertEqual({ "x" : v("y") }, subst)

    def test_apply2(self):
        subst = unify(a("f",v("x"),v("y")),a("f",v("y"),v("x")),{})
        self.assertEqual({ "x" : v("y") }, subst)

    def test_apply3(self):
        subst = unify(a("f",
                        a("g",v("x")),v("y")),
                      a("f",
                        v("y"),a("g",v("x"))),{})
        self.assertEqual({ "y" : a("g",v("x")) }, subst)

    def test_apply4(self):
        subst = unify(a("f",v("x"),v("y"),v("z"),v("v"),v("w")),
                      a("f",v("y"),v("z"),v("v"),v("w"),v("x")),
                      {})
        self.assertEqual({ "x" : v("y"),
                           "y" : v("z"),
                           "z" : v("v"),
                           "v" : v("w")
                          }, subst)
    # a case from SICP
    def test_apply5(self):
        subst = unify(a("f",v("x"),v("x")),
                      a("f",a("g",c("a"),v("y"),c("c")),
                            a("g",c("a"),c("b"),v("z"))),
                      {})
        subst = complete_subst(subst)
        self.assertEqual({ "x" : a("g",c("a"),c("b"),c("c")),
                           "y" : c("b"),
                           "z" : c("c")
                          }, subst)
        
    def test_occurs1(self):
        subst = unify(v("x"),a("f",v("x")),{})
        self.assertEqual(None, subst)

    def test_occurs2(self):
        subst = unify(v("x"),a("f",a("f",v("x"))),{})
        self.assertEqual(None, subst)

    def test_occurs3(self):
        subst = unify(v("x"),a("f",a("f",v("y"),v("x"))),{})
        self.assertEqual(None, subst)
        
    def test_occurs3(self):
        subst = unify(a("f",
                        a("g",v("x"),v("y")),v("y")),
                      a("f",
                        v("y"),a("g",v("x"),v("y"))),{})
        self.assertEqual(None, subst)

        
if __name__ == "__main__":
    main()

    
        
