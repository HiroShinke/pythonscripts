
import weakref
import unittest
import sys
import io

class Desc:
    
    def __init__(self,defaultValue):
        self._value = weakref.WeakKeyDictionary()
        self.defaultValue = defaultValue

    def __get__(self,obj,objtype):
        print(f"__get__called({obj},{objtype})")
        if obj is None:
            return self.defaultValue
        else:
            return self._value.get(obj,None)
        
    def __set__(self,obj,value):
        print(f"__set__called({obj},{value})")
        self._value[obj] = value

class A:

    a = Desc(10)
    b = Desc(20)
    c = Desc(30)

class StaticMethod:

    def __init__(self,f):
        self.f = f

    def __get__(self,obj,objtype=None):
        return self.f

class ClassMethod:

    def __init__(self,f):
        self.f = f

    def __get__(self,obj,klass=None):

        if klass is None:
            klass = type(obj)

        def func(*args):
            return self.f(klass,*args)
        return func

def justfunc(*args):
    return args

class DescTest(unittest.TestCase):

    def test_set(self):

        x = A()

        with io.StringIO() as fh:
            sys.stdout = fh
            x.a = 1
            self.assertEqual(f"__set__called({x},1)\n",fh.getvalue())

        sys.stdout = sys.__stdout__
        
    def test_get(self):

        x = A()

        with io.StringIO() as fh:
            sys.stdout = fh
            zzz = x.a
            self.assertEqual(f"__get__called({x},{A})\n",fh.getvalue())

        sys.stdout = sys.__stdout__
        
    def test_basic(self):

        x = A()
        y = A()
        
        x.a = 1
        x.b = 2
        x.c = 3

        self.assertEqual(1,x.a)
        self.assertEqual(2,x.b)
        self.assertEqual(3,x.c)
        
        y.a = 4
        y.b = 5
        y.c = 6
        
        self.assertEqual(4,y.a)
        self.assertEqual(5,y.b)
        self.assertEqual(6,y.c)

    def test_basic2(self):

        self.assertEqual(10,A.a)
        self.assertEqual(20,A.b)
        self.assertEqual(30,A.c)

    def test_basic3(self):

        x = A()

        self.assertEqual(True,hasattr(x,"a"))
        self.assertEqual(True,hasattr(A,"a"))
        self.assertEqual(Desc,type(A.__dict__["a"]))
        self.assertEqual(Desc,type(object.__getattribute__(A,"a")))
        self.assertEqual(Desc,type(A.__getattribute__(A,"a")))        
        self.assertEqual(int,type(getattr(A,"a")))

        self.assertEqual(False,"a" in x.__dict__)
        self.assertEqual(None,object.__getattribute__(x,"a"))
        self.assertEqual(None,getattr(x,"a"))


    def test_attr(self):

        class C:
            def __init__(self):
                self.a = 1

            def __getattr__(self,name):
                return f"value of {name}"
            
        c = C()

        self.assertEqual(1,c.a)
        self.assertEqual("value of b",c.b)
        self.assertEqual("value of b",getattr(c,"b"))

        
    def test_simplemethod(self):

        class B:
            f = justfunc
            def g(*args):
                return args

        b = B()
        self.assertEqual((b,1,2),b.f(1,2))
        self.assertEqual((1,2),B.f(1,2))

        self.assertEqual((b,1,2),b.g(1,2))
        self.assertEqual((1,2),B.g(1,2))

        self.assertEqual(True,hasattr(justfunc,"__get__"))
        
        
    def test_classmethod(self):

        class B:
            f = classmethod(justfunc)

            @classmethod
            def g(*args):
                return args

            h = ClassMethod(justfunc)

        b = B()
        self.assertEqual((B,1,2),b.f(1,2))
        self.assertEqual((B,1,2),B.f(1,2))

        self.assertEqual((B,1,2),b.g(1,2))
        self.assertEqual((B,1,2),B.g(1,2))

        self.assertEqual((B,1,2),b.h(1,2))
        self.assertEqual((B,1,2),B.h(1,2))
        
    def test_staticmethod(self):

        class B:
            f = staticmethod(justfunc)

            @staticmethod
            def g(*args):
                return args

            h = StaticMethod(justfunc)            
        
        b = B()
        self.assertEqual((1,2),b.f(1,2))
        self.assertEqual((1,2),B.f(1,2))

        self.assertEqual((1,2),b.g(1,2))
        self.assertEqual((1,2),B.g(1,2))

        self.assertEqual((1,2),b.h(1,2))
        self.assertEqual((1,2),B.h(1,2))

        
if __name__ == "__main__":
    unittest.main()

    
