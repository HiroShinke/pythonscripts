

import tkinter as tk
import tkinter.ttk as ttk
from pathlib import Path

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
        
def main():

    root = tk.Tk()
    root.title("simple dir browser")
    
    treeview = TreeView(root)
    treeview.grid(row=0,column=0,columnspan=2,sticky=tk.N+tk.S+tk.E+tk.W)

    def event_printer(*args):
        print(f"{args}")
        print(f"{tree.focus()}")

    nodes = {}
    
    def tree_insert_item(p,parent):
        node = treeview.tree.insert(parent,tk.END,text=p.name,open=False)
        if p.is_dir():
            nodes[node] = p            
            treeview.tree.insert(node,tk.END)

    def tree_open_item(e):
        item = treeview.tree.focus()
        p = nodes.pop(item,False)
        if p:
            children = treeview.tree.get_children(item)
            treeview.tree.delete(children)
            for c in p.iterdir():
                tree_insert_item(c,item)

    button1 = ttk.Button(root,text="Button1")
    button1.grid(row=1,column=0,sticky=tk.W+tk.E)
    button2 = ttk.Button(root,text="Quit",command=root.destroy)
    button2.grid(row=1,column=1,sticky=tk.W+tk.E)
    root.columnconfigure(0,weight=1)
    root.rowconfigure(0,weight=1)
    
    treeview.tree.bind("<Double-1>",event_printer)
    treeview.tree.bind("<<TreeviewOpen>>",tree_open_item)
    treeview.tree.bind("<<TreeviewClose>>",event_printer)
    
    p = Path(".")
    tree_insert_item(p,"")
            
    root.mainloop()


if __name__ == "__main__":
    main()

