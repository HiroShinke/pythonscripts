

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

    
        
