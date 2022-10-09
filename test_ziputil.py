

from ziputil import *

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

    
