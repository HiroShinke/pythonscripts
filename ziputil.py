

import zipfile
from pathlib import Path
import diffutil
import re
import io
import os
import tempfile


def tree_to_zip(path,zip,arcRoot=None):

    if not arcRoot: arcRoot = path

    relpath = Path(path).relative_to(arcRoot)
    if path.is_file():
        zip.write(path,arcname=relpath)
    elif path.is_dir():
        if m := re.search(r"^(.+\.zip)$",
                          relpath.name,re.IGNORECASE):
            zipname = m.group(1)
            with tempfile.NamedTemporaryFile("w+b") as fh:
                with zipfile.ZipFile(fh,"w") as zip2:
                    for c in  path.iterdir():                
                        tree_to_zip(c,zip2,path)
                zip.write(fh.name,arcname=relpath)
        else:
            for c in  path.iterdir():
                tree_to_zip(c,zip,arcRoot)
    
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

def do_diff(fp,tp,diffproc=None):
    if fp.is_file() and tp.is_file():
        if re.search(r"\.zip$",str(fp)) and re.search(r"\.zip$",str(tp)):
            do_diffzip(fp,tp,diffproc)
        elif diffproc:
            diffproc(fp,tp)
        else:
            diffutil.print_diff(fp.open().read().splitlines(),
                                tp.open().read().splitlines())
    elif fp.is_dir() and tp.is_dir():
        do_diffdir(fp,tp,diffproc)
    else:
        print(f"uncomparable {f} and {t}")

def do_diffzip(fp,tp,diffproc=None):
    with fp.open("rb") as fh, tp.open("rb") as th:
        fx = io.BytesIO(fh.read())
        fzip = zipfile.ZipFile(fx)
        fzip.filename = str(fp)
        fr = zipfile.Path(fzip)
        tx = io.BytesIO(th.read())
        tzip = zipfile.ZipFile(tx)
        tzip.filename = str(tp)
        tr = zipfile.Path(tzip)
        do_diff(fr,tr,diffproc)
    
def do_diffdir(f,t,diffproc=None):

    seq1 = list( [ n1 for n1 in f.iterdir() ])
    seq2 = list( [ n2 for n2 in t.iterdir() ])

    def match_func(i,j):
        do_diff(seq1[i],seq2[j],diffproc)
                
    def discard_a(i):
        print(f'{seq1[i]} only in {seq1[i].parent}')        

    def discard_b(j):
        print(f'{seq2[j]} only in {seq2[j].parent}')        

    diffutil.traverse_sequences(seq1,seq2,
                                matchFunc=match_func,
                                discardAFunc=discard_a,
                                discardBFunc=discard_b,
                                keyFunc=lambda p: p.name)


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
        
def makeFile(path,contents=None):

    path   = Path(path)
    parent = path.parent
    parent.mkdir(parents=True,exist_ok=True)

    if not contents:
        contents = f"contents of file: {path}\n"
    
    with open(path,"w") as fh:
        fh.write(contents)


def test_make_zipfile():

    contents = """\
abcdef
abcdef
"""
    makeFile("tmp/_sample.zip/a.txt")
    makeFile("tmp/_sample.zip/b.txt")
    makeFile("tmp/_sample.zip/sample2.zip/e.txt")
    makeFile("tmp/_sample.zip/sample2.zip/sample3.zip/f.txt")
    makeFile("tmp/_sample.zip/xxx/c.txt")
    makeFile("tmp/_sample.zip/xxx/yyy/d.txt")

    makeFile("tmp/_sample4.zip/a.txt")
    makeFile("tmp/_sample4.zip/b.txt")
    makeFile("tmp/_sample4.zip/sample2.zip/e.txt")
    makeFile("tmp/_sample4.zip/sample2.zip/sample3.zip/f.txt",contents)
    makeFile("tmp/_sample4.zip/xxx/c.txt")
    makeFile("tmp/_sample4.zip/xxx/yyy/d.txt")

    zip = zipfile.ZipFile("tmp/sample.zip","w")
    tree_to_zip(Path("tmp/_sample.zip"),zip)

    zip = zipfile.ZipFile("tmp/sample4.zip","w")
    tree_to_zip(Path("tmp/_sample4.zip"),zip)


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

    
if __name__ == "__main__":
    main()

    
