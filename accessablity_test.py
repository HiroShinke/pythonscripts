
import unittest
from dataclasses import dataclass

@dataclass
class A:
  x : str
  y : str
  z : str

a = A(1,2,3)
b = A(1,2,3)
c = A(1,2,3)

print(f"a = {a}")
print(f"b = {b}")
print(f"c = {c}")

def foo(x: str):
    print(f"x = {x}")

foo(1)
foo("xxxx")

class B:
  __slots__ = ['a','b','__x']
  def __init__(self,a,b):
    self.a = a
    self.b = b
    self.__x = 1

class C:
  def __init__(self):
    print("called C.__init__")
    self.a = 1
    self.__p1 = 2
    self._p2 = 3

class D(C):
  def __init__(self):
    super().__init__()
    print("called D.__init__")    
    self.b = 1

d = D()

print(f"d = {d.__dict__}")

  
class AccessTest(unittest.TestCase):

  def test_private1(self):
    c = C()
    print(f" = {c.__dict__}")
    self.assertEqual(1,c.a)
    self.assertEqual(2,c._C__p1)
    self.assertEqual(2,c.__dict__["_C__p1"])
    self.assertEqual(2,getattr(c,"_C__p1"))
    self.assertEqual(3,c._p2)
    
    with self.assertRaises(AttributeError):
      print(c.__p1)

  # no protected scope in Python
  def test_protected1(self):
    d = D()
    print(f" = {d.__dict__}")
    self.assertEqual(1,d.a)
    self.assertEqual(2,d._C__p1)
    self.assertEqual(2,d.__dict__["_C__p1"])
    self.assertEqual(2,getattr(d,"_C__p1"))

    with self.assertRaises(AttributeError):
      print(d.__p1)

    self.assertEqual(3,d._p2)


  def test_assignment(self):
    c = C()
    d = D()
    
    c.x = 1
    d.x = 2

    self.assertEqual(1,c.x)
    self.assertEqual(2,d.x)


  def test_slots(self):
    b = B(1,2)
    with self.assertRaises(AttributeError):
      b.x = 1

    
if __name__ == "__main__":
  unittest.main()

  
  


  
