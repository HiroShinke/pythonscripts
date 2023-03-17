

import re
import abc
import types
from dataclasses import dataclass

SUCCESS = True
FAILED  = False

class Parser(abc.ABC):
    
    @abc.abstractmethod
    def parse(self,seq,i):
        pass

    
@dataclass
class Success:
    value : any
    pos   : int

@dataclass
class Failure:
    pos   : int


class Pred(Parser):
    def __init__(self,pred):
        self.pred = pred
    def parse(self,s,i):
        if i < len(s) and self.pred(s[i]):
            return Success(s[i],i+1)
        else:
            return Failure(i)

class Seq(Parser):

    def __init__(self,*parsers):
        self.parsers = list(parsers)

    def parse(self,s,i):
        ret = []
        for p in self.parsers:
            match p.parse(s,i):
                case Success(v,j):
                    ret.append(v)
                    i = j
                case _ as fail:
                    return fail
        return Success(ret,i)

class Or(Parser):

    def __init__(self,*parsers):
        self.parsers = list(parsers)
        
    def parse(self,s,i):
        maxi = i
        for p in self.parsers:
            match p.parse(s,i):
                case Success() as succ:
                    return succ
                case Failure(j):
                    if maxi < j:
                        maxi = j
        return Failure(maxi)

class TaggedOr(Parser):

    def __init__(self,*kwparsers):
        self.parsers = dict(kwparsers)
        
    def parse(self,s,i):
        maxi = i
        for k,p in self.parsers.items():
            match p.parse(s,i):
                case Success(v,j):
                    return Success([k,v],j)
                case Failure(j):
                    if maxi < j:
                        maxi = j
        return Failure(maxi)
    
    
class Action(Parser):

    def __init__(self,p,func):
        self.p    = p
        self.func = func

    def parse(self,s,i):
        match self.p.parse(s,i):
            case Success(v,j):
                return Success(self.func(v),j)
            case _ as fail:
                return fail

class Many(Parser):

    def __init__(self,p):
        self.p    = p

    def parse(self,s,i):
        ret = []
        while True:
            match self.p.parse(s,i):
                case Success(v,j):
                    ret.append(v)
                    i = j
                case _ as fail:
                    break
        return Success(ret,i)


class Opt(Parser):

    def __init__(self,p):
        self.p    = p

    def parse(self,s,i):
        match self.p.parse(s,i):
            case Success() as succ:
                return succ
            case _ as fail:
                return Success(None,i)

class Recursive(Parser):

    def __init__(self):
        self.p    = None

    def parse(self,s,i):
        return self.p.parse(s,i)

    def defined(self,q):
        self.p = q
        return self

        
class Empty(Parser):

    def __init__(self,c=None):
        self.c    = c

    def parse(self,s,i):
        return Success(self.c,i)


################################################################################
# special parser for string


class StrP(Parser):

    def __init__(self,str):
        self.str = str

    def parse(self,s,i):
        pos = i+len(self.str)
        if s[i:i+len(self.str)] == self.str:
            return Success(self.str,pos)
        else:
            return Failure(i)

class RegexpP(Parser):

    def __init__(self,str,group=0,**kwargs):
        self.re = re.compile(str,**kwargs)
        self.group = group

    def parse(self,s,i):
        if m := self.re.match(s,i):
            str = m.group(self.group)
            start,end = m.span(self.group)
            return Success(str,end)
        else:
            return Failure(i)

def lexme(p):
    return (regexpp(r"\s+") + p)(1)

def strp(str): return StrP(str)

def regexpp(str,group=0,**kwargs):
    return RegexpP(str,group,**kwargs)

def token(str,flags=0):
    return regexpp(rf"\s*({str})",group=1,flags=flags)
