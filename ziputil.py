

import zipfile
from pathlib import Path
import diffutil
import re
import io
import os
import tempfile


def tree_to_zip(path,zip,arcRoot=None):

    """copy a directory tree into a zip archive.
       Args:
           path: path to file to add
           if path is for a directory, all elements in the directory is added.
           At that time if path name is ended with .zip, 
           nested archive are created and added to the original zip archive.
           zip:  a zip archive to add files on
           arcRoot: path to directory root
           use to evaluate relative path for each file 
           in the archive 
       Returns:
           None
    """

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


def pathFromZipContents0(path):
    with zipfile.ZipFile(path) as zip:
        return zipfile.Path(zip)
                
def pathFromZipContents(path):
    with path.open("rb") as fh:
        contents = fh.read()
        xx = io.BytesIO(contents)
        zip = zipfile.ZipFile(xx)
        zip.filename = str(path)
        return zipfile.Path(zip)
                
def do_rec_zipfile(path,proc,*args,**kwargs):

    """recursive do something with every files in the archive.
       Args:
           path: path to the file to processing
           if path is for a directory (in the archive),
            all directory elements are processed recursivey
           if path is for a zip file, (nested in the archive),
           all archived items are processed recusively
           if path is for a ordinary file, proc is called with path
           proc:  the procedure to call for path
           Note proc is always called also for directories, and zip files.
           args: additional argument for proc
           kwargs additional keyword argument for proc
       Returns:
           None
    """

    proc(path,*args,**kwargs)
    if path.is_dir():
        for c in  path.iterdir():
            do_rec_zipfile(c,proc,*args,**kwargs)
    elif re.search(r"\.zip$",str(path)):
        root = pathFromZipContents(path)
        do_rec_zipfile(root,proc,*args,**kwargs)

        
def do_diff(fp,tp,diffproc=None):

    """diff to compare archives
       Args:
           fp: a path to compare
           if fp,tp are directories, 
           elements in each directory are to compare recursively.
           if fp,tp are archives, 
           items in each archives are to compare recursively.
           tp: another path to compare
           diffproc: proc to compre two single files
    """

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

    """diff to compare archives
       implementation of do_diff for the case of zip argument.
    """
    fr = pathFromZipContents(fp)
    tr = pathFromZipContents(tp)
    do_diff(fr,tr,diffproc)
    
def do_diffdir(f,t,diffproc=None):

    """diff to compare archives
       implementation of do_diff for the case of directory argument.
    """

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


if __name__ == "__main__":
    main()

    
