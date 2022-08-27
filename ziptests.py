

import zipfile
from pathlib import Path
import re
import io

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

    def print_helper(path):
        if path.is_file() and re.search(r"\.txt$",str(path)):
            print(f"path = {str(path)}")
            with path.open("r") as fh:
                for l in fh:
                    print(l,end="")

    print("!!!!! 1 !!!!!")
    root = zipfile.Path("tmp/sample.zip")
    do_rec_zipfile(root,print_helper)
    print("!!!!! 2 !!!!!")
    do_rec_zipfile(Path("tmp/sample.zip"),print_helper)
    
def test_make_zipfile():

    contents = """\
abcdef
abcdef
"""
    makeFile("tmp/a.txt")
    makeFile("tmp/b.txt")
    makeFile("tmp/xxx/c.txt")
    makeFile("tmp/xxx/yyy/d.txt")
    makeFile("tmp/e.txt")    
    makeFile("tmp/f.txt")

    def zipwrite(zip,path):
        relpath = Path(path).relative_to("tmp")
        zip.write(path,arcname=relpath)
    
    with zipfile.ZipFile("tmp/sample3.zip","w") as zip:
        zipwrite(zip,"tmp/f.txt")
    
    with zipfile.ZipFile("tmp/sample2.zip","w") as zip:
        zipwrite(zip,"tmp/e.txt")
        zipwrite(zip,"tmp/sample3.zip")
        
    with zipfile.ZipFile("tmp/sample.zip","w") as zip:
        zipwrite(zip,"tmp/a.txt")
        zipwrite(zip,"tmp/b.txt")
        zipwrite(zip,"tmp/xxx/c.txt")
        zipwrite(zip,"tmp/xxx/yyy/d.txt")
        zipwrite(zip,"tmp/sample2.zip")

        
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
            
if __name__ == "__main__":
    main()

    
