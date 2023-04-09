

import unittest
import sys

def foo(x,y,key=None,**kwargs):
    print(f"{kwargs}",file=sys.stderr)
    return (x,y,key)

def goo(x,y,/,*,key=None,**kwargs):
    print(f"{kwargs}",file=sys.stderr)
    return (x,y,key)

def hoo(x,/,y,*,key=None,**kwargs):
    print(f"{kwargs}",file=sys.stderr)
    return (x,y,key)


class TestFuncDefinition(unittest.TestCase):

    def setUp(self):
        pass

    def test_basic1(self):
        key = foo(1,2,key="abc")
        self.assertEqual((1,2,"abc"),key)

    # def test_basic2(self):
    #   key = foo(1,2,key="abc",3,4)
    #   self.assertEqual("abc",key)

    def test_basic2(self):
        key = foo(1,2,key="abc",key2="def")
        self.assertEqual((1,2,"abc"),key)

    def test_basic3(self):
        key = foo(1,2,key2="def")
        self.assertEqual((1,2,None),key)        

    def test_basic4(self):
        key = foo(1,2,"abc",key2="def")
        self.assertEqual((1,2,"abc"),key)        

    def test_basic5(self):
        key = foo(y=2,x=1,key="abc",key2="def")
        self.assertEqual((1,2,"abc"),key)

    def test_keyword1(self):
        key = goo(1,2,key="abc")
        self.assertEqual((1,2,"abc"),key)

    # def test_basic2(self):
    #   key = foo(1,2,key="abc",3,4)
    #   self.assertEqual("abc",key)

    def test_keyword2(self):
        key = goo(1,2,key="abc",key2="def")
        self.assertEqual((1,2,"abc"),key)

    def test_keyword3(self):
        key = goo(1,2,key2="def")
        self.assertEqual((1,2,None),key)        

    def test_keyword4(self):
        with self.assertRaises(TypeError):        
            goo(1,2,"abc",key2="def")

    def test_keyword5(self):
        with self.assertRaises(TypeError):
            goo(y=2,x=1,key="abc",key2="def")

    def test_keyword2_1(self):
        key = hoo(1,2,key="abc")
        self.assertEqual((1,2,"abc"),key)

    # def test_basic2(self):
    #   key = foo(1,2,key="abc",3,4)
    #   self.assertEqual("abc",key)

    def test_keyword2_2(self):
        key = hoo(1,2,key="abc",key2="def")
        self.assertEqual((1,2,"abc"),key)

    def test_keyword2_3(self):
        key = hoo(1,2,key2="def")
        self.assertEqual((1,2,None),key)        

    def test_keyword2_4(self):
        with self.assertRaises(TypeError):        
            hoo(1,2,"abc",key2="def")

    def test_keyword2_5(self):
        ret = hoo(1,y=2,key="abc",key2="def")
        self.assertEqual((1,2,"abc"),ret)

    def test_keyword2_6(self):
        with self.assertRaises(TypeError):        
            hoo(1,2,"abc",key2="def")

    def test_keyword2_7(self):
        with self.assertRaises(TypeError):        
            hoo(x=1,y=2,key="abc",key2="def")


            
if __name__ == '__main__':
    unittest.main()        





