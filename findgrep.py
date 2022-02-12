

import sys
from pathlib import Path
import argparse
import re

def do_path(path,proc,*args):
    if path.is_dir():
        do_dir(path,proc,*args)
    else:
        do_file(path,proc,*args)

def do_file(path,proc,*args):
    proc(path,*args)

def do_dir(path,proc,*args):
    for x in path.iterdir():
        do_path(x,proc,*args)

def proc1(path,pat):
    f = path.open(mode='r')
    for x in f:
        if pat.search(x):
            print(x,end='')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target",action='append')
    parser.add_argument("-e"    ,type=str,  action='store')
    args = parser.parse_args()
    pat = re.compile(args.e)
    
    for f in args.target:
        path = Path(f)
        do_path(path,proc1,pat)

if __name__ == "__main__":
    main()
    
