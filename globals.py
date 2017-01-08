


def func():
    return "abcde"

func1 = func
globals()["func2"] = func


import unittest

class TestGlobals(unittest.TestCase):

    def setUp(self):
        pass

    def test_dynamically_generated_function(self):
        self.assertTrue( func() == "abcde" )
        self.assertTrue( func1() == "abcde" )
        self.assertTrue( func2() == "abcde" )

if __name__ == '__main__':
    unittest.main()        

