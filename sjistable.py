

import itertools

def make_chars():

    for c in range(0x8140,0xfff0):
        try:
            b = int.to_bytes(c,2,"big")
            t = str(b,"cp932")
            if t.isprintable():
                yield f"{c:04X}:1:{t}"
            else:
                yield f"{c:04X}:0:xx"
        except UnicodeDecodeError as e:
            yield f"{c:04X}:0:xx"
    
def main():


    chars = make_chars()
    while m := itertools.islice(chars,8):
        l = list(m)
        if l:
            print(" ".join(l))
        else:
            break
    
            
if __name__ == "__main__":
    main()
    
