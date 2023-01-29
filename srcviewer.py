

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
                syntax_highlight(srcview.text,contents)
                srcview.text.config(state='disabled')
        
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
                srcview.text.config(state='disabled')                
            case CallItem(name,s,e) if s is not None:
                srcview.text.config(state='normal')
                srcview.text.tag_remove("sel","1.0","end")
                srcview.text.tag_add("sel",f"1.0 +{s}c",f"1.0 +{e}c")
                srcview.text.see(f"1.0 +{s}c")
                srcview.text.config(state='disabled')                


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

