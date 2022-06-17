

import sys
import tkinter as tk
from tkinter import ttk
from pathlib import Path
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

def do_diff(fp,tp,of,func=lambda n: n):
    if fp.is_file() and tp.is_file():
        do_difffile(fp,tp,of,func)
    elif fp.is_dir() and tp.is_dir():
        do_diffdir(fp,tp,of,func)
    else:
        print(f"uncomparable {fp} and {tp}",file=of)
    

def do_difffile(f,t,of,func):

    fh = f.open(mode='r')
    th = t.open(mode='r')

    ret = []
    diff = False

    seq1 = list( [ DifferPair(func(l),l) for l in fh ])
    seq2 = list( [ DifferPair(func(l),l) for l in th ])

    matcher = difflib.SequenceMatcher(a = seq1,b = seq2)

    for tag,i1,i2,j1,j2 in matcher.get_opcodes():
        if tag == "equal":
            for i,f0,j,t0 in zip(range(i1,i2),
                                 seq1[i1:i2],
                                 range(j1,j2),                                 
                                 seq2[j1:j2]):
                ret.append("\t".join(["",f"{i},{j}",f0.o]))
        else:
            diff = True
            for i,f0 in zip(range(i1,i2),seq1[i1:i2]):
                ret.append("\t".join(["-",f"{i}",f0.o]))
            for j,t0 in zip(range(j1,j2),seq2[j1:j2]):
                ret.append("\t".join(["+",f"{j}",t0.o]))

    if diff:
        print(f"---{f}",file=of)
        print(f"+++{t}",file=of)
        print(''.join(ret),end='',file=of)
        

def do_diffdir(f,t,of,func):
    seq1 = list( [ DifferPair(n1.name,n1) for n1 in f.iterdir() ])
    seq2 = list( [ DifferPair(n2.name,n2) for n2 in t.iterdir() ])

    matcher = difflib.SequenceMatcher(a = seq1,b = seq2)

    for tag,i1,i2,j1,j2 in matcher.get_opcodes():
        if tag == "equal":
            for f0,t0 in zip(seq1[i1:i2],seq2[j1:j2]):
                do_diff(f0.o,t0.o,of,func)
        else:
            for f0 in seq1[i1:i2]:
                print(f'{f0.o} only in {f0.o.parent}',file=of)
            for t0 in seq2[j1:j2]:
                print(f'{t0} only in {t0.o.parent}',file=of)

def main():

    for arg in sys.argv: 
        print(arg)

    topf = sys.argv[1]
    topt = sys.argv[2]
    tmpfile = pathsToTempfile(topf,topt)
    
    root = tk.Tk()
    root.title("tkdiff.py")
    
    fromString = tk.StringVar()
    toString   = tk.StringVar()
    fileString = tk.StringVar()

    fromString.set(topf)
    toString.set(topt)
    fileString.set(tmpfile)
    
    frm = ttk.Frame(root, padding=10)
    frm.grid()
    
    lf=ttk.Label(frm, text="From:")
    lfv = ttk.Entry(frm, textvariable=fromString)
    lt=ttk.Label(frm, text="To:")
    ltv = ttk.Entry(frm, textvariable=toString)
    lfunc=ttk.Label(frm, text="Func:")
    lfuncv = tk.Text(frm, width=80, height=5)
    lfi=ttk.Label(frm, text="File:")
    lfiv = ttk.Entry(frm, width=80, textvariable=fileString)
    
    lf.grid(column=0, row=0)
    lfv.grid(column=1, row=0, columnspan=3, sticky="nsew")
    lt.grid(column=0, row=1)
    ltv.grid(column=1, row=1, columnspan=3, sticky="nsew")
    lfunc.grid(column=0,row=2)
    lfuncv.grid(column=1,row=2, columnspan=3, sticky="nsew")
    lfi.grid(column=0,row=3)
    lfiv.grid(column=1,row=3, columnspan=3, sticky="nsew")
    
    def call_tk_diff():
        ofile = Path(fileString.get()).open(mode="w")
        functext = lfuncv.get("1.0","end -1c")
        func = compileFuncObj(functext)
        if func:
            print("KeyFunc:",file=ofile)
            print(functext,file=ofile)
            tk_diff(fromString.get(),toString.get(),ofile,func)
        else:
            tk_diff(fromString.get(),toString.get(),ofile)

    b2=ttk.Button(frm,text="Execute",command=call_tk_diff)
    b3=ttk.Button(frm, text="Quit", command=root.destroy)

    def call_tk_swap():
        tk_swap(fromString,toString,fileString)

    b4=ttk.Button(frm, text="Swap", command=call_tk_swap)
    
    # b1.grid(column=2, row=2, sticky="nsew")
    b2.grid(column=1, row=4, sticky="nsew")
    b3.grid(column=2, row=4, sticky="nsew")
    b4.grid(column=3, row=4, sticky="nsew")

    root.mainloop()

def tk_swap(f0,t0,o0):
    (f,t,o)=(f0.get(),t0.get(),o0.get())
    o = pathsToTempfile(t,f)
    f0.set(t)
    t0.set(f)
    o0.set(o)
    
def tk_diff(f,t,ofile,func=lambda n:n):
    do_diff(Path(f),Path(t),ofile,func)
    
def pathsToTempfile(topf,topt):
    fpath = Path(topf)
    tpath = Path(topt)
    fname = fpath.name
    tname = tpath.name
    parent = fpath.parent

    tmpfile = Path(parent).joinpath(f"{fname}-{tname}.diff.txt")
    return tmpfile

def compileFuncObj(text):
    g = dict()
    l = dict()
    exec(text,g,l)
    if l:
        return list(l.values())[0]

if __name__ == "__main__":
    main()

    

