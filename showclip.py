
import sys
import tkinter as tk
import tkinter.scrolledtext
from tkinter import ttk

from ctypes import *

GetLastError     = windll.kernel32.GetLastError
GMEM_MOVEABLE = 0x002
CF_TEXT        = 0x0001

def get_clipboard_bytes():
    text = ""
    if windll.user32.OpenClipboard(c_int(0)):
        h_clip_mem = windll.user32.GetClipboardData(CF_TEXT)
        windll.kernel32.GlobalLock.restype = c_char_p
        b = windll.kernel32.GlobalLock(c_int(h_clip_mem))
        windll.kernel32.GlobalUnlock(c_int(h_clip_mem))
        windll.user32.CloseClipboard()
    return b


def set_clipboard_text(s):

    btext = bytes(s,"cp932")
    length = len(btext)
    
    if windll.user32.OpenClipboard(c_int(0)):

        hglb = windll.kernel32.GlobalAlloc(GMEM_MOVEABLE,
                                           length + 1)

        windll.kernel32.GlobalLock.restype = c_void_p
        lpstr = windll.kernel32.GlobalLock(c_int(hglb))

        strp = cast(lpstr,POINTER(c_char))

        memmove(strp,btext,length)
        strp[length] = c_char(0)

        windll.user32.EmptyClipboard()
        windll.user32.SetClipboardData(CF_TEXT,c_int(hglb))

        windll.kernel32.GlobalUnlock(c_int(hglb))
        windll.user32.CloseClipboard()


def main():

    root = tk.Tk()
    root.title("showclip")
    
    frm = ttk.Frame(root, padding=10)
    frm.grid(sticky="nsew")
    
    lfunc=ttk.Label(frm, text="Func:")
    lfuncv = tk.scrolledtext.ScrolledText(frm,height=10)

    default_proc_text = r"""

def default_proc(t):
    
    lines = t.splitlines()
    lines = [ ">> " + l + "\r\n" for l in lines ]
    return "".join(lines)

"""
    lfuncv.insert("1.0",default_proc_text)
    lfunc.grid(column=0,row=0,sticky="nsew")
    lfuncv.grid(column=1,row=0, columnspan=3, sticky="nsew")


    lclip=ttk.Label(frm, text="Result:")
    lclipv = tk.scrolledtext.ScrolledText(frm,height=10)

    lclip.grid(column=0,row=1,sticky="nsew")
    lclipv.grid(column=1,row=1, columnspan=3, sticky="nsew")


    def test_clipboard():
        functext = lfuncv.get("1.0","end -1c")
        func = compileFuncObj(functext)
        func = func if func else default_proc

        b = get_clipboard_bytes()
        t = str(b,"cp932")
        text = func(t)
        lclipv.delete("1.0","end -1c")
        lclipv.insert("1.0",text)
    
    def process_clipboard():
        functext = lfuncv.get("1.0","end -1c")
        func = compileFuncObj(functext)
        func = func if func else default_proc

        b = get_clipboard_bytes()
        t = str(b,"cp932")
        text = func(t)
        set_clipboard_text(text)

    b1=ttk.Button(frm,text="Test",   command=test_clipboard)
    b2=ttk.Button(frm,text="Execute",command=process_clipboard)
    b3=ttk.Button(frm, text="Quit", command=root.destroy)

    b1.grid(column=1, row=2, sticky="nsew")    
    b2.grid(column=2, row=2, sticky="nsew")
    b3.grid(column=3, row=2, sticky="nsew")

    root.grid_columnconfigure(0,weight=1)
    root.grid_rowconfigure(0,weight=1)

    frm.grid_columnconfigure(1,weight=1)
    frm.grid_columnconfigure(2,weight=1)
    frm.grid_columnconfigure(3,weight=1)    

    frm.grid_rowconfigure(0,weight=1)
    frm.grid_rowconfigure(1,weight=1)
    
    root.mainloop()

def default_proc(t):
    
    lines = t.splitlines()
    lines = [ ">> " + l + "\r\n" for l in lines ]
    return "".join(lines)

def compileFuncObj(text):
    l = dict()
    exec(text,globals(),l)
    if l:
        return list(l.values())[0]
    
if __name__ == "__main__":
    main()

