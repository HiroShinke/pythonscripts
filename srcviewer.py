

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as fd
import argparse
from pathlib import Path
import re

from dataclasses import dataclass

@dataclass
class PerformItem:
    name : str
    start : int | None
    end   : int | None

@dataclass
class CallItem:
    name : str
    start : int
    end   : int

class Treeview(tk.Frame):

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
    
        self.tree = ttk.Treeview(self,show="tree")
        xsb = ttk.Scrollbar(self, orient=tk.HORIZONTAL,command=self.tree.xview)
        ysb = ttk.Scrollbar(self, orient=tk.VERTICAL,command=self.tree.yview)

        self.tree.configure(yscroll=ysb.set,xscroll=xsb.set)
        self.tree.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
        ysb.grid(row=0, column=1, sticky=tk.N+tk.S)
        xsb.grid(row=1, column=0, sticky=tk.E+tk.W)
        self.rowconfigure(0,weight=1)
        self.columnconfigure(0,weight=1)


class ModelTreeview(Treeview):

    def __init__(self,*args,get_item=None,get_children=None,**kwargs):

        super().__init__(*args,**kwargs)

        self.dummy_nodes = {}
        self.all_nodes = {}

        self.get_children = get_children
        self.get_item = get_item
        self.tree.bind("<<TreeviewOpen>>",self.tree_open_item)

    def tree_insert_item(self,p,parent):

        param = self.get_item(p)
                
        node = self.tree.insert(parent,tk.END,**param,open=False)
        self.all_nodes[node] = p            
        if self.get_children(p):
            self.dummy_nodes[node] = p            
            self.tree.insert(node,tk.END)

    def tree_open_item(self,e):
        item = self.tree.focus()
        p = self.dummy_nodes.pop(item,False)
        if p:
            children = self.tree.get_children(item)
            self.tree.delete(children)
            for c in self.get_children(p):
                self.tree_insert_item(c,item)

    def clear_item(self):
        self.dummy_nodes.clear()
        self.all_nodes.clear()
        if items := self.tree.get_children():
            self.tree.delete(items)

    def tree_focus(self):
        item = self.tree.focus()
        return self.all_nodes.get(item,None)

class SrcView(tk.Frame):

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


def syntax_highlight(text,contents):

    text.tag_configure("keyword",foreground="orange")
    text.tag_configure("func",foreground="violet")
    text.tag_configure("literal",foreground="violet")    
    text.tag_configure("funcname",foreground="blue")
    text.tag_configure("lhs",foreground="orange")

    def open_link(e):
        print(f"text button : event = {e}")
        position = f"@{e.x},{e.y} +1c"
        index = text.index(position)
        prevrange = text.tag_prevrange("literal",index)
        literal = text.get(*prevrange)
        print(f"literal = {literal}")

    text.tag_bind("literal","<Button-1>",open_link)

    
    token_specification = [
        ("keyword", r"(?<!\w)(def|class|for|from|if|in)(?!\w)"),
        ("func",r"(?<!\w)(print|len|open|write)(?!\w)"),
        ("literal",r'"[^"]+"'),
        ("funcname",r"(?<=def)\s+\w+"),
        ("lhs",r"\w+(?=\s+=)")
    ]
    
    token_pat = '|'.join(f'(?P<{p}>{pat})'
                         for p,pat in token_specification)
    expre = re.compile(token_pat)
    
    for m in expre.finditer(contents):
        token_type = m.lastgroup            
        start,end = m.span(token_type)
        text.tag_add(token_type,f"1.0 +{start}c",f"1.0 +{end}c")

