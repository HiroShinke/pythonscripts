

import sys
import tkinter as tk
from tkinter import ttk
from pathlib import Path
import ziputil
import diffutil
import io
import re
import subprocess


class ContentsView(tk.Frame):

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        
        self.text = tk.Text(self)
        xsb = ttk.Scrollbar(self, orient=tk.HORIZONTAL,command=self.text.xview)
        ysb = ttk.Scrollbar(self, orient=tk.VERTICAL,command=self.text.yview)

        self.text.configure(yscroll=ysb.set,xscroll=xsb.set)
        self.text.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
        ysb.grid(row=0, column=1, sticky=tk.N+tk.S)
        xsb.grid(row=1, column=0, sticky=tk.E+tk.W)
        self.rowconfigure(0,weight=1)
        self.columnconfigure(0,weight=1)

    def setContents(self,contents):
        self.text.config(state='normal')
        self.text.delete("1.0","end -1c")
        self.text.insert("1.0",contents)

def main():

    for arg in sys.argv: 
        print(arg)

    argsnum = len(sys.argv)
    topf = sys.argv[1] if argsnum > 1 else ""
    topt = sys.argv[2] if argsnum > 2 else ""

    root = tk.Tk()
    root.title("tkdiff.py")
    
    frm = ttk.Frame(root, padding=10)
    frm.grid(row=0, column=0, sticky=tk.N+tk.W+tk.S+tk.E)    
    root.columnconfigure(0,weight=1)
    root.rowconfigure(0,weight=1)

    frm.columnconfigure(0,weight=1)
    frm.columnconfigure(1,weight=1)
    frm.columnconfigure(2,weight=1)
    frm.columnconfigure(3,weight=1)    
    frm.rowconfigure(0,weight=1)
    frm.rowconfigure(1,weight=3)
    
    pw = ttk.PanedWindow(frm,orient=tk.VERTICAL)
    lfv = ContentsView(pw, width=80, height=5)
    lfuncv = ContentsView(pw, width=80, height=10)
    lfuncv.setContents("cat testgitdir2/xxx/hello1.txt")
    pw.add(lfv)
    pw.add(lfuncv)
    pw.grid(column=0, row=0, columnspan=4, sticky="nsew")

    def cmd_stdout(cmdstr,print_=False):
        try:
            p = subprocess.run(cmdstr,
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               check=True)
            rets = p.stdout.decode("cp932")
            if print_:
                print(rets)
            return rets
        except Exception as e:
            if print_:
                print(e.stdout.decode("cp932"))
            raise e

    def exec_out():
        cmd = lfuncv.text.get(tk.SEL_FIRST, tk.SEL_LAST)        
        ret = cmd_stdout(cmd)
        toplevel = tk.Toplevel(root)
        cv = ContentsView(toplevel)
        cv.grid()
        cv.setContents(ret)
        print(ret)

    def exec_in():
        cmd = lfuncv.text.get(tk.SEL_FIRST, tk.SEL_LAST)
        ret = cmd_stdout(cmd)
        lfuncv.text.insert(tk.SEL_LAST,"\n" + ret)
        print(ret)
        
    b2=ttk.Button(frm,text="ExecIn",command=exec_in)
    b3=ttk.Button(frm,text="ExecOut",command=exec_out)
    b4=ttk.Button(frm, text="Quit", command=root.destroy)

    b2.grid(column=1, row=1, sticky="nsew")
    b3.grid(column=2, row=1, sticky="nsew")
    b4.grid(column=3, row=1, sticky="nsew")

    
    root.mainloop()
    

if __name__ == "__main__":
    main()

    
