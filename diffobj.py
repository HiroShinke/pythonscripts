


import difflib

def createDifferClass(func):
    
    class FuncDiffer:
        def __init__(self,o):
            self.o = o
        def __repr__(self):
            return f'{self.o}'
        def __hash__(self):
            return hash(func(self.o))
        def __eq__(self,other):
            return (
                self.__class__ == other.__class__ and
                func(self.o) == func(other.o)
            )
    return FuncDiffer


def diff_obj(oseq1,oseq2,func=(lambda x: x)):
    diffclass = createDifferClass(func)
    seq1 = [ diffclass(o1) for o1 in oseq1 ]
    seq2 = [ diffclass(o2) for o2 in oseq2 ]
    matcher = difflib.SequenceMatcher(a = seq1,b = seq2)
    return matcher.get_opcodes()


def print_diff_obj(oseq1,oseq2,func=(lambda x: x)):

    def match_func(i,j):
        print("\t".join([" ",f'{oseq1[i]}']))        
    
    def discard_a(i):
        print("\t".join(["-",f'{oseq1[i]}']))

    def discard_b(j):
        print("\t".join(["+",f'{oseq2[j]}']))

    traverse_sequences(oseq1,oseq2,
                       matchFunc=match_func,
                       discardAFunc=discard_a,
                       discardBFunc=discard_b,
                       keyFunc=func)


def traverse_sequences(oseq1,oseq2,/,*,
                       matchFunc=None,
                       discardAFunc=None,
                       discardBFunc=None,
                       keyFunc=(lambda x: x)):
    opcodes = diff_obj(oseq1,oseq2,keyFunc)
    for tag,i1,i2,j1,j2 in opcodes:
        if tag == "equal":
            for i,j in zip(range(i1,i2),range(j1,j2)):
                if matchFunc: matchFunc(i,j)
        else:
            for i in range(i1,i2):
                if discardAFunc: discardAFunc(i)
            for j in range(j1,j2):
                if discardBFunc: discardBFunc(j)

def test1():

    print("case1")
    a = ["1","2","3","4"]
    b = ["1","0","3","4"]
    print_diff_obj(a,b)

    print("case2")
    a = ["a","b","c","d","e"]
    b = ["A","B","f","D","E"]
    print_diff_obj(a,b,str.upper)

    def match_func(i,j):
        print(f"  {i},{j}: {a[i]}")

    def discard_a_func(i):
        print(f"- {i}: {a[i]}")

    def discard_b_func(j):
        print(f"+ {j}: {b[j]}")

    print("case3")        
    traverse_sequences(a,b,
                       matchFunc=match_func,
                       discardAFunc=discard_a_func,
                       discardBFunc=discard_b_func,
                       keyFunc=str.upper)
    
if __name__ == "__main__":
    test1()