def cobol_src_analyze(contents):

    lines = contents.splitlines()

    pat = re.compile(r"^.{6}\*")

    line_specification = [
        ("perform", r"(?<!\w)PERFORM\s+([\w-]+)"),
        ("division", r"(\S+)\s+DIVISION(?!\w)"),
        ("section",r"(\S+)\s+SECTION\s*\."),
        ("call",  r"""(?<!\w)CALL\s+["']([^"']+)['"]""")
    ]
    line_pat = '|'.join(f'(?P<{p}>{pat})'
                         for p,pat in line_specification)
    expre = re.compile(line_pat)
    inProcedureDivision = False

    currentSec = None
    perform_dict = {}
    entrySec = None

    pos = 0
    
    for l in lines:

        if pat.search(l):
            pass
        elif m := expre.search(l):
            tokentype = m.lastgroup
            word = m.group(m.lastindex + 1)
            # print(f"{tokentype},{word}")
            start,end = m.span(tokentype)
            if tokentype == "division":
                if word == "PROCEDURE":
                    inProcedureDivision = True
            elif inProcedureDivision and tokentype == "section":
                currentSec = word
                if entrySec is None:
                    entrySec = currentSec
            elif tokentype == "perform":
                if ( word != "VARYING" and
                     word != "UNTIL" and
                     word != "TIMES" ):
                    register_multivalue(perform_dict,
                                        currentSec,
                                        PerformItem(word,
                                                    pos + start,
                                                    pos + end))
            elif tokentype == "call":
                register_multivalue(perform_dict,
                                    currentSec,
                                    CallItem(word,
                                             pos + start,
                                             pos + end))
        pos += len(l) + 1

    # print(f"{perform_dict}")

    def recursivePrintSec(p,lev):
        print(" " * lev, p)
        for c in perform_dict.get(p,[]):
            recursivePrintSec(c.name,lev+1)

    recursivePrintSec(entrySec,0)

    return (entrySec,perform_dict)


def cobol_syntax_highlight(text,contents):

    text.tag_configure("comment",foreground="violet")
    text.tag_configure("keyword",foreground="pink")
    text.tag_configure("literal",foreground="blue")    
    text.tag_configure("callname",foreground="orange")
    text.tag_configure("section",foreground="orange")
    
    def open_link(e):
        print(f"text button : event = {e}")
        position = f"@{e.x},{e.y} +1c"
        index = text.index(position)
        prevrange = text.tag_prevrange("callname",index)
        callname = text.get(*prevrange)
        print(f"literal = {callname}")

    text.tag_bind("callname","<Button-1>",open_link)
    text.tag_bind("callname", "<Enter>", lambda _: text.config(cursor="hand2"))
    text.tag_bind("callname", "<Leave>", lambda _: text.config(cursor=""))    
                  
    lines = contents.splitlines()

    pat = re.compile(r"^.{6}\*.*")

    line_specification = [
        ("perform", r"(?<!\w)PERFORM\s+([\w-]+)"),
        ("division", r"(\S+)\s+DIVISION(?!\w)"),
        ("section",r"(\S+)\s+SECTION\s*\."),
        ("callname",  r"""(?<!\w)CALL\s+["']([^"']+)['"]"""),
        ("keyword", r"(?<=\s)(COPY|MOVE|ADD|IF|WHEN|EVALUATE|GO|TO)(?=\s)")
    ]
    line_pat = '|'.join(f'(?P<{p}>{pat})'
                         for p,pat in line_specification)

    expre = re.compile(line_pat)
    pos = 0
    
    for l in lines:

        if m := pat.search(l):
            start0,end0 = m.span()
            start = start0 + pos
            end   = end0 + pos
            text.tag_add("comment",f"1.0 +{start}c",f"1.0 +{end}c")
        elif m := expre.search(l):
            tokentype = m.lastgroup
            word = m.group(m.lastindex + 1)
            # print(f"{tokentype},{word}")
            start0,end0 = m.span(tokentype)
            start = start0 + pos
            end   = end0 + pos
            if tokentype == "division":
                text.tag_add("division",f"1.0 +{start}c",f"1.0 +{end}c")
            elif tokentype == "section":
                text.tag_add("section",f"1.0 +{start}c",f"1.0 +{end}c")
            elif tokentype == "literal":
                text.tag_add("literal",f"1.0 +{start}c",f"1.0 +{end}c")
            elif tokentype == "keyword":
                text.tag_add("keyword",f"1.0 +{start}c",f"1.0 +{end}c")
            elif tokentype == "perform":
                if ( word != "VARYING" and
                     word != "UNTIL" and
                     word != "TIMES" ):
                    pass
            elif tokentype == "callname":
                text.tag_add("callname",f"1.0 +{start}c",f"1.0 +{end}c")

        pos += len(l) + 1

            
def register_multivalue(dict,k,v):
    e = dict.get(k,None)
    if e is None:
        dict[k] = e = [] 
    e.append(v)


