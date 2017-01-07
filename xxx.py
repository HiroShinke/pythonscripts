

class Base:
    def __init__(self,n):
        self.n = n

class A(Base):

    def __init__(self,n,m):
        Base.__init__(self,n)
        self.m = m
    
    AAA = "dddd"

    def foo(self):
        print(self.AAA)
        return self.AAA

    def goo(self):
        self.foo()

    hoo = foo


import unittest


class TestClassVarAndInstanceVar(unittest.TestCase):

    def setUp(self):
        pass
    
    def test_constructor_chain(self):

        a = A(10,20)
        self.assertTrue( a.n == 10 )        
        self.assertTrue( a.m == 20 )
        
    def test_classvariable_blinding(self):

        a = A(10,20)
        self.assertTrue( a.AAA == "dddd" )
        self.assertTrue( a.foo() == "dddd" )
        a.AAA = "aaaa"
        self.assertTrue( a.AAA == "aaaa" )
        self.assertTrue( a.foo() == "aaaa" )
        self.assertTrue( a.hoo() == "aaaa" )
        
if __name__ == '__main__':
    unittest.main()        





