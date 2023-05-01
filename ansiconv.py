


c_cc = None
done  = False
prepare_ff = False
reclen = None

"""
(None) -> 0c/FF      -> (0d)
       -> 0a/-       -> (0a)
       -> 0d/-       -> (0d)
       -> */error

(0d)   -> 0c/OUTPUT  -> (0d) + PFF
       -> 0a/OUTPUT  -> (0a)
       -> 0d/OUTPUT  -> (0d)

(0a)   -> 0c/OUTPUT  -> (0d) + PFF
       -> 0a/OUTPUT  -> (0a)
       -> 0d/OUTPUT  -> (0d)

(0d) + PFF -> -/FF   -> (0d)


"""

def initialize(len_):
    global c_cc
    global done
    global reclen
    c_cc = None
    done = False
    reclen = len_

def make_record(buff):
    ba = bytearray()
    if c_cc == 0x0a:
        ba.append(ord(" "))
    elif c_cc == 0x0d:
        ba.append(ord("+"))
    else:
        raise ValueError(f"c_cc = {c_cc:02x}")
    ba.extend(buff)
    ba.extend(b" "*(reclen -len(buff)))
    return bytes(ba)

def get_record(fh):

    global done
    global c_cc
    global prepare_ff

    buff = b""

    if done:
        return None

    if prepare_ff:
        prepare_ff = False
        assert c_cc == 0x0d
        return b"1" + b" "*reclen

    while b := fh.read(1):
        c = b[0]
        if c_cc is None:
            if c == 0x0c:
                c_cc = 0x0d
                return b"1" + b" "*reclen
            elif c == 0x0a or c == 0x0d:
                c_cc = c
            else:
                raise ValueError(f"c_cc={c_cc},c={c}")
        elif c_cc == 0x0a or c_cc == 0x0d:
            if c == 0x0c:
                ret = make_record(buff)
                c_cc = 0x0d
                prepare_ff = True
                return ret
            elif c == 0x0a or c == 0x0d:
                ret = make_record(buff)                
                c_cc = c
                return ret                
            else:
                buff += bytes([c])

    done = True
    if c_cc:
        return  make_record(buff)
    else:
        return None
    
