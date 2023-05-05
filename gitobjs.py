

import hashlib
import argparse
import zlib
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--infile")
    parser.add_argument("--type")
    parser.add_argument("--unzip",action="store_true")
    parser.add_argument("--cat",action="store_true")
    parser.add_argument("--digest",action="store_true")    
    args = parser.parse_args()

    m=hashlib.sha1()
    with open(args.infile,"rb") as fh:
        contents = fh.read()
        typeb = bytes(args.type,"iso-8859-1")
        m.update(typeb)
        m.update(b" ")
        if args.unzip:
            contents = zlib.decompress(contents)
        s = f"{len(contents)}"
        m.update(bytes(s,"iso-8859-1"))
        m.update(b"\x00")
        m.update(contents)

    if args.digest:
        print("digest=",m.hexdigest())
    if args.cat:
        sys.stdout.buffer.write(contents)
        
if __name__ == "__main__":
    main()
