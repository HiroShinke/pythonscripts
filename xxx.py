

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

    def func():
        return "bbbb"
    
    def ioo(self):
        return A.func()

    @classmethod
    def meth(cls):
        return "cccc"
    
    hoo = foo


import unittest


class TestClassDefinition(unittest.TestCase):

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

    def test_aliasing(self):       
        a = A(10,20)
        self.assertTrue( a.hoo() == "dddd" ) 

    def test_function(self):       
        a = A(10,20)
        self.assertTrue( a.ioo() == "bbbb" )
        self.assertTrue( A.func() == "bbbb" )

    def test_classmethod(self):
        a = A(10,20)
        self.assertTrue( a.meth() == "cccc" )
        self.assertTrue( A.meth() == "cccc" )

    def test_dynamic_method_creation(self):
        a = A(10,20)
        def func(self):
            return "zzzz"
        setattr(A, "hoo", func)
        A.joo = func
        self.assertTrue( a.hoo() == "zzzz" )
        self.assertTrue( a.joo() == "zzzz" )
        
if __name__ == '__main__':
    unittest.main()        





