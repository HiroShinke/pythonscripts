

import sys

import shutil
import os
from pathlib import Path
import argparse
import re


def do_path(path,proc,*args,**kwargs):
    proc(path,*args,**kwargs)
    if path.is_dir():
        do_dir(path,proc,*args,**kwargs)

def do_dir(path,proc,*args,**kwargs):
    for x in path.iterdir():
        do_path(x,proc,*args,**kwargs)

def make_filelist(path):
    
    list = []
    def helper(p):
        if p.is_file():
            list.append(p)

    do_path(path,helper)
    return list

def copy_file(f,t):
    print(f"copy {f} to {t}")
    abspath = t.resolve()
    if abspath.parent:
        abspath.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(f,t)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f" ,type=str,  action='store')    
    parser.add_argument("-l" ,type=str,  action='store')    
    parser.add_argument("-t" ,type=str,  action='store')
    args = parser.parse_args()

    if (fromDir := args.f) and (toDir := args.t) :

        def helper():
            if args.l:
                fh = open(args.l)
                return [ Path.joinpath(Path(fromDir),l.strip()) for l in fh ]
            else:
                return make_filelist(Path(fromDir))

        list=helper()
            
        for f in list:
            relpath = f.relative_to(fromDir)
            topath  = Path.joinpath(Path(toDir),relpath)
            print(topath)
            if relpath != topath:
                copy_file(f,Path(topath))
            
if __name__ == "__main__":
    main()



    
