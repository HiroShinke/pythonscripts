

import sys
import tkinter as tk
from tkinter import ttk
from pathlib import Path
import diffutil


def do_diff(fp,tp,of,func=lambda n: n):
    if fp.is_file() and tp.is_file():
        do_difffile(fp,tp,of,func)
    elif fp.is_dir() and tp.is_dir():
        do_diffdir(fp,tp,of,func)
    else:
        print(f"uncomparable {fp} and {tp}",file=of)
    

def do_difffile(f,t,of,func):


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
                                discardBFunc=discard_b,
                                keyFunc=func)
    if diffOccurs:
        print(f"---{f}",file=of)
        print(f"+++{t}",file=of)
        of.writelines(lines)

def do_diffdir(f,t,of,func):

    seq1 = list( [ n1 for n1 in f.iterdir() ])
    seq2 = list( [ n2 for n2 in t.iterdir() ])

    def match_func(i,j):
        do_diff(seq1[i],seq2[j],of,func)

    def discard_a(i):
        print(f'{seq1[i]} only in {seq1[i].parent}',file=of)        

    def discard_b(j):
        print(f'{seq2[j]} only in {seq2[j].parent}',file=of)        
        
    diffutil.traverse_sequences(seq1,seq2,
                                matchFunc=match_func,
                                discardAFunc=discard_a,
                                discardBFunc=discard_b,
                                keyFunc=lambda x: x.name)

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

    

