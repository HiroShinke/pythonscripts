
class A:
    def __init__(str):
        self.str = str

    def __str__(self):
        return "<<class A: {0}>>".format(self.str)


"""
>>> a = "abcdef"
>>> b = 100
>>> print("xxxxxxx {0}= {1}".format(a,b))
xxxxxxx abcdef= 100
>>> print("xxxxxxx {a}= {b}".format(a=a,b=b))
xxxxxxx abcdef= 100
>>> a = A("John Lennon")
>>> str(a)
<<class A: John Lennon>>

"""

if __name__ == '__main__':
    import doctest
    doctest.testmod()
