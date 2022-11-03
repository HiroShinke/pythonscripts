
import itertools

def make_chars():

    for c in range(0x81,0x100):
        r = range(0x40,0x100)
        for d in r:
            try:
                i = (c << 8 ) | d
                b = int.to_bytes(i,2,"big")
                t = str(b,"cp932")
                yield (i,t)
            except UnicodeDecodeError as e:
                yield (i,"??")
    
def main():

    try:
        chars = make_chars()
        while m := itertools.islice(chars,16):
            l = list(m)
            if l:
                code  = l[0][0]
                strs = [ f"{s:<3}" for c,s in l ]
                print(f"{code:04X}: ", " ".join(strs))
            else:
                break
    except BrokenPipeError:
        return
        
            
if __name__ == "__main__":
    main()
    
