

import re

def main():

    NAME = r"(?P<NAME>[a-zA-Z]+)"
    NUM  = r"(?P<NUM>\d+)"

    pat = re.compile("|".join([NAME,NUM]))

    applyPat(pat,"123")
    applyPat(pat,"abc")
    
    scanner = pat.scanner("abc123")

    print(f"{type(scanner)}")
    
    while m := scanner.match():
        print(f"{m}")
        print(f"{m.lastgroup}")
        print(f"{m.group()}")

    print("finditer version")

    for m in pat.finditer("abc123"):
        print(f"{m}")
        print(f"{m.lastgroup}")
        print(f"{m.group()}")

    for m in pat.finditer("abc*123"):
        print(f"{m}")
        print(f"{m.lastgroup}")
        print(f"{m.group()}")

        

def applyPat(pat,str):
    if m := pat.search(str):
        print(f"{m}")
        print(f"{m.lastgroup}")
        print(f"{m.group()}")

if __name__ == "__main__":
    main()
