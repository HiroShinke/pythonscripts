
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
        






if __name__ == "__main__":
    unittest.main()

    
