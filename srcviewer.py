

import tkinter as tk
import tkinter.ttk as ttk
from pathlib import Path
import re

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

        
def main():

    root = tk.Tk()
    root.title("simple dir browser")
    
    treeview = TreeView(root)
    treeview.grid(row=0,column=0,columnspan=2,sticky=tk.N+tk.S+tk.E+tk.W)

    srcview = SrcView(root)
    srcview.grid(row=0,column=2,columnspan=2,sticky=tk.N+tk.S+tk.E+tk.W)

    def event_printer(*args):
        print(f"{args}")
        print(f"{treeview.tree.focus()}")
        
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

    def tree_select_item(e):
        item = treeview.tree.focus()
        print(f"{item}")
        p = all_nodes[item]
        if p.is_file():
            with open(p) as fh:
                contents = fh.read()
                srcview.text.delete("1.0","end -1c")
                srcview.text.insert("1.0",contents)
                syntax_highlight(srcview.text,contents)
                

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

    button1 = ttk.Button(root,text="Button1")
    button1.grid(row=1,column=0,sticky=tk.W+tk.E)
    button2 = ttk.Button(root,text="Quit",command=root.destroy)
    button2.grid(row=1,column=1,sticky=tk.W+tk.E)
    root.columnconfigure(0,weight=1)
    root.columnconfigure(1,weight=1)    
    root.rowconfigure(0,weight=1)
    
    treeview.tree.bind("<Double-1>",event_printer)
    treeview.tree.bind("<<TreeviewOpen>>",tree_open_item)
    treeview.tree.bind("<<TreeviewClose>>",event_printer)
    treeview.tree.bind("<<TreeviewSelect>>",tree_select_item)    
    
    p = Path(".")
    tree_insert_item(p,"")
            
    root.mainloop()


if __name__ == "__main__":
    main()

