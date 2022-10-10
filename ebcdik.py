
import re

# table from 
# http://itdoc.hitachi.co.jp/manuals/3020/30203J3820/ISUS0268.HTM

ASCIIEBCDIK="""\
00 10 80 90 20 26 2D 6A 73 BF 77 79 7B 7D 24 30
01 11 81 91 A1 AA 2F 6B B1 C0 7E 7A 41 4A 9F 31
02 12 82 16 A2 AB 62 6C B2 C1 CD E0 42 4B 53 32
03 13 83 93 A3 AC 63 6D B3 C2 CE E1 43 4C 54 33
9C 9D 84 94 A4 AD 64 6E B4 C3 CF E2 44 4D 55 34
09 0A 85 95 A5 AE 65 6F B5 C4 D0 E3 45 4E 56 35
86 08 17 96 A6 AF 66 70 B6 C5 D1 E4 46 4F 57 36
7F 87 1B 04 A7 A0 67 71 B7 C6 D2 E5 47 50 58 37
97 18 88 98 A8 B0 68 72 B8 C7 D3 E6 48 51 59 38
8D 19 89 99 A9 61 69 60 B9 C8 D4 E7 49 52 5A 39
8E 92 8A 9A 5B 5D 7c 3A BA C9 D5 DA E8 EE F4 FA
0B 8F 8B 9B 2E 5C 2C 23 74 75 78 DB E9 EF F5 FB
0C 1C 8C 14 3C 2A 25 40 BB 76 D6 DC EA F0 F6 FC
0D 1D 05 15 28 29 5F 27 BC CA D7 DD EB F1 F7 FD
0E 1E 06 9E 2B 3B 3E 3D BD CB D8 DE EC f2 F8 FE
0F 1f 07 1A 21 5e 3F 22 BE CC D9 DF ED F3 F9 FF
"""

dupcheck = set()

tmptable     = []
ebcdik2ascii = []
mappingList  = []

rows = ASCIIEBCDIK.splitlines()
for i,r in enumerate(rows):
    row = re.split(r"\s",r)
    for j,c in enumerate(row):
        code = int(c,16)
        tmptable.append(code)

def charFromCode(x):
    try:
        chars = str(bytes((x,)),"cp932")
        if chars.isprintable():
            pass
        else:
            chars = " "
    except Exception as e:
        chars = " "
    return chars

def printTable(table):
    for i in range(0,16):
        for j in range(0,16):
            x = table[i*16 + j]
            print(f"{x:02X} ",end="")
        print("")            
        for j in range(0,16):
            x = table[i*16 + j]
            print(f" {charFromCode(x)} ",end="")
        print("")

def transposeTable(table):
    ret = []
    for i in range(0,16):
        for j in range(0,16):
            x = table[i + j*16]
            ret.append(x)
    return ret

def reverseTable(table):
    tuplelist = [(c,i) for i,c in enumerate(table)]
    tuplelist2 = sorted(tuplelist)
    return [ i for c,i in tuplelist2 ]


ebcdik2ascii = transposeTable(tmptable)
ascii2ebcdik = reverseTable(ebcdik2ascii)
asciitable   = [ c for c in range(0,256) ]

print("ASCII")
printTable(asciitable)

print("EBCDIK")
printTable(ebcdik2ascii)



      
