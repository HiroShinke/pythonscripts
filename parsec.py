

import re

SUCCESS = True
FAILED  = False

class Parser:
    pass

class CharP(Parser):

    def __init__(self,c):
        self.c = c

    def parse(self,s,i):
        if i < len(s) and s[i] == self.c:
            return (SUCCESS,i+1,s[i])
        else:
            return (FAILED,i)

class RegExpP(Parser):

    def __init__(self,pat):
        self.prog = re.compile("^" + pat)

    def parse(self,s,i):
        if i < len(s):
            pass
        else:
            return (FAILED,i)
        
        m = self.prog.match(s[i:])
        if m:
            s = m.group(0)
            return (SUCCESS,i + len(s),s)
        else:
            return (FAILED,i)
        
class SeqP(Parser):

    def __init__(self,*ps):
        self.ps = ps

    def parse(self,s,i):
        ret = []
        for p in self.ps:
            success,i,*w = p.parse(s,i)
            if success:
                ret.append(*w)
            else:
                pass
        return (SUCCESS,i,ret)
            
class OrP(Parser):

    def __iniit__(self,*ps):
        self.ps = ps

    def parse(self,s,i):
        ret = []
        for p in self.ps:
            success,i0,*w = p.parse(s,i)
            if success:
                return (SUCCESS,i0,*w)
        return (FAILED,i)


class ChainP(Parser):

    def __init__(self,p,op):
        self.p = p
        self.op = op

    def parse(self,s,i):
        values = []
        ops    = []
        success,i,*w = self.p.parse(s,i)
        if success:
            values.append(*w)
            while True:
                success,i,*w = self.op.parse(s,i)
                if success:
                    success,i,*w1 = self.p.parse(s,i)
                    if success:
                        ops.append(w[0])
                        values.append(*w1)
                    else:
                        print(s[i])
                        print("here1\n")
                        return [FAILED,i]
                else:
                    break
            return [SUCCESS,i,self.evalStack(values,ops)]
        else:
            print("here2\n")
            return [FAILED,i]

class ActionP(Parser):

    def __init__(self,p,func):
        self.p    = p
        self.func = func

    def parse(self,s,i):
        success,i,*w = self.p.parse(s,i)
        if success:
            return [SUCCESS,i,self.func(*w)]
        else:
            return [FAILED,i]


class ChainRP(ChainP):

    def evalStack(self,values,ops):
        vs = values.copy()
        os = ops.copy()
        while len(os) > 0:
            v2 = vs.pop()
            v1 = vs.pop()
            o = os.pop()
            v = o(v1,v2)
            vs.append(v)
        return vs[0]

class ChainLP(ChainP):

    def evalStack(self,values,ops):
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


def digit():
    return ActionP(RegExpP("\d+"), lambda s: int(s))


p = SeqP(CharP("a"),CharP("b"),CharP("c"))
print( p.parse("abcde",0) )

p = ChainLP(digit(),
            ActionP(CharP("+"), lambda _: (lambda n,m: n+m)))

print( p.parse("1+2",0) )
