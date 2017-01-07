

class Base:
    def __init__(self,n):
        self.n = n

class A(Base):

    """
    contstructor chain
    >>> a = A(10,20)
    >>> a.n
    10
    >>> a.m
    20

    classvariable hiding
    >>> a = A(10,20)
    >>> a.AAA
    \'dddd\'
    >>> a.foo()
    \'dddd\'
    >>> a.AAA = "aaaa"
    >>> a.AAA
    \'aaaa\'
    >>> a.foo()
    \'aaaa\'
    >>> A.AAA
    \'dddd\'

    """
    
    def __init__(self,n,m):
        Base.__init__(self,n)
        self.m = m
    
    AAA = "dddd"

    def foo(self):
        return self.AAA

    def goo(self):
        self.foo()

if __name__ == '__main__':
    import doctest
    doctest.testmod()





