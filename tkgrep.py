

import sys
import tkinter as tk
from tkinter import ttk
from pathlib import Path
import re

def do_grep(fp,proc):
    if fp.is_file():
        do_grepfile(fp,proc)
    elif fp.is_dir():
        do_grepdir(fp,proc)
    else:
        print(f"uncomparable {fp}",file=of)
    
def do_grepfile(f,proc):
    proc(f)
    
def do_grepdir(f,proc):
    for c in f.iterdir():
        do_grep(c,proc)


def main():

    topf = sys.argv[1]
    tmpfile = pathsToTempfile(topf)
    
    root = tk.Tk()
    root.title("tkgrep.py")
    
    fromString = tk.StringVar()
    patString   = tk.StringVar()
    fileString = tk.StringVar()

    fromString.set(topf)
    patString.set("")
    fileString.set(tmpfile)
    
    frm = ttk.Frame(root, padding=10)
    frm.grid()
    
    lf=ttk.Label(frm, text="File:")
    lfv = ttk.Entry(frm, textvariable=fromString)
    lt=ttk.Label(frm, text="Pattan:")
    ltv = ttk.Entry(frm, textvariable=patString)
    lfi=ttk.Label(frm, text="Result:")
    lfiv = ttk.Entry(frm, width=80, textvariable=fileString)
    
    lf.grid(column=0, row=0)
    lfv.grid(column=1, row=0, columnspan=3, sticky="nsew")
    lt.grid(column=0, row=1)
    ltv.grid(column=1, row=1, columnspan=3, sticky="nsew")
    lfi.grid(column=0,row=3)
    lfiv.grid(column=1,row=3, columnspan=3, sticky="nsew")
    

    def call_do_grep():

        if patStr:= patString.get():

            pat = re.compile(patStr)
            of = Path(fileString.get()).open(mode='w')
            top = Path(fromString.get())
            
            def grep_proc(f):
                fh = f.open(mode='r')
                lines = enumerate(fh)
                relative = f.relative_to(top.parent)
                for i,x in lines:
                    if pat.search(x):
                        print(f"{relative}: {i}: {x}",end='',file=of)
            
            do_grep(top,grep_proc)

            
    b2=ttk.Button(frm,text="Execute",command=call_do_grep)
    b3=ttk.Button(frm, text="Quit", command=root.destroy)

    # b1.grid(column=2, row=2, sticky="nsew")
    b2.grid(column=2, row=4, sticky="nsew")
    b3.grid(column=3, row=4, sticky="nsew")

    root.mainloop()

    
def pathsToTempfile(topf):
    fpath  = Path(topf)
    fname  = fpath.name
    parent = fpath.parent
    tmpfile = Path(parent).joinpath(f"{fname}.grep.txt")
    return tmpfile

if __name__ == "__main__":
    main()

    
