

import sys
from pathlib import Path
import diffutil
import argparse

def do_diff(fp,tp):
    if fp.is_file() and tp.is_file():
        do_difffile(fp,tp)
    elif fp.is_dir() and tp.is_dir():
        do_diffdir(fp,tp)
    else:
        print(f"uncomparable {f} and {t}")
    

def do_difffile(f,t):


    seq1 = list(f.open(mode='r'))
    seq2 = list(t.open(mode='r'))

    diffOccurs = False
    lines = []
    
    def match_func(i,j):
        lines.append("\t".join([" ",f'{i},{j}',f'{seq1[i]}']))        
    
    def discard_a(i):
        nonlocal diffOccurs
        diffOccurs = True
        lines.append("\t".join(["-",f'{i}',f'{seq1[i]}']))

    def discard_b(j):
        nonlocal diffOccurs        
        diffOccurs = True        
        lines.append("\t".join(["+",f'{j}',f'{seq2[j]}']))

    diffutil.traverse_sequences(seq1,seq2,
                                matchFunc=match_func,
                                discardAFunc=discard_a,
                                discardBFunc=discard_b)
    if diffOccurs:
        print(f"---{f}")
        print(f"+++{t}")
        sys.stdout.writelines(lines)


        
def do_diffdir(f,t):
    
    seq1 = list( [ n1 for n1 in f.iterdir() ])
    seq2 = list( [ n2 for n2 in t.iterdir() ])

    def match_func(i,j):
        do_diff(seq1[i],seq2[j])

    def discard_a(i):
        print(f'{seq1[i]} only in {seq1[i].parent}')        

    def discard_b(j):
        print(f'{seq2[j]} only in {seq2[j].parent}')        
        
    diffutil.traverse_sequences(seq1,seq2,
                                matchFunc=match_func,
                                discardAFunc=discard_a,
                                discardBFunc=discard_b,
                                keyFunc=lambda x: x.name)
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f"    ,type=str,  action='store')
    parser.add_argument("-t"    ,type=str,  action='store')    
    args = parser.parse_args()
    do_diff(Path(args.f), Path(args.t))

if __name__ == "__main__":
    main()
    
