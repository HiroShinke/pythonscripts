

from parsecp import *
import sys
import re

def tr(reg): return token(pR(reg))
def ts(str): return token(pS(str))

def createParser():

    pExpr = None
                
    def addopObj(t):
        if   t.word == "+": return (lambda n,m: n+m)
        elif t.word == "-": return (lambda n,m: n-m)
        else: return None

    pAddop = a( o( tr(r"\+"), tr(r"-") ), addopObj )

    def mulopObj(t):
        if   t.word == "*": return (lambda n,m: n*m)
        elif t.word == "/": return (lambda n,m: n/m)
        else: return None

    pMulop = a( o( tr(r"\*"), tr(r"\/") ), mulopObj )
        
    pDigit = a( tr(r"\d+"), lambda t: int(t.word) )
    pFactor = o( pDigit,
                 para( ts("("), pRef(lambda : pExpr), ts(")") ) )
    pTerm   = c( pFactor, pMulop )
    pExpr   = c( pTerm,   pAddop )

    return pExpr

def mainLoop():
    pExpr = createParser()
    buff = ""
    while True:
        str = sys.stdin.readline()
        buff = buff + str
        m = re.search(r";",buff)
        if m:
            pos = m.start(0)
            print( runParser(pExpr,buff[0:pos]) )
            buff = ""

mainLoop()



    
