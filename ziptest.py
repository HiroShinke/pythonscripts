

import zipfile
from pathlib import Path
import difflib
import re
import io
import os
import tempfile

def main():

    with zipfile.ZipFile("sample1.zip","w",
                         compression=zipfile.ZIP_DEFLATED) as zip:

        with zip.open("xxx/a.txt","w") as fh:
            fh.write(b"xxxxxxxx\n")
            fh.write(b"xxxxxxxx\n")
            fh.write(b"xxxxxxxx\n")
            
        with zip.open("xxx/yyy/a.txt","w") as fh:
            fh.write(b"xxxxxxxx\n")
            fh.write(b"xxxxxxxx\n")
            fh.write(b"xxxxxxxx\n")

    with zipfile.ZipFile("sample2.zip","w",
                         compression=zipfile.ZIP_DEFLATED) as zip:

        with zip.open("xxx/a.txt","w") as fh:
            fh.write(b"xxxxxxxx\n")
            fh.write(b"yyyyyyyy\n")
            fh.write(b"xxxxxxxx\n")
            
        with zip.open("xxx/yyy/a.txt","w") as fh:
            fh.write(b"xxxxxxxx\n")
            fh.write(b"xxxxxxxx\n")
            fh.write(b"xxxxxxxx\n")


    with zipfile.ZipFile("sample3.zip","w",
                         compression=zipfile.ZIP_DEFLATED) as zip:

        with zip.open("xxx/a.txt","w") as fh:
            fh.write(b"xxxxxxxx\n")
            fh.write(b"xxxxxxxx\n")
            fh.write(b"xxxxxxxx\n")
            
        with zip.open("xxx/yyy/a.txt","w") as fh:
            fh.write(b"xxxxxxxx\n")
            fh.write(b"xxxxxxxx\n")
            fh.write(b"xxxxxxxx\n")

        zip.write("sample1.zip","xxx/sample.zip")

    with zipfile.ZipFile("sample4.zip","w",
                         compression=zipfile.ZIP_DEFLATED) as zip:

        with zip.open("xxx/a.txt","w") as fh:
            fh.write(b"xxxxxxxx\n")
            fh.write(b"xxxxxxxx\n")
            fh.write(b"xxxxxxxx\n")
            
        with zip.open("xxx/yyy/a.txt","w") as fh:
            fh.write(b"xxxxxxxx\n")
            fh.write(b"xxxxxxxx\n")
            fh.write(b"xxxxxxxx\n")

        zip.write("sample2.zip","xxx/sample.zip")

            
    
if __name__ == "__main__":
    main()

    
