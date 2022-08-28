

import zipfile
from pathlib import Path
import difflib
import re
import io
import os
import tempfile

class DifferPair:
    def __init__(self,k,o):
        self.k = k
        self.o = o
    def __repr__(self):
        return f'({self.k}, {self.o})'
    def __hash__(self):
        return hash(self.k)
    def __eq__(self,other):
        return (
            self.__class__ == other.__class__ and
            self.k == other.k
            )

def makeFile(path,contents=None):

    path   = Path(path)
    parent = path.parent
    parent.mkdir(parents=True,exist_ok=True)

    if not contents:
        contents = f"contents of file: {path}\n"
    
    with open(path,"w") as fh:
        fh.write(contents)

def main():

    test_make_zipfile()

    def print_name(path):
        print(str(path))
    
    def print_helper(path):
        print(str(path))
        if path.is_file() and re.search(r"\.txt$",str(path)):
            with path.open("r") as fh:
                for l in fh:
                    print(l,end="")

    root = zipfile.Path("tmp/sample.zip")
    print("print_name")
    do_rec_zipfile(root,print_name)
    print("print_helper")
    do_rec_zipfile(root,print_helper)    
    print("do_diff")
    do_diff(zipfile.Path("tmp/sample.zip"),
            zipfile.Path("tmp/sample4.zip"))
        
def test_make_zipfile():

    contents = """\
abcdef
abcdef
"""
    makeFile("tmp/_sample.zip/a.txt")
    makeFile("tmp/_sample.zip/b.txt")
    makeFile("tmp/_sample.zip/_sample2.zip/e.txt")
    makeFile("tmp/_sample.zip/_sample2.zip/_sample3.zip/f.txt")
    makeFile("tmp/_sample.zip/xxx/c.txt")
    makeFile("tmp/_sample.zip/xxx/yyy/d.txt")

    makeFile("tmp/_sample4.zip/a.txt")
    makeFile("tmp/_sample4.zip/b.txt")
    makeFile("tmp/_sample4.zip/_sample2.zip/e.txt")
    makeFile("tmp/_sample4.zip/_sample2.zip/_sample3.zip/f.txt",contents)
    makeFile("tmp/_sample4.zip/xxx/c.txt")
    makeFile("tmp/_sample4.zip/xxx/yyy/d.txt")

    def zipwrite(zip,path):
        relpath = Path(path).relative_to("tmp")
        zip.write(path,arcname=relpath)

    def do_rec_make_zip(path,zip,arcRoot):
        relpath = Path(path).relative_to(arcRoot)
        if path.is_file():
            zip.write(path,arcname=relpath)
        elif path.is_dir():
            if m := re.search(r"^_(.+\.zip)$",relpath.name,re.IGNORECASE):
                zipname = m.group(1)
                with tempfile.NamedTemporaryFile("w+b") as fh:
                    # print(f"name = {fh.name}")
                    with zipfile.ZipFile(fh,"w") as zip2:
                        for c in  path.iterdir():                
                            do_rec_make_zip(c,zip2,str(path))
                    zip.write(str(fh.name),arcname=relpath)
            else:
                for c in  path.iterdir():
                    do_rec_make_zip(c,zip,arcRoot)

    zip = zipfile.ZipFile("tmp/sample.zip","w")
    do_rec_make_zip(Path("tmp/_sample.zip"),zip,"tmp/_sample.zip")

    zip = zipfile.ZipFile("tmp/sample4.zip","w")
    do_rec_make_zip(Path("tmp/_sample4.zip"),zip,"tmp/_sample4.zip")

        
def test_print_filelist():
    with zipfile.ZipFile("tmp/sample.zip") as zip:
        for n in zip.namelist():
            print(f"{zip.filename} : {n}")


def test_print_contents():
    with zipfile.ZipFile("tmp/sample.zip") as zip:
        for n in zip.namelist():
            with zip.open(n) as f:
                if re.search(r"\.txt$",n):
                    print(f"---{n}---")
                    for l in f:
                        print(str(l,"cp932"),end="")

def test_print_with_path():
    root = zipfile.Path("tmp/sample.zip")
    for fn in root.iterdir():
        if fn.is_file() and re.search(r"\.txt$",fn.name):
            with fn.open("r") as fh:
                print(f"---{fn}---")
                for l in fh:
                    print(l,end="")

    
def do_rec_file(path,proc,*args,**kwargs):
    proc(path,*args,**kwargs)
    if path.is_dir():
        for c in  path.iterdir():
            do_rec_file(c,proc,*args,**kwargs)
            
def do_rec_zipfile(path,proc,*args,**kwargs):
    proc(path,*args,**kwargs)
    if path.is_dir():
        for c in  path.iterdir():
            do_rec_zipfile(c,proc,*args,**kwargs)
    elif re.search(r"\.zip$",str(path)):
        with path.open("rb") as fh:
            contents = fh.read()
            xx = io.BytesIO(contents)
            zip = zipfile.ZipFile(xx)
            zip.filename = str(path)
            root = zipfile.Path(zip)
            do_rec_zipfile(root,proc,*args,**kwargs)

def do_diff(fp,tp):
    if fp.is_file() and tp.is_file():
        if re.search(r"\.zip$",str(fp)) and re.search(r"\.zip$",str(tp)):
            do_diffzip(fp,tp)
        else:
            do_difffile(fp,tp)
    elif fp.is_dir() and tp.is_dir():
        do_diffdir(fp,tp)
    else:
        print(f"uncomparable {f} and {t}")

def do_diffzip(fp,tp):
    with fp.open("rb") as fh, tp.open("rb") as th:
        fx = io.BytesIO(fh.read())
        fzip = zipfile.ZipFile(fx)
        fzip.filename = str(fp)
        fr = zipfile.Path(fzip)
        tx = io.BytesIO(th.read())
        tzip = zipfile.ZipFile(tx)
        tzip.filename = str(tp)
        tr = zipfile.Path(tzip)
        do_diff(fr,tr)
    
def do_difffile(f,t):
    print(f"---{f}")
    print(f"+++{t}")
    ret = difflib.ndiff(list(f.open(mode='r')),
                        list(t.open(mode='r')),
                        charjunk=None)
    ret = [ l for l in ret if l[0] != '?']
    print(''.join(ret),end='')

def do_diffdir(f,t):
    seq1 = list( [ DifferPair(n1.name,n1) for n1 in f.iterdir() ])
    seq2 = list( [ DifferPair(n2.name,n2) for n2 in t.iterdir() ])

    matcher = difflib.SequenceMatcher(a = seq1,b = seq2)
    # print(seq1)
    # print(seq2)
    for tag,i1,i2,j1,j2 in matcher.get_opcodes():
        # print(f"{tag} a[{i1}:{i2}], b[{j1}:{j2}]")
        if tag == "equal":
            for f0,t0 in zip(seq1[i1:i2],seq2[j1:j2]):
                do_diff(f0.o,t0.o)
        else:
            for f0 in seq1[i1:i2]:
                print(f'{f0.o} only in {f0.o.parent}')
            for t0 in seq2[j1:j2]:
                print(f'{t0} only in {t0.o.parent}')
            
if __name__ == "__main__":
    main()

    
