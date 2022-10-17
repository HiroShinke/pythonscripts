

import sys

MULTILINE_TEXT = """\
abcde
efghi
jklmn
"""

for l in MULTILINE_TEXT.splitlines():
    print(l)
    
with open("tokenizer.py","r") as fh:
    for l in fh.readlines():
        sys.stdout.write(l)
        
    
