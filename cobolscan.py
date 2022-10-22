

from dataclasses import dataclass
import re
import argparse

@dataclass
class Token:
    type: str
    value: str
    line: int
    column: int

def linesFromText(sourceText):

    lines = sourceText.splitlines()
    lines1 = enumerate(lines)

    def splitArea(l):
        return (l[0:6],
                l[6],
                l[7:72],
                l[72:])

    lines2 = [ (i,*splitArea(l)) for (i,l) in lines1
               if re.search(f"^.{6}[^*]",l) ]

    def srcLines(lines):
        acc = ""
        idx = 0
        for i,ser,a,b,com in lines:
            if a == "-":
                acc += b
            elif acc:
                yield (idx,acc)
                acc = b
                idx = i
            else:
                acc = b
                idx = i
        if acc:
            yield (idx,acc)

    yield from srcLines(lines2)
    

def parse(path):
    fh = open(path)
    contents = fh.read()
    for i,l in linesFromText(contents):
        print(f"{l}")
        for k,v in tokenize(l):
            if k != "SKIP":
                print(f"{k,v}")
            

def tokenize(l):
    token_specification = [
        ('NUMBER',   r'\d+(\.\d+)?'),
        ('SEPARATOR',    r'[=\+\-*/\(\)\.,:<>]'),
        ('SEPARATOR2',    r'\.,;(=?\s)'),
        ('LITERAL',    r'"[^"]*"'),
        ('LITERAL2',   r"'[^']*'"),        
        ('ID',       r'[\w-]+'),  
        ('NEWLINE',  r'\n'),         
        ('SKIP',     r'\s+'),     
        ('MISMATCH', r'.'),          
    ]
    tok_regex = '|'.join(f'(?P<{p}>{pat})' for p,pat in token_specification)
    regexp = re.compile(tok_regex)
    for m in regexp.finditer(l):
        kind  = m.lastgroup
        value = m.group()
        yield kind,value

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", "-s", type=str, action="store")
    args = parser.parse_args()
    parse(args.src)


if __name__ == "__main__":
    main()

    

        
