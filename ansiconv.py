


lf_count = 0
done  = False
prepare_ff = False
reclen = None

"""

0  -> 0c/FF   -> 0
   -> 0a/-    -> 1
   -> 0d/-    -> 0
   -> X/-     -> 0+X
   -> eof/-   -> Z

0+X-> 0c/OUTPUT(0),FF -> 0
   -> 0a/OUTPUT(0)    -> 1
   -> 0d/OUTPUT(0)    -> 0
   -> X/-             -> 0+X
   -> eof/OUTPUT(0)   -> Z

1  -> 0c/OUTPUT(1),FF -> 0
   -> 0a/-            -> 2
   -> 0d/-            -> 1
   -> X/-             -> 1+X

1+X-> 0c/OUTPUT(1),FF -> 0
   -> 0a/OUTPUT(1)    -> 1
   -> 0d/OUTPUT(1)    -> 0
   -> X/-             -> 1+X

2  -> 0c/OUTPUT(2),FF -> 0
   -> 0a/-            -> 3
   -> 0d/-            -> 2
   -> X/-             -> 2+X

2+X-> 0c/OUTPUT(2),FF -> 0
   -> 0a/OUTPUT(2)    -> 1
   -> 0d/OUTPUT(2)    -> 0
   -> X/-             -> 2+X

3  -> 0c/OUTPUT(3),FF -> 0
   -> 0a/OUTPUT(3)    -> 1
   -> 0d/-            -> 3
   -> X/-             -> 3+X

3+X-> 0c/OUTPUT(3),FF -> 0
   -> 0a/OUTPUT(3)    -> 1
   -> 0d/OUTPUT(3)    -> 0
   -> X/-             -> 3+X

"""

def initialize(len_):
    global lf_count
    global done
    global reclen
    global prepare_ff

    lf_count = 0
    done = False
    prepare_ff = False
    reclen = len_

def make_record(buff):

    global lf_count
    
    if lf_count == 0 and not buff:
        return None

    ba = bytearray()

    if lf_count == 0:
        ba.append(ord("+"))
    elif lf_count == 1:
        ba.append(ord(" "))
    elif lf_count == 2:
        ba.append(ord("0"))
    elif lf_count == 3:
        ba.append(ord("-"))

    lf_count = 0

    ba.extend(buff)
    ba.extend(b" "*(reclen -len(ba)))
    return bytes(ba)

def get_record(fh):

    global done
    global prepare_ff
    global lf_count
    
    buff = b""

    if done:
        return None

    if prepare_ff:
        prepare_ff = False
        return b"1" + b" "*(reclen-1)

    while b := fh.read(1):
        c = b[0]
        
        if c == 0x0c:
            if ret := make_record(buff):
                prepare_ff = True
                return ret
            else:
                return b"1" + b" "*(reclen-1)
        elif c == 0x0a:
            if lf_count == 3 or buff:
                ret = make_record(buff)
                lf_count += 1
                return ret
            else:
                lf_count += 1
        elif c == 0x0d:
            if buff:
                ret =  make_record(buff)
                return ret
            else:
                pass
        else:
            buff += bytes([c])

    done = True
    if ret := make_record(buff):
        return  ret
    else:
        return None
    
