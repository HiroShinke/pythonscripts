

import unittest
import io
import sys

class A:
    def method(self):
        super().method()
        print("A.method")

class B:
    def method(self):        
        print("B.method")

class C(A,B):
    def method(self):
        super().method()
        print("C.method")

class A11:
    def method(self):
        super().method()
        print("A11.method")

class A1(A11):
    def method(self):
        super().method()
        print("A1.method")

class C1(A1,B):
    def method(self):
        super().method()
        print("C1.method")

class D:
    def method(self):
        print("D.method")

class A2(D):
    def method(self):
        super().method()
        print("A2.method")

class B2(D):
    def method(self):
        super().method()
        print("B2.method")
        
class C2(A2,B2):
    def method(self):
        super().method()
        print("C2.method")

class MroTest(unittest.TestCase):

    def test_basic(self):
        self.assertEqual([C,A,B,object],C.mro())

        with io.StringIO() as fh:
            sys.stdout = fh
            c = C()
            c.method()
            self.assertEqual("B.method\n"
                             "A.method\n"
                             "C.method\n",
                             fh.getvalue())
            
        sys.stdout = sys.__stdout__

    def test_basic2(self):
        self.assertEqual([C1,A1,A11,B,object],C1.mro())

        with io.StringIO() as fh:
            sys.stdout = fh
            c1 = C1()
            c1.method()
            self.assertEqual("B.method\n"
                             "A11.method\n"
                             "A1.method\n"
                             "C1.method\n",
                             fh.getvalue())
            
        sys.stdout = sys.__stdout__

        
    def test_basic3(self):

        self.assertEqual([C2,A2,B2,D,object],C2.mro())

        with io.StringIO() as fh:
            sys.stdout = fh
            c2 = C2()
            c2.method()
            self.assertEqual("D.method\n"
                             "B2.method\n"
                             "A2.method\n"
                             "C2.method\n",
                             fh.getvalue())
            
        sys.stdout = sys.__stdout__

        

if __name__ == "__main__":
    unittest.main()

    

    
        
