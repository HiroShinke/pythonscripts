

import argparse
from pathlib import Path
import importlib
import re
import sys

OUTFH = None

class Env:

    def __init__(self,*strenv):
        self._env = []
        for s in strenv:
            if s is None: continue
            if s == "" : continue
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

        items = list(dict.fromkeys([*(self._env),
                                    *(other._env)]))
        return Env(*items)
        
        
def build_dirs(pathes):

    ret = []
    def helper(p):
        if p.is_dir():
            ret.append(p)

    for p in pathes:
        do_file_rec(Path(p),helper)

    return ret


TRACE_REC = {}

def trace_rec(kind,name,envs,roots):

    if ret := TRACE_REC.get((kind,name,envs),None):
        return ret

    roots2 = adjust_path(kind,envs,roots)
    ret = find_path(kind,name,roots2)

    print(f"Start: {kind},{name},{envs} -> {ret}",file=OUTFH)
    TRACE_REC[(kind,name,envs)] = ret

    if ret:
        p,subk = ret
        for k,n,e in get_names(p,subk):
            envs2 = e.join(envs)
            q = trace_rec(k,n,envs2,roots)

    return ret

GET_NAMES = {}

def get_names(p,subk):

    if ret := GET_NAMES.get(p,None):
        for cmd,name,envs in ret:
            print(f"Rel: {p} -> {(cmd,name,envs)}",file=OUTFH)
        return ret

    if mod := LANG_HANDLER.get(subk):
        ret = mod.getName(p)
        ret = [ (cmd,name,Env(env)) for cmd,name,env in ret ]
    else:
        ret = []

    for cmd,name,envs in ret:
        print(f"Rel: {p} -> {(cmd,name,envs)}",file=OUTFH)
    
    GET_NAMES[p] = ret
    return ret
                

def adjust_path(k,es,roots):
    return roots

def find_path(kind,name,roots):

    def helper(p):
        if p.name == name:
            if handlers := FIND_HANDLER.get(kind,None):
                for mod in handlers:
                    if sub := mod.checkPath(p):
                        return (str(p),sub)
                return None
            else:
                return None
        else:
            return None

    for r in roots:
        if ret := do_file_rec1(Path(r),helper):
            return ret

    return None


FIND_HANDLER = {}
LANG_HANDLER = {}

def read_modules(dir,find_handlers,lang_handlers):

    p = Path(dir)
    base = p.name 
    
    for c in p.iterdir():
        if c.suffix != ".py": continue
        name = c.stem
        print(f"name = {name}")
        mod = importlib.import_module(base + "." + name)
        register_multi(find_handlers,mod.getType(),mod)
        lang_handlers[mod.getLang()] = mod

def register_multi(dict,k,v):

    if e := dict.get(k,None):
        pass
    else:
        e = []
        dict[k] = e

    e.append(v)

    
def main():

    global OUTFH

    parser = argparse.ArgumentParser()
    parser.add_argument("--src","-s",action="append")
    parser.add_argument("--start_list","-l")
    parser.add_argument("--debug",action="store_true")
    parser.add_argument("--out","-o")
    parser.add_argument("--parsers")
    args = parser.parse_args()

    srcs = args.src
    start_list = args.start_list

    if args.out:
        OUTFH = open(args.out,"w")
    else:
        OUTFh = sys.stdout

    parsers = args.parsers
        
    if parsers:
        read_modules(parsers,FIND_HANDLER,LANG_HANDLER)

    if srcs:
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