def rec_find_file(p,proc,*args,**kwargs):

    if proc(p,*args,**kwargs):
        return p

    if p.is_dir():
        for c in p.iterdir():
            if q := rec_find_file(c,proc,*args,**kwargs):
                return q
    return None

def includedir_find(incdir,w):
    def name_equal(p):
        return p.is_file() and p.stem == w
    return rec_find_file(incdir,name_equal)


def show_dialog_func(e,root,srcview):

    frame = tk.Toplevel(root)
        
    frame.geometry(f"+{srcview.winfo_x()+e.x}+{srcview.winfo_y()+e.y}")
    entry = ttk.Entry(frame)
    label = tk.Label(frame, text="Search for ...", anchor=tk.W)

    findresult = []
    pos = 0

    def find_text_select():
        
        nonlocal pos
        text = entry.get()
        
        if text:
            src = srcview.text.get("1.0","end -1c")
            findresult.clear()
            findresult.extend(re.finditer(text,src))
            if findresult:
                pos = 0
                count = len(findresult)                    
                label.config(text = f"Found {pos+1}/{count} item")
                s,e=findresult[pos].span()                
                srcview.text.tag_remove("sel","1.0","end")
                srcview.text.tag_add("sel",f"1.0 +{s}c",f"1.0 +{e}c")
                srcview.text.see(f"1.0 +{s}c")
            else:
                label.config(text = "Not Found ...")

    def find_next_select():

        nonlocal pos

        if findresult and pos + 1 < len(findresult):
            pos += 1
            count = len(findresult)                
            label.config(text = f"Found {pos+1}/{count} item")
            s,e=findresult[pos].span()
            srcview.text.tag_remove("sel","1.0","end")
            srcview.text.tag_add("sel",f"1.0 +{s}c",f"1.0 +{e}c")
            srcview.text.see(f"1.0 +{s}c")
        else:
            pos = -1
            label.config(text = "Wrapping Search from Start ...")
            
            
    button1 = ttk.Button(frame,text="Find",command=find_text_select)
    button2 = ttk.Button(frame,text="Next",command=find_next_select)
    button3 = ttk.Button(frame,text="Close",command=frame.destroy)
    entry.grid(row=0,column=0,columnspan=3,sticky=tk.W+tk.E)
    label.grid(row=1,column=0,columnspan=3,sticky=tk.W+tk.E)
    button1.grid(row=2,column=0,sticky=tk.W+tk.E)
    button2.grid(row=2,column=1,sticky=tk.W+tk.E)
    button3.grid(row=2,column=2,sticky=tk.W+tk.E)
    frame.columnconfigure(0,weight=1)
    frame.columnconfigure(1,weight=1)
    frame.columnconfigure(2,weight=1)        
    # frame.focus_force()
    entry.focus()
    
    # frame.grab_set()


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--srcdir", "-s")
    parser.add_argument("--incdir", "-i")    
    args = parser.parse_args()
    
    targetDir = Path(args.srcdir if args.srcdir else ".")
    srcEncoding = "euc-jp"
    includeDir = Path(args.incdir if args.incdir else ".")
    
    root = tk.Tk()
    paned = tk.PanedWindow(root)
    root.title("Simple source browser")

    def get_item(p): return dict( text = p.name )
    def get_children(p): return p.iterdir() if p.is_dir() else None
    
    treeview = ModelTreeview(paned,get_item=get_item,get_children=get_children)
    paned.add(treeview)

    get_callee_cache = {}
    
    def get_callee(p):

        if m := get_callee_cache.get(p,None):
            return m

        ret = set()
        with open(p,encoding=srcEncoding) as fh:
            lines = fh.read().splitlines()
            for l in lines:
                if re.search(r".{6]\*",l):
                    continue
                elif m := re.search(r"""\sCALL\s+["']([^"']+)["']""",l):
                    w = m.group(1)
                    print(f"w = {w}")
                    if q := includedir_find(includeDir,w):
                        ret.add(q)

        get_callee_cache[p] = ret
        return ret
                        
    
    calltree = ModelTreeview(paned,get_item=get_item,get_children=get_callee)
    paned.add(calltree)
    
    calldict = {}
    
    def get_item2(p):
        match p:
            case PerformItem():
                tag = "perform"
            case CallItem():
                tag = "call"
            case _:
                tag = None
        return dict(text = p.name, tag  = tag )

    def get_children2(p):
        return calldict.get(p.name,[])
    
    treeview2 = ModelTreeview(paned,get_item=get_item2,get_children=get_children2)
    paned.add(treeview2)

    srcview = SrcView(paned)
    paned.add(srcview)

    def event_printer(*args):
        print(f"{args}")
        print(f"{treeview.tree.focus()}")
        
    def refresh_tree():
        if filename := fd.askdirectory(title="Open Directory",initialdir="/"):
            p = Path(filename)
            treeview.tree_insert_item(p,"")
        
    def tree_select_item(e):
        p = treeview.tree_focus()
        print(f"{p}")
        item_view_src(p)
        item_analyze_src(p)
        if p.is_file():
            calltree.clear_item()
            calltree.tree_insert_item(p,"")        
        
    def item_view_src(p):
        if p.is_file():
            with open(p,encoding=srcEncoding) as fh:
                contents = fh.read()
                srcview.text.config(state='normal')
                srcview.text.delete("1.0","end -1c")
                srcview.text.insert("1.0",contents)
                # syntax_highlight(srcview.text,contents)
                cobol_syntax_highlight(srcview.text,contents)                
                # srcview.text.config(state='disabled')
        
    def item_analyze_src(p):
        if p.is_file():
            with open(p,encoding=srcEncoding) as fh:
                contents = fh.read()
                entrySec,retdict = cobol_src_analyze(contents)

            treeview2.clear_item()
            calldict.clear()
            calldict.update(retdict)
    
            treeview2.tree.tag_configure("perform",foreground="violet")
            treeview2.tree.tag_configure("call",foreground="orange")
            treeview2.tree_insert_item(PerformItem(entrySec,None,None),"")

    def tree_select_item2(e):
        p = treeview2.tree_focus()
        print(f"p = {p}")
        match p:
            case PerformItem(name,s,e) if s is not None:
                srcview.text.config(state='normal')
                srcview.text.tag_remove("sel","1.0","end")
                srcview.text.tag_add("sel",f"1.0 +{s}c",f"1.0 +{e}c")
                srcview.text.see(f"1.0 +{s}c")
                # srcview.text.config(state='disabled')                
            case CallItem(name,s,e) if s is not None:
                srcview.text.config(state='normal')
                srcview.text.tag_remove("sel","1.0","end")
                srcview.text.tag_add("sel",f"1.0 +{s}c",f"1.0 +{e}c")
                srcview.text.see(f"1.0 +{s}c")
                # srcview.text.config(state='disabled')                


    paned.grid(row=0,column=0,columnspan=4,sticky=tk.N+tk.S+tk.E+tk.W)
    button1 = ttk.Button(root,text="Reload...",command=refresh_tree)
    button1.grid(row=1,column=2,sticky=tk.W+tk.E)
    button2 = ttk.Button(root,text="Quit",command=root.destroy)
    button2.grid(row=1,column=3,sticky=tk.W+tk.E)
    root.columnconfigure(1,weight=1)
    root.columnconfigure(2,weight=1)
    root.columnconfigure(3,weight=1)
    root.rowconfigure(0,weight=1)
    
    treeview.tree.bind("<Double-1>",event_printer)
    treeview.tree.bind("<<TreeviewSelect>>",tree_select_item)
    treeview2.tree.bind("<<TreeviewSelect>>",tree_select_item2)


    def show_dialog(e):
        show_dialog_func(e,root,srcview)
    
        
    srcview.text.bind("<Button-1>",event_printer)
    srcview.text.bind("<Control-f>",show_dialog)
    srcview.text.bind("<Key>", lambda e: "break")
    
    menubar = tk.Menu(root)
    file_menu = tk.Menu(menubar, tearoff=False)
    file_menu.add_command(label="Open new file...", command=refresh_tree)
    file_menu.add_command(label="Quit", command=root.destroy)
    menubar.add_cascade(label="File", menu = file_menu)
    root.config(menu = menubar)

    treeview.tree_insert_item(targetDir,"")
            
    root.mainloop()


if __name__ == "__main__":
    main()

