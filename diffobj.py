


import difflib

class DifferPair:
    def __init__(self,k,o):
        self.k = k
        self.o = o
    def __repr__(self):
        return f'({self.k}, {self.o})'
    def __hash__(self):
        return hash(self.k)
    def __eq__(self,other):
        return (
            self.__class__ == other.__class__ and
            self.k == other.k
            )

def diff_obj(oseq1,oseq2,func=(lambda x: x)):
    seq1 = [ DifferPair(func(o1),o1) for o1 in oseq1 ]
    seq2 = [ DifferPair(func(o2),o2) for o2 in oseq2 ]
    matcher = difflib.SequenceMatcher(a = seq1,b = seq2)
    return matcher.get_opcodes()

def print_diff_obj(oseq1,oseq2,func=(lambda x: x)):
    opcodes = diff_obj(oseq1,oseq2,func)
    for tag,i1,i2,j1,j2 in opcodes:
        if tag == "equal":
            for f0,t0 in zip(oseq1[i1:i2],oseq2[j1:j2]):
                print("\t".join([" ",f'{f0}']))
        else:
            for f0 in oseq1[i1:i2]:
                print("\t".join(["-",f'{f0}']))
            for t0 in oseq2[j1:j2]:
                print("\t".join(["+",f'{t0}']))

def test1():

    print("case1")
    a = ["1","2","3","4"]
    b = ["1","0","3","4"]
    print_diff_obj(a,b)

    print("case2")
    a = ["a","b","c","d","e"]
    b = ["A","B","f","D","E"]
    print_diff_obj(a,b,str.upper)

                
if __name__ == "__main__":
    test1()
