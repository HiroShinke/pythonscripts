

def funcmaker1(str):
    def helper():
        return str
    return helper

def funcmaker2(str):
    x = str
    def helper():
        return x
    return helper

def funcmaker3():
    x = "abc"
    def helper():
        return x
    return helper

def funcmaker4():
    x = None
    def helper():
        if not x:
            x = "abc"
        return x
    return helper


import unittest


class TestFuncDefinition(unittest.TestCase):

    def setUp(self):
        pass

    def test_normal(self):
        f1 = funcmaker1("abc")
        self.assertTrue( f1() == "abc" )

    def test_localvariable(self):
        f1 = funcmaker2("abc")
        self.assertTrue( f1() == "abc" )

    def test_local_fromliteral(self):
        f1 = funcmaker3()
        self.assertTrue( f1() == "abc" )

    def test_local_fromnone(self):
        f1 = funcmaker4()
        self.assertTrue( f1() == "abc" )
        
        
if __name__ == '__main__':
    unittest.main()        





