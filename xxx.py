

class Base:
    def __init__(self,n):
        self.n = n

class A(Base):

    def __init__(self,n,m):
        Base.__init__(self,n)
        self.m = m
    
    AAA = "dddddddddd\n"

    def foo(self):
        print(self.AAA)

    def goo(self):
        self.foo()

a = A("nn","mm")
a.foo()
a.goo()





