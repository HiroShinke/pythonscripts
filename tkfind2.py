

import sys
import tkinter as tk
from tkinter import ttk
from pathlib import Path
import tkinter.filedialog as fd
import re
import PyEditText
import tkfind2work
import threading


def main():

    topf = sys.argv[1]
    tmpfile = pathsToTempfile(topf)
    
    root = tk.Tk()
    root.title("tkfind.py")
    
    fromString = tk.StringVar()
    patString  = tk.StringVar()
    linePatString = tk.StringVar()
    fileString = tk.StringVar()
    typeString = tk.StringVar()
    countString = tk.StringVar()
    pbval = tk.DoubleVar(value=00.0)
    
    fromString.set(topf)
    patString.set("")
    linePatString.set("")
    fileString.set(tmpfile)
    typeString.set("")
    countString.set("Count: 0/0")
    
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
    lp=ttk.Label(frm, text="FilePattan:")
    llp=ttk.Label(frm, text="LinePattan:")
    lfunc=ttk.Label(frm, text="FileFunc:")
    lfuncv = PyEditText.PyEditText(frm, width=80, height=5)
    lfuncv.insert("1.0","""\
def filefunc(p):
    with open(p) as fh:
        contents = fh.read()
        lines = contents.splitlines()
        for l in lines:
            if re.search("def ",l):
                print(f"{p} {l}")
""")
    lfuncv.syntax_highlight(None)
    
    lpv = ttk.Entry(frm, textvariable=patString)
    llpv = ttk.Entry(frm, textvariable=linePatString)

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
    llp.grid(column=0, row=3)
    llpv.grid(column=1, row=3, columnspan=3, sticky=tk.N+tk.S+tk.E+tk.W)
    lfunc.grid(column=0,row=4)
    lfuncv.grid(column=1,row=4, columnspan=3, sticky=tk.N+tk.S+tk.E+tk.W)
    lfi.grid(column=0,row=5)
    lfiv.grid(column=1,row=5, columnspan=2, sticky=tk.N+tk.S+tk.E+tk.W)
    b1=ttk.Button(frm,text="File...",command=choose_file)
    b1.grid(column=3, row=5, columnspan=2, sticky=tk.N+tk.S+tk.E+tk.W)



    pb = ttk.Progressbar(frm,
                         orient=tk.HORIZONTAL,
                         variable=pbval,
                         maximum=1.0,
                         mode='determinate')
    pb.grid(row=7, column=1, columnspan=3,sticky=tk.N+tk.S+tk.E+tk.W)

    LOCK = threading.Lock()
    WORK_CANCELED = False

    def on_finished(count_proc,count_done):

        nonlocal WORK_CANCELED

        if count_proc is None:
            with LOCK:
                b2.config(text="Execute")
                WORK_CANCELED = False
                return WORK_CANCELED
        else:
            countString.set(f"Count: {count_proc}/{count_done}")
            pbval.set(0 if count_proc == 0 else count_done/count_proc)
            with LOCK:
                return WORK_CANCELED                

    def call_do_grep():

        nonlocal WORK_CANCELED

        try:
            functext = lfuncv.get("1.0","end -1c")
            compileFuncObj(functext)
        except Exception as e:
            functext = None

        with LOCK:
            if b2["text"] == "Execute":
                b2.config(text="Cancel...")
                thread = threading.Thread(target=tkfind2work.call_do_grep,
                                          args=(Path(fromString.get()),
                                                patString.get(),
                                                linePatString.get(),
                                                typeString.get(),
                                                functext,
                                                on_finished))
                thread.daemon = True
                thread.start()
            elif b2["text"] == "Cancel...":
                WORK_CANCELED = True


    lfc = ttk.Label(frm, textvariable=countString)
    b2=ttk.Button(frm,text="Execute",command=call_do_grep)
    b3=ttk.Button(frm, text="Quit", command=root.destroy)
    lfc.grid(column=1, row=6,sticky=tk.N+tk.S+tk.E+tk.W)
    b2.grid(column=2, row=6, sticky=tk.N+tk.S+tk.E+tk.W)
    b3.grid(column=3, row=6, sticky=tk.N+tk.S+tk.E+tk.W)
    frm.columnconfigure(1,weight=1)
    frm.columnconfigure(2,weight=1)
    frm.columnconfigure(3,weight=1)
    frm.rowconfigure(4,weight=1)

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
        #return list(l.values())[0]
        return l["filefunc"]

if __name__ == "__main__":
    main()

    
