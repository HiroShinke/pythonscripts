

import argparse
from pathlib import Path
import re
import sys

OUTFH = None

class Env:

    def __init__(self,*strenv):
        self._env = []
        for s in strenv:
            if s is None: continue
            for e in s.split(";"):
                self._env.append(e)

    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        return ";".join(self._env)

    def __repr__(self):
        args = ",".join(map(repr, self._env))
        return f"Env({args})"
    
    def __eq__(self,other):
        if isinstance(other,Env) and hash(self) == hash(other):
            return True
        else:
            return False

    def join(self,other):
        if other is None:
            return Env(*(self._env))
        elif isinstance(other,Env):
            pass
        else:
            raise TypeError(f"Env.join: self={self}, other={other}")
        return Env(*(self._env),*(other._env))
        
        
def build_dirs(pathes):

    ret = []
    def helper(p):
        if p.is_dir():
            ret.append(p)

    for p in pathes:
        do_file_rec(Path(p),helper)

    return ret


FIND_NAME = {}

def trace_rec(kind,name,envs,roots):

    if ret := FIND_NAME.get((kind,name,envs),None):
        return ret

    roots2 = adjust_path(kind,envs,roots)
    p = find_path(kind,name,roots2)
    
    print(f"Start: {kind},{name},{envs} -> {p}",file=OUTFH)
    FIND_NAME[(kind,name,envs)] = p

    if p:
        for k,n,e in get_names(p):
            envs2 = e.join(envs)
            q = trace_rec(k,n,envs2,roots)
            # print(f"Rel: {p} -> {q}",file=OUTFH)

    return p

def get_names(p):

    ret = []
    with open(p) as fh:
        for l in fh.read().splitlines():
            if m := re.search(r"^(\S+)\s+(\S+)(?:\s+(\S+))?$",l):
                cmd,name,envs = m.groups()
                ret.append((cmd,name,Env(envs)))
                print(f"Rel: {p} -> {(cmd,name,Env(envs))}",file=OUTFH)
    return ret
                

def adjust_path(k,es,roots):
    return roots

def find_path(kind,name,roots):

    def helper(p):
        if p.name == name:
            return str(p)
        else:
            return None

    for r in roots:
        if p := do_file_rec1(Path(r),helper):
            return p

    return None

def main():

    global OUTFH

    parser = argparse.ArgumentParser()
    parser.add_argument("--src","-s",action="append")
    parser.add_argument("--start_list","-l")
    parser.add_argument("--debug",action="store_true")
    parser.add_argument("--out","-o")
    args = parser.parse_args()

    srcs = args.src
    start_list = args.start_list

    if args.out:
        OUTFH = open(args.out,"w")
    else:
        OUTFh = sys.stdout

    rootdirs = build_dirs(srcs)
    print(f"rootdirs = {[str(r) for r in rootdirs]}",file=sys.stderr)
    
    with open(start_list) as fh:
        for l in fh.read().splitlines():
            if m := re.search(r"^(\S+)\s+(\S+)(?:\s+(\S+))?$",l):
                kind,name,envs = m.groups()
                trace_rec(kind,name,Env(envs),rootdirs)
    
def do_file_rec(p,proc,*args,**kwargs):
    
    proc(p,*args,**kwargs)
    if p.is_dir():
        for c in p.iterdir():
            do_file_rec(c,proc,*args,**kwargs)

def do_file_rec1(p,proc,*args,**kwargs):
    
    if m := proc(p,*args,**kwargs):
        return m
    if p.is_dir():
        for c in p.iterdir():
            if m := do_file_rec1(c,proc,*args,**kwargs):
                return m
    return None


if __name__ == "__main__":
    main()

