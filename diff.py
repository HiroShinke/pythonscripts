

import sys
from pathlib import Path
import difflib
import argparse

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

def do_diff(fp,tp):
    if fp.is_file() and tp.is_file():
        do_difffile(fp,tp)
    elif fp.is_dir() and tp.is_dir():
        do_diffdir(fp,tp)
    else:
        print(f"uncomparable {f} and {t}")
    

def do_difffile(f,t):
    print(f"---{f}")
    print(f"+++{t}")
    ret = difflib.ndiff(list(f.open(mode='r')),
                        list(t.open(mode='r')),
                        charjunk=None)
    ret = [ l for l in ret if l[0] != '?']
    print(''.join(ret),end='')

def do_diffdir(f,t):
    seq1 = list( [ DifferPair(n1.name,n1) for n1 in f.iterdir() ])
    seq2 = list( [ DifferPair(n2.name,n2) for n2 in t.iterdir() ])

    matcher = difflib.SequenceMatcher(a = seq1,b = seq2)
    # print(seq1)
    # print(seq2)
    for tag,i1,i2,j1,j2 in matcher.get_opcodes():
        # print(f"{tag} a[{i1}:{i2}], b[{j1}:{j2}]")
        if tag == "equal":
            for f0,t0 in zip(seq1[i1:i2],seq2[j1:j2]):
                do_diff(f0.o,t0.o)
        else:
            for f0 in seq1[i1:i2]:
                print(f'{f0.o} only in {f0.o.parent}')
            for t0 in seq2[j1:j2]:
                print(f'{t0} only in {t0.o.parent}')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f"    ,type=str,  action='store')
    parser.add_argument("-t"    ,type=str,  action='store')    
    args = parser.parse_args()
    do_diff(Path(args.f), Path(args.t))

if __name__ == "__main__":
    main()
    
