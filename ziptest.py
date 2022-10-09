

import zipfile
from pathlib import Path
import difflib
import re
import io
import os
import tempfile

def main():

    zip = zipfile.ZipFile("sample.zip","w",
                          compression=zipfile.ZIP_DEFLATED)

    with zip.open("xxx/a.txt","w") as fh:
        fh.write(b"xxxxxxxx\n")
        fh.write(b"xxxxxxxx\n")

    with zip.open("xxx/yyy/a.txt","w") as fh:
        fh.write(b"xxxxxxxx\n")
        fh.write(b"xxxxxxxx\n")


    
if __name__ == "__main__":
    main()

    
