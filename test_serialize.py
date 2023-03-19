

import unittest
import pickle
import copyreg


def dumpAndLoad(obj):
    return pickle.loads(pickle.dumps(obj))


class A:
    def __init__(self,name):
        self.name = name
    def __eq__(self,other):
        if isinstance(other,A) and self.name == other.name:
            return True
        else:
            return False

def createA(name):
    return A(name)
                
class SerTest(unittest.TestCase):

    def test1(self):

        exlist = ["a",["b","c"],"d"]
        exdict = {"a": 1, "b": 2 }
        obj  = (exlist,exdict)
        obj2 = dumpAndLoad(obj)
        self.assertEqual(obj,obj2)


    def test2(self):

        cyclic = ["a"]
        cyclic.append(cyclic)
        obj2 = dumpAndLoad(cyclic)
        self.assertTrue(obj2[1]==obj2)


    def test3(self):

        a = A("test")
        b = dumpAndLoad(a)
        self.assertEqual(a,b)


    def test3(self):

        def helper(obj):
            return createA, (obj.name,)
                
        copyreg.pickle(A,helper)
        a = A("test")
        b = dumpAndLoad(a)
        self.assertEqual(a,b)
        

if __name__ == "__main__":
    unittest.main()
