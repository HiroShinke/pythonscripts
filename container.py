

class A:
    def __init__(self,str):
        self.str = str

    def __getitem__(self,key):
        return self.str[key]

    def __len__(self):
        return len(self.str)

    def __eq__(self,o):
        return self.str == o.str


import unittest

class TestConainer(unittest.TestCase):

    def setUp(self):
        pass

    def test_getitem(self):
        a = A("01234567")
        self.assertTrue( a[0:0]  == '' )
        self.assertTrue( a[0]  == '0' )
        self.assertTrue( a[1:] == "1234567" )
        self.assertTrue( a[2:4] == "23" )
        self.assertTrue( a[-1]  == "7" )

    def test_len(self):
        a = A("01234567")
        self.assertTrue( len(a) == 8 )

    def test_eq(self):
        a = A("01234567")
        b = A("01234567")
        self.assertTrue( a == b )

if __name__ == '__main__':
    unittest.main()        

