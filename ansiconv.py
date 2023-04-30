

import re
import sys
import argparse

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--reclen",type=int)
    parser.add_argument("--newline",action="store_true")
    args = parser.parse_args()

    stdin = sys.stdin.buffer
    stdout = sys.stdout.buffer

    reclen = args.reclen

    c_cc = None
    done  = False

    def make_record(c,buff):
        ba = bytearray()
        ba.append(c_cc)
        ba.extend(buff)
        ba.extend(b" "*(reclen -len(buff)))
        return bytes(ba)

    def get_record(fh):

        nonlocal done
        buff = b""

        while not done and (b := fh.read(1)):
            c = b[0]
            if c == 0x0a or c == 0x0c or c == 0x0d:
                if c_cc in not None:
                    ret = make_record(c_cc,buff)
                    c_cc = c
                    return ret
                else:
                    c_cc = c
            else:
                if c_cc is not None:
                    buff += [c]
                else:
                    raise ValueError()

        if not done:
            done = True
            if c_cc == 0x0a or c_cc == 0x0c:
                ret = make_record(c_cc,buff)
                return ret
            else:
                return None
        else:
            return None
                    
    while ret := get_record(stdin):
        stdout.write(ret)
        if args.newline:
            stdout.write(b"\n")
    
if __name__ == "__main__":
    main()
    
    
