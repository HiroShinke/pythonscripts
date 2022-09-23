

import sys
import tkinter as tk
from tkinter import ttk
from pathlib import Path
import re

def do_rec_file(fp,proc):

    proc(fp)
    if fp.is_dir():
        for c in fp.iterdir():
            do_rec_file(c,proc)

            
def main():

    topf = sys.argv[1]
    tmpfile = pathsToTempfile(topf)
    
    root = tk.Tk()
    root.title("tkgrep.py")
    
    fromString = tk.StringVar()
    patString  = tk.StringVar()
    fileString = tk.StringVar()
    typeString = tk.StringVar()
    
    fromString.set(topf)
    patString.set("")
    fileString.set(tmpfile)
    typeString.set("")
    
    frm = ttk.Frame(root, padding=10)
    frm.grid()
    
    lf=ttk.Label(frm, text="File:")
    lfv = ttk.Entry(frm, textvariable=fromString)
    lt=ttk.Label(frm, text="Type:")
    ltb1 = ttk.Radiobutton(frm, text="both",variable=typeString,value="")
    ltb2 = ttk.Radiobutton(frm, text="file",variable=typeString,value="f")
    ltb3 = ttk.Radiobutton(frm, text="dir" ,variable=typeString,value="d")
    lp=ttk.Label(frm, text="Pattan:")
    lfunc=ttk.Label(frm, text="Func:")
    lfuncv = tk.Text(frm, width=80, height=5)
    lpv = ttk.Entry(frm, textvariable=patString)



    lfi=ttk.Label(frm, text="Result:")
    lfiv = ttk.Entry(frm, width=80, textvariable=fileString)
    
    lf.grid(column=0, row=0)
    lfv.grid(column=1, row=0, columnspan=3, sticky="nsew")
    lt.grid(column=0, row=1)
    ltb1.grid(column=1, row=1, sticky="nsew")
    ltb2.grid(column=2, row=1, sticky="nsew")
    ltb3.grid(column=3, row=1, sticky="nsew")
    lp.grid(column=0, row=2)
    lpv.grid(column=1, row=2, columnspan=3, sticky="nsew")
    lfunc.grid(column=0,row=3)
    lfuncv.grid(column=1,row=3, columnspan=3, sticky="nsew")
    lfi.grid(column=0,row=4)
    lfiv.grid(column=1,row=4, columnspan=3, sticky="nsew")
    

    def call_do_grep():

        if patStr:= patString.get():
            pat = re.compile(patStr)
        else:
            pat = None

        type = typeString.get()

        if not type:
            def pred(f):
                return True
        elif type == "f":
            def pred(f):
                return f.is_file()
        elif type == "d":
            def pred(f):
                return f.is_dir()

        of = Path(fileString.get()).open(mode='w')
        top = Path(fromString.get())

        functext = lfuncv.get("1.0","end -1c")            
        if functext:
            print("KeyFunc:",file=of)
            print(functext,file=of)
            func = compileFuncObj(functext)
        else:
            def func(f,of):
                relative = f.relative_to(top.parent)
                print(f"{relative}",file=of)
            
        def grep_proc(f):
            if pred(f) and ( pat is None or pat.search(f.name) ):
                func(f,of)
            
        do_rec_file(top,grep_proc)
            
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

def compileFuncObj(text):
    l = dict()
    exec(text,globals(),l)
    if l:
        return list(l.values())[0]

if __name__ == "__main__":
    main()

    
