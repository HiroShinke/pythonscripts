

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as fd
import argparse
from pathlib import Path
import re

from dataclasses import dataclass

@dataclass
class PerformItem:
    performName : str
    start : int | None
    end   : int | None

class TreeView(tk.Frame):

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
        ("call", r'(?<!\w)CALL\s+["\']([^\.]+)["\']')
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
                pass

        pos += len(l) + 1

    # print(f"{perform_dict}")

    def recursivePrintSec(p,lev):
        print(" " * lev, p)
        for c in perform_dict.get(p,[]):
            recursivePrintSec(c.performName,lev+1)

    recursivePrintSec(entrySec,0)

    return (entrySec,perform_dict)
    
            
def register_multivalue(dict,k,v):
    e = dict.get(k,None)
    if e is None:
        dict[k] = e = [] 
    e.append(v)

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--srcdir", "-s")
    parser.add_argument("--incdir", "-i")    
    args = parser.parse_args()
    
    targetDir = args.srcdir if args.srcdir else "."
    srcEncoding = "euc-jp"
    
    root = tk.Tk()
    root.title("simple dir browser")
    
    treeview = TreeView(root)
    treeview.grid(row=0,column=0,sticky=tk.N+tk.S+tk.E+tk.W)

    treeview2 = TreeView(root)
    treeview2.grid(row=0,column=1,sticky=tk.N+tk.S+tk.E+tk.W)

    srcview = SrcView(root)
    srcview.grid(row=0,column=2,columnspan=2,sticky=tk.N+tk.S+tk.E+tk.W)

    def event_printer(*args):
        print(f"{args}")
        print(f"{treeview.tree.focus()}")
        
    def refresh_tree():
        if filename := fd.askdirectory(title="Open Directory",initialdir="/"):
            p = Path(filename)
            tree_insert_item(p,"")
        
    dummy_nodes = {}
    all_nodes = {}
    
    def tree_insert_item(p,parent):
        node = treeview.tree.insert(parent,tk.END,text=p.name,open=False)
        all_nodes[node] = p            
        if p.is_dir():
            dummy_nodes[node] = p            
            treeview.tree.insert(node,tk.END)

    def tree_open_item(e):
        item = treeview.tree.focus()
        p = dummy_nodes.pop(item,False)
        if p:
            children = treeview.tree.get_children(item)
            treeview.tree.delete(children)
            for c in p.iterdir():
                tree_insert_item(c,item)

    dummy_nodes2 = {}
    all_nodes2 = {}
    calldict = {}
    
    def tree_insert_item2(p,parent):
        node = treeview2.tree.insert(parent,tk.END,text=p.performName,open=False)
        all_nodes2[node] = p            
        if p.performName in calldict:
            dummy_nodes2[node] = p            
            treeview2.tree.insert(node,tk.END)

    def tree_open_item2(e):
        item = treeview2.tree.focus()
        p = dummy_nodes2.pop(item,False)
        if p:
            children = treeview2.tree.get_children(item)
            treeview2.tree.delete(children)
            for c in calldict[p.performName]:
                tree_insert_item2(c,item)

    def tree_select_item(e):
        item = treeview.tree.focus()
        print(f"{item}")
        item_view_src(item)
        item_analyze_src(item)
        
    def item_view_src(item):
        p = all_nodes[item]
        if p.is_file():
            with open(p,encoding=srcEncoding) as fh:
                contents = fh.read()
                srcview.text.delete("1.0","end -1c")
                srcview.text.insert("1.0",contents)
                syntax_highlight(srcview.text,contents)
        
    def item_analyze_src(item):
        p = all_nodes[item]
        if p.is_file():
            with open(p,encoding=srcEncoding) as fh:
                contents = fh.read()
                entrySec,retdict = cobol_src_analyze(contents)

            dummy_nodes2.clear()
            all_nodes2.clear()
            calldict.clear()
            calldict.update(retdict)
            if items := treeview2.tree.get_children():
                treeview2.tree.delete(items)
            tree_insert_item2(PerformItem(entrySec,None,None),"")

    def tree_select_item2(e):
        item = treeview2.tree.focus()
        p = all_nodes2[item]
        print(f"p = {p}")
        match p:
            case PerformItem(name,s,e) if s is not None:
                srcview.text.tag_remove("sel","1.0","end")
                srcview.text.tag_add("sel",f"1.0 +{s}c",f"1.0 +{e}c")
                srcview.text.see(f"1.0 +{s}c")
                
    button1 = ttk.Button(root,text="Reload...",command=refresh_tree)
    button1.grid(row=1,column=2,sticky=tk.W+tk.E)
    button2 = ttk.Button(root,text="Quit",command=root.destroy)
    button2.grid(row=1,column=3,sticky=tk.W+tk.E)
    root.columnconfigure(1,weight=1)
    root.columnconfigure(2,weight=1)
    root.columnconfigure(3,weight=1)
    root.rowconfigure(0,weight=1)
    
    treeview.tree.bind("<Double-1>",event_printer)
    treeview.tree.bind("<<TreeviewOpen>>",tree_open_item)
    treeview.tree.bind("<<TreeviewClose>>",event_printer)
    treeview.tree.bind("<<TreeviewSelect>>",tree_select_item)

    treeview2.tree.bind("<<TreeviewOpen>>",tree_open_item2)
    treeview2.tree.bind("<<TreeviewSelect>>",tree_select_item2)
    
    menubar = tk.Menu(root)
    file_menu = tk.Menu(menubar, tearoff=False)
    file_menu.add_command(label="Open new file...", command=refresh_tree)
    file_menu.add_command(label="Quit", command=root.destroy)
    menubar.add_cascade(label="File", menu = file_menu)
    root.config(menu = menubar)

    
    p = Path(targetDir)
    tree_insert_item(p,"")
            
    root.mainloop()


if __name__ == "__main__":
    main()

