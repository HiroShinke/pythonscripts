

import sys
from dataclasses import dataclass
from collections import namedtuple

## TEST
## PEP 634 -- Structural Pattern Matching: Specification
## https://www.python.org/dev/peps/pep-0634/

# python 3.10 or later is required
assert (3,10) <= sys.version_info 

###### literal 

def check_literal(n):
    match n:
        case 10:
            print("int 10")
        case "abc":
            print("string abc")
        case (a,10):
            print(f"tuple(b fixed) :({a},10)")
        case (a,b):
            print(f"tuple :({a},{b})")
        case _:
            print(f"n is not found[ {n}")

check_literal(10)
check_literal(20)
check_literal("abc")
check_literal((10,20))
check_literal(("abc",10))
check_literal(("abc",(10,20)))

###### mapping

def check_mapping(n):
    match n:
        case { "a": 1, "b" : 2 } as y :
            print(f"match y={y}")
        case { "a": 1 } as x :
            print(f"match x={x}")
        case _:
            print(f"n is not found[ {n}")

check_mapping({ "a" : 1 })
check_mapping({ "a" : 1, "b" : 2 })
check_mapping({ "a" : 1, "b" : 3 })


####### class matching

@dataclass
class Person:
    name: str
    age: int

class Person2:
    __match_args__ = ("name","age")
    def __init__(self,name,age):
        self.name = name
        self.age  = age

Person3 = namedtuple("Person3",["name","age"])
        
p = Person("tom",10)
q = Person2("john",20)
a = Person("alice",10)
r = Person2("paul",40)
s = Person2("geoge",40)
t = Person3("bob",23)


def checkPerson(p):
    match p:
        case Person(name="tom",age=10):
            print("found tom")
        case Person("alice",10):
             print("found alice")
        case Person2("paul",40):
             print("found paul")
        case Person2(name="john",age=20):
             print("found john")
        case Person2():
            print("found geoge")
        case Person3(name="bob"):
            print("found bob")
        case _:
             print("found nothing")

checkPerson(p)
checkPerson(q)
checkPerson(a)
checkPerson(r)
checkPerson(s)
checkPerson(t)

