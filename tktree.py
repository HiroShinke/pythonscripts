

import tkinter as tk
import tkinter.ttk as ttk
from pathlib import Path

def main():

    root = tk.Tk()
    root.title("simple dir browser")
    
    tree = ttk.Treeview(root)

    p = Path(".")
    nodes = {}
    
    def tree_insert_item(p,parent):
        node = tree.insert(parent,tk.END,text=p.name,open=False)
        if p.is_dir():
            nodes[node] = p            
            tree.insert(node,tk.END)

    def tree_open_item(e):
        item = tree.focus()
        p = nodes.pop(item,False)
        if p:
            children = tree.get_children(item)
            tree.delete(children)
            for c in p.iterdir():
                tree_insert_item(c,item)

    tree_insert_item(p,"")
            
    def event_printer(*args):
        print(f"{args}")
        print(f"{tree.focus()}")
    
    tree.bind("<Double-1>",event_printer)
    tree.bind("<<TreeviewOpen>>",tree_open_item)
    tree.bind("<<TreeviewClose>>",event_printer)
    tree.pack(expand=True,fill=tk.BOTH)

    button1 = ttk.Button(root,text="Button1")
    button1.pack(side=tk.LEFT)
    button2 = ttk.Button(root,text="Quit",command=root.destroy)
    button2.pack(side=tk.LEFT)

    root.mainloop()


if __name__ == "__main__":
    main()

