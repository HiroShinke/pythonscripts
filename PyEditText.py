

import tkinter as tk
import tkinter.ttk as ttk
import re


class PyEditText(tk.Text):

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.bind("<Tab>",self.tab_event)
        self.bind("<Return>",self.return_event)
        self.bind("<Key>",self.syntax_highlight)

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

    def syntax_highlight(self,e):

        self.tag_configure("keyword",foreground="orange")
        self.tag_configure("func",foreground="violet")
        self.tag_configure("literal",foreground="violet")    
        self.tag_configure("funcname",foreground="blue")
        self.tag_configure("lhs",foreground="orange")
        
        token_specification = [
            ("keyword", r"(?<!\w)(def|class|for|from|if|in|while)(?!\w)"),
            ("func",r"(?<!\w)(print|len|open|write)(?!\w)"),
            ("literal",r'"[^"]+"'),
            ("funcname",r"(?<=def)\s+\w+"),
            ("lhs",r"\w+(?=\s+=)")
        ]
        
        token_pat = '|'.join(f'(?P<{p}>{pat})'
                             for p,pat in token_specification)
        expre = re.compile(token_pat)
        
        contents = self.get("1.0","end")

        for m in expre.finditer(contents):
            token_type = m.lastgroup            
            start,end = m.span(token_type)
            self.tag_add(token_type,f"1.0 +{start}c",f"1.0 +{end}c")

    
    def print_event(e):
         lastchar = self.get("end -1c")
         print(f"lastchar = {list(lastchar)}")
         lastindex = self.index("end")
         print(f"lastindex = {lastindex}")            
         last1index = self.index("end -1c")
         print(f"last1index = {last1index}")            
            

if __name__ == "__main__":
    
    root = tk.Tk()
    root.title("PyEditText test")
    
    text=PyEditText(root)
    text.pack(expand=True,fill=tk.BOTH)

    root.mainloop()

    
