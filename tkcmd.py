


from tkinter import *
from tkinter import ttk
import subprocess
import re

root = Tk()
frm = ttk.Frame(root, padding=10)
frm.grid()
ttk.Label(frm, text="Exceucte cmd in IDLE shell").grid(column=0, row=0)

def process_on_shell():
    cmd = re.split(r"\s+",
                   "python3 -m idlelib -r testconsole.py a b c")
    print(f"cmd = {cmd}")
    subprocess.run(cmd)

ttk.Button(frm, text="Execute", command=process_on_shell).grid(column=0, row=1)
ttk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=1)
root.mainloop()

