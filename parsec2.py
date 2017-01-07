

import re

SUCCESS = True
FAILED  = False

def pChar(c):
    def parse(s,i):
        if i < len(s) and s[i] == c:
            return (SUCCESS,i+1,s[i])
        else:
            return (FAILED,i)
    return parse
    
def regexpP(pat):
    prog = re.compile("^" + pat)
    def parse(s,i):
        if i < len(s):
            pass
        else:
            return (FAILED,i)
        m = prog.match(s[i:])
        if m:
            s = m.group(0)
            return (SUCCESS,i + len(s),s)
        else:
            return (FAILED,i)
    return parse

def pDo(*ps):

    def parse(s,i):
        ret = []
        for p in ps:
            success,i,*w = p(s,i)
            if success:
                ret.append(*w)
            else:
                pass
        return (SUCCESS,i,ret)
    return parse
            
def pOr(*ps):

    def parse(s,i):
        ret = []
        for p in ps:
            success,i0,*w = p(s,i)
            if success:
                return (SUCCESS,i0,*w)
        return (FAILED,i)
    return parse

def pChain(p,op,evalFunc):

    def parse(s,i):
        values = []
        ops    = []
        success,i,*w = p(s,i)
        if success:
            values.append(*w)
            while True:
                success,i,*w = op(s,i)
                if success:
                    success,i,*w1 = p(s,i)
                    if success:
                        ops.append(w[0])
                        values.append(*w1)
                    else:
                        return [FAILED,i]
                else:
                    break
            return [SUCCESS,i,evalFunc(values,ops)]
        else:
            return [FAILED,i]
    return parse

def actionP(p,func):

    def parse(s,i):
        success,i,*w = p(s,i)
        if success:
            return [SUCCESS,i,func(*w)]
        else:
            return [FAILED,i]
    return parse

    
def pCr1(p,op):

    def evalStack(values,ops):
        vs = values.copy()
        os = ops.copy()
        while len(os) > 0:
            v2 = vs.pop()
            v1 = vs.pop()
            o = os.pop()
            v = o(v1,v2)
            vs.append(v)
        return vs[0]

    return pChain(p,op,evalStack)
    
def pCl1(p,op):    

    def evalStack(values,ops):
        vs = values.copy()
        os = ops.copy()
        vs.reverse()
        os.reverse()
        while len(os) > 0:
            v1 = vs.pop()
            v2 = vs.pop()
            o = os.pop()
            v = o(v1,v2)
            vs.append(v)
        return vs[0]

    return pChain(p,op,evalStack)

# def token(p):

def digit():
    return actionP(regexpP("\d+"), lambda s: int(s))


p = pDo(pChar("a"),pChar("b"),pChar("c"))
print( p("abcde",0) )

p = pCl1(digit(),
         actionP(pChar("+"), lambda _: (lambda n,m: n+m)))

print( p("1+2",0) )
