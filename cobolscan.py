

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
        for k,v in tokensiter(l):
            if k != "SKIP":
                print(f"{k,v}")

def scanLiteral(l,pos):

    regex1 = re.compile(r"'[^']*'")
    regex2 = re.compile(r'"[^"]*"')
    
    if m := regex1.match(l,pos):
        value = m.group()
        start,end = m.span()
        return value,end
    elif m := regex2.match(l,pos):
        value = m.group()
        start,end = m.span()
        return value,end        
    else:
        raise ValueError(f"invalid source string {l}{pos}")

def tokensiter(l):

    token_specification = [
        ('NUMBER',     r'\d+(\.\d+)?'),
        ('SEPARATOR',  r'[=\+\-*/\(\)\.,:<>]'),
        ('SEPARATOR2', r'\.,;(=?\s)'),
        ('QUOTE',      '["\']'),
        # ('LITERAL',    r'"[^"]*"'),
        # ('LITERAL2',   r"'[^']*'"),        
        ('ID',         r'[\w-]+'),  
        ('NEWLINE',    r'\n'),         
        ('SKIP',       r'\s+'),     
        ('MISMATCH',   r'.'),          
    ]
    tok_regex = '|'.join(f'(?P<{p}>{pat})' for p,pat in token_specification)
    regexp = re.compile(tok_regex)

    pos = 0

    while pos < len(l):
        for m in regexp.finditer(l,pos):
            kind  = m.lastgroup
            value = m.group()
            start,end = m.span()
            if kind == "QUOTE":
                value,end = scanLiteral(l,start)
                pos = end
                yield "LITERAL",value
                break
            else:
                pos = end
                yield kind,value

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", "-s", type=str, action="store")
    args = parser.parse_args()
    parse(args.src)


if __name__ == "__main__":
    main()

    

        
