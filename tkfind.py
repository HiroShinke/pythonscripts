

import sys
import tkinter as tk
from tkinter import ttk
from pathlib import Path
import tkinter.filedialog as fd
import re

def do_rec_file(fp,proc):

    proc(fp)
    if fp.is_dir():
        for c in fp.iterdir():
            do_rec_file(c,proc)


class PyEditText(tk.Text):

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.bind("<Tab>",self.tab_event)
        self.bind("<Return>",self.return_event)

    def prev_indent(self,num_goback=1):

        while True:
            idx = self.index(f"insert -{num_goback}l linestart")
            prevline = self.get(f"insert -{num_goback}l linestart",
                                  f"insert -{num_goback}l lineend")
            if m := re.search(r"\S",prevline):
                s,_ = m.span()
                delta = 4 if re.search(r":$",prevline) else 0
                return (s+delta)
            elif idx == "1.0":
                break
            num_goback += 1

        return None
        
    def tab_event(self,e):

        prev_height = self.prev_indent()
        s = self.current_indent()
        l,c = self.location_linepos("insert")

        if c < s:
            self.mark_set("insert",f"insert linestart +{s}c")
        else:
            r = int(s)%4
            if prev_height is not None and s < prev_height:
                self.insert("insert linestart"," "*(4-r))
            else:
                self.delete("insert linestart",f"insert linestart +{s}c")

        return "break"

    def current_indent(self):
        line = self.get("insert linestart","insert lineend")
        if m := re.search(r"^\s*",line):
            _,s = m.span()
        else:
            s = 0
        return s

    def location_linepos(self,location):
        pos = self.index(location)
        if m := re.search(r"(\d+)\.(\d+)",pos):
            l,c= map(lambda x: int(x), m.groups())
            return l,c
        else:
            return None
    
    def return_event(self,e):

        prev_height = self.prev_indent(0)
        prev_height = 0 if prev_height is None else prev_height
        s = self.current_indent()
        l,c = self.location_linepos("insert")

        if c <= s:
            self.insert("insert linestart","\n")
            if s < prev_height:
                self.insert("insert linestart"," "*(prev_height-s))
            self.mark_set("insert",f"insert linestart +{prev_height}c")           
        else:
            text = self.get("insert","insert lineend")
            self.delete("insert","insert lineend")
            prev_height = self.prev_indent(0)
            if self.compare("insert +1l linestart","==","end"):
                # workaround the limitation of tk.Text insert command 
                # (https://www.tcl.tk/man/tcl8.5/TkCmd/text.html#M105")
                # pathName insert index chars ?tagList chars tagList ...?
                #  Inserts all of the chars arguments just before the character at index.
                #  If index refers to the end of the text
                #  (the character after the last newline) then the new text is
                #  inserted just before the last newline instead. "
                self.insert("end","\n" + " "*prev_height + text)
            else:
                self.insert("insert +1l linestart"," "*prev_height + text + "\n")
            self.mark_set("insert",f"insert +1l linestart +{prev_height}c")

        return "break"

    def print_event(e):
         lastchar = self.get("end -1c")
         print(f"lastchar = {list(lastchar)}")
         lastindex = self.index("end")
         print(f"lastindex = {lastindex}")            
         last1index = self.index("end -1c")
         print(f"last1index = {last1index}")            
            
def main():

    topf = sys.argv[1]
    tmpfile = pathsToTempfile(topf)
    
    root = tk.Tk()
    root.title("tkfind.py")
    
    fromString = tk.StringVar()
    patString  = tk.StringVar()
    fileString = tk.StringVar()
    typeString = tk.StringVar()
    
    fromString.set(topf)
    patString.set("")
    fileString.set(tmpfile)
    typeString.set("")
    
    frm = ttk.Frame(root, padding=10)
    frm.grid(column=0,row=0,sticky=tk.N+tk.S+tk.E+tk.W)
    root.columnconfigure(0,weight=1)
    root.rowconfigure(0,weight=1)
    
    lf=ttk.Label(frm, text="File:")
    lfv = ttk.Entry(frm, textvariable=fromString)
    lt=ttk.Label(frm, text="Type:")
    ltb1 = ttk.Radiobutton(frm, text="both",variable=typeString,value="")
    ltb2 = ttk.Radiobutton(frm, text="file",variable=typeString,value="f")
    ltb3 = ttk.Radiobutton(frm, text="dir" ,variable=typeString,value="d")
    lp=ttk.Label(frm, text="Pattan:")
    lfunc=ttk.Label(frm, text="Func:")
    lfuncv = PyEditText(frm, width=80, height=5)
    lpv = ttk.Entry(frm, textvariable=patString)

    lfi=ttk.Label(frm, text="Result:")
    lfiv = ttk.Entry(frm, width=80, textvariable=fileString)

    def choose_file():
        if filename := fd.askopenfilename(title="Open Directory",
                                          filetypes=[("","*")],
                                          initialdir="/"):
            fileString.set(filename)
        
    lf.grid(column=0, row=0)
    lfv.grid(column=1, row=0, columnspan=3, sticky=tk.N+tk.S+tk.E+tk.W)
    lt.grid(column=0, row=1)
    ltb1.grid(column=1, row=1, sticky=tk.N+tk.S+tk.E+tk.W)
    ltb2.grid(column=2, row=1, sticky=tk.N+tk.S+tk.E+tk.W)
    ltb3.grid(column=3, row=1, sticky=tk.N+tk.S+tk.E+tk.W)
    lp.grid(column=0, row=2)
    lpv.grid(column=1, row=2, columnspan=3, sticky=tk.N+tk.S+tk.E+tk.W)
    lfunc.grid(column=0,row=3)
    lfuncv.grid(column=1,row=3, columnspan=3, sticky=tk.N+tk.S+tk.E+tk.W)
    lfi.grid(column=0,row=4)
    lfiv.grid(column=1,row=4, columnspan=2, sticky=tk.N+tk.S+tk.E+tk.W)
    b1=ttk.Button(frm,text="File...",command=choose_file)
    b1.grid(column=3, row=4, columnspan=2, sticky=tk.N+tk.S+tk.E+tk.W)
    
    
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

        # of = Path(fileString.get()).open(mode='w')
        of = sys.stdout
        top = Path(fromString.get())

        functext = lfuncv.get("1.0","end -1c")            
        if functext:
            print("KeyFunc:",file=of)
            print(functext,file=of)
            func = compileFuncObj(functext)
        else:
            def func(f):
                relative = f.relative_to(top.parent)
                print(f"{relative}")
            
        def grep_proc(f):
            if pred(f) and ( pat is None or pat.search(f.name) ):
                func(f)
            
        do_rec_file(top,grep_proc)
            
    b2=ttk.Button(frm,text="Execute",command=call_do_grep)
    b3=ttk.Button(frm, text="Quit", command=root.destroy)

    # b1.grid(column=2, row=2, sticky=tk.N+tk.S+tk.E+tk.W)
    b2.grid(column=2, row=5, sticky=tk.N+tk.S+tk.E+tk.W)
    b3.grid(column=3, row=5, sticky=tk.N+tk.S+tk.E+tk.W)
    frm.columnconfigure(1,weight=1)
    frm.columnconfigure(2,weight=1)
    frm.columnconfigure(3,weight=1)
    frm.rowconfigure(3,weight=1)

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

    
