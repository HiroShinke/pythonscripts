

import hashlib
import argparse
import zlib
import sys
import os
import re
from pathlib import Path


def pretty_bytes_tree(contents):

    pos = 0
    ba = bytearray()
    
    while pos < len(contents):
        pos1 = contents.index(b"\x00",pos)
        txt = contents[pos:pos1]
        if not txt.startswith(b"tree "):
            digs = "".join([f"{b:02x}" for b in contents[pos1+1:pos1+21]])
            pos = pos1 + 21
            ba += txt
            ba += bytes(digs,"iso-8859-1")
        else:
            pos = pos1+1
            ba += txt
        ba += b"\n"

    return bytes(ba)

def complete_path(infile):
    path = Path(infile)
    dir_ = Path(path.parent)
    base = path.name
    print(dir_)
    for p in dir_.iterdir():
        if p.name.startswith(base):
            return str(p)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--infile")
    parser.add_argument("--type")
    parser.add_argument("--unzip",action="store_true")
    parser.add_argument("--cat",action="store_true")
    parser.add_argument("--pretty",action="store_true")
    parser.add_argument("--digest",action="store_true")    
    args = parser.parse_args()

    if os.path.exists(args.infile):
        infile = args.infile
    elif m := re.search(r"^([0-9a-fA-F]{2})([0-9a-fA-F]+)$",args.infile):
        pre,base = m.groups()
        infile = f".git/objects/{pre}/{base}"
        path = Path(infile)
        if path.is_file():
            pass
        else:
            infile = complete_path(infile)
        
    m=hashlib.sha1()
    with open(infile,"rb") as fh:
        contents = fh.read()
        if args.unzip:
            contents = zlib.decompress(contents)
        if args.type == "blob":
            typeb = bytes(args.type,"iso-8859-1")
            m.update(typeb)
            m.update(b" ")
            s = f"{len(contents)}"
            m.update(bytes(s,"iso-8859-1"))
            m.update(b"\x00")
        m.update(contents)

    if args.digest:
        print("digest=",m.hexdigest())
    if args.cat:
        if args.pretty and args.type == "tree":
            sys.stdout.buffer.write(pretty_bytes_tree(contents))
        else:
            sys.stdout.buffer.write(contents)

if __name__ == "__main__":
    main()
