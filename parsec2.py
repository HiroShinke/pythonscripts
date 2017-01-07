

import re

SUCCESS = True
FAILED  = False

class ParserState:

    def __init__(self,str,pos=0,lineno=0,column=0):
        self.str = str
        self.pos = pos
        self.lineno = lineno
        self.column = column

    def __eq__(self,o):
        return self.pos == o.pos

    def __getitem__(self,key):
        return self.str[key]

    def curstr(self):
        return self[self.pos:]

    def forwardPos(self,p):
        str = self.curstr()[0:p]
        nc  = str.count("\n")
        ln  = str.split("\n",-1)
        return ParserState(self.str,
                           self.pos + p,
                           self.lineno + nc,
                           self.column + p if nc == 0 else len(ln[-1]))
    def isEos(self):
        return not (self.pos < len(self.str) )

class Token:

    def __init__(self,word,pos,lineno,column):
        self.word = word
        self.pos = pos
        self.lineno = lineno
        self.column = column


def runParser(p,str):
    return p(ParserState(str))

        
def pChar(pred):
    def parse(s):
        if s.isEos:
            w = pred(s)
            if w:
                return (SUCCESS,
                        s.forwardPos(len(w)),
                        Token(w,
                              s.pos,
                              s.lineno,
                              s.column))
            else:
                return (FAILED,s)
    return parse

def pNotChar(pred):
    def parse(s):
        if s.isEos:
            w = pred(s)
            if w == None:
                return (SUCCESS,
                        s.forwardPos(1),
                        Token(s.curstr()[0],
                              s.pos,
                              s.lineno,
                              s.column))
            else:
                return (FAILED,s)
    return parse

def predString(str):
    def pred(s):
        cur = s.curstr()
        if cur[0:len(str)] == str:
            return str
        else:
            return None
    return pred

def predRegexp(pat):
    prog = re.compile("^" + pat)
    def pred(s):
        m = prog.match(s.curstr())
        if m:
            str = m.group(0)
            return str
        else:
            return None
    return pred

def pS(str):
    return pChar( predString(str) )

def pR(str):
    return pChar( predRegexp(str) )

def pNS(str):
    return pNotChar( predString(str) )
  
def pNR(regexp):
    return pNotChar( predRegexp(regexp) )
  
def pAny():
    return pChar( lambda s: s.curstr[0] )

def pEof():
    return pNotFollowdBy(pAny)

def token(p):
    return pU( pDo( pK( pR("\s*") ), p ))

def pDo(*ps):
    def parse(s):
        ret = []
        for p in ps:
            print(s.curstr())
            success,s,*w = p(s)
            print(*w)
            if success:
                ret.append(*w)
            else:
                return (FAILED,s)
        return (SUCCESS,s,*ret)
    return parse

def pChain(p,op,evalFunc):

    def parse(s):
        values = []
        ops    = []
        success,s,*w = p(s)
        if success:
            values.append(*w)
            while True:
                success,s,*w = op(s)
                if success:
                    success,s,*w1 = p(s)
                    if success:
                        ops.append(w[0])
                        values.append(*w1)
                    else:
                        return (FAILED,s)
                else:
                    break
            return (SUCCESS,
                    s,
                    evalFunc(values,ops))
        else:
            return (FAILED,s)
    return parse

def pAction(p,func):

    def parse(s):
        success,s,*w = p(s)
        if success:
            return (SUCCESS,s,func(*w))
        else:
            return (FAILED,s)
    return parse


def pDebug(label,p):
    def parse(s):
      success,s0,*w = p(s)
      if success:
        print("label=" + label + " SUCCESS")
        return (SUCCESS,s0,*w)
      else:
        print("label=" + label + " FAILED")
        return (FAILED,s0)
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

# P is for paren
def pP(po,p,pc):
    return pD( pK(po), p, pK(pc) )

# pOpt
def pOpt(p):
    def parse(s):
      success,s0,*w = p(s)
      if success:
          return (SUCCESS,s0,*w)
      else:
          if s0 == s:
              return (SUCCESS,s)
          else:
              # print "failed at #{s0}"
              return (FAILED,s0)
    return parse

# notFollowedBy
def pNotFolloedBy(p):
    def parse(s):
        success,_ = p(s)
        if not success:
            return (SUCCESS,s)
        else:
            return (FAILED,s)
            
# lookAhead
def pLookAhead(p):
    def parse(s):
        success,s0,_ = p(s)
        if success:
            return (SUCCESS,s)
        else:
            if s0 != s:
                # print "failed at #{s0}"
                return (FAILED,s0)
            else:
                return (FAILED,s)
    return parse

# O is for Or
# the choice combinator
def pO(*ps):
    def parse(s):
        ret = []
        for p in ps:
            success,s0,*w = p(s)
            if success:
                return (SUCCESS,s0,*w)
            elif s0 != s:
                return (FAILED,s0)
        return (FAILED,s)
    return parse


# U is for Undo
# the try combinator
def pU(p):
    def parse(s):
        success,s0,*w = p(s)
        if success:
            return (SUCCESS,s0,*w)
        else:
            return (FAILED,s)
    return parse


def word(str):
    return pDebug(str,pAction(pS(str), lambda s: s.word))

def digit():
    return pAction(pR("\d+"), lambda s: int(s.word))

p = pDo(word("a"),word("b"),word("c"))
print( runParser(p,"abcde") )

p = pCl1(digit(),
         pAction(pS("+"), lambda _: (lambda n,m: n+m)))

print( runParser(p,"1+2") )

print( runParser(digit(),"12") )
