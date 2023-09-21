

import re
import abc
import types
from dataclasses import dataclass

SUCCESS = True
FAILED  = False

class Parser(abc.ABC):

    @abc.abstractmethod
    def parseImpl(self,seq,i):
        pass

    def parse(self,seq,i):
        if hasattr(self,"tag") and self.tag:
            match self.parseImpl(seq,i):
                case Success(v,j):
                    return Success([self.tag,v],j)
                case _ as fail:
                    return fail
        elif hasattr(self,"action") and self.action:
            match self.parseImpl(seq,i):
                case Success(v,j):
                    return Success(self.action(v),j)
                case _ as fail:
                    return fail
        else:
            return self.parseImpl(seq,i)

    def setTag(self,tag):
        self.tag = tag
        return self

    
@dataclass
class Success:
    value : any
    pos   : int
    splicing : bool = False

@dataclass
class Failure:
    pos   : int


class Pred(Parser):
    def __init__(self,pred):
        self.pred = pred
    def parseImpl(self,s,i):
        if i < len(s) and self.pred(s[i]):
            return Success(s[i],i+1)
        else:
            return Failure(i)

class Seq(Parser):

    def __init__(self,*parsers,splicing=False,**kwparsers):
        if parsers and kwparsers:
            raise ValueError(
                "only all positional or all keyword parameters are possible"
            )
        if parsers:
            self.parsers = list(parsers)
        elif kwparsers:
            self.parsers = dict(kwparsers)

        self.splicing = splicing

    def parseImpl(self,s,i):
        ret = []
        if isinstance(self.parsers,list):
            for p in self.parsers:
                match p.parse(s,i):
                    case Success(v,j):
                        if self.splicing:
                            ret.extend(v)
                        else:
                            ret.append(v)
                        i = j
                    case _ as fail:
                        return fail
            return Success(ret,i,self.splicing)
        elif isinstance(self.parsers,dict):
            for k,p in self.parsers.items():
                match p.parse(s,i):
                    case Success(v,j):
                        ret.append([k,v])
                        i = j
                    case _ as fail:
                        return fail
            return Success(ret,i,self.splicing)

def seqs(*parsers,**kwparsers):
    return Seq(*parsers,splicing=True,**kwparsers)
        

class Or(Parser):

    def __init__(self,*parsers,**kwparsers):
        if parsers and kwparsers:
            raise ValueError(
                "only all positional or all keyword parameters are possible"
            )
        if parsers:
            self.parsers = list(parsers)
        elif kwparsers:
            self.parsers = dict(kwparsers)

    def parseImpl(self,s,i):
        maxi = i
        if isinstance(self.parsers,list):
            for p in self.parsers:
                match p.parse(s,i):
                    case Success() as succ:
                        return succ
                    case Failure(j):
                        if maxi < j:
                            maxi = j
        elif isinstance(self.parsers,dict):
            for k,p in self.parsers.items():
                match p.parse(s,i):
                    case Success(v,j):
                        return Success([k,v],j)
                    case Failure(j):
                        if maxi < j:
                            maxi = j
        return Failure(maxi)
    
    
class Many(Parser):

    def __init__(self,p,splicing=False):
        self.p    = p
        self.splicing = splicing

    def parseImpl(self,s,i):
        ret = []
        while True:
            match self.p.parse(s,i):
                case Success(v,j):
                    if self.splicing:
                        ret.extend(v)
                    else:
                        ret.append(v)
                    i = j
                case _ as fail:
                    break
        return Success(ret,i,self.splicing)


def manys(p):
    return Many(p,splicing=True)
    

class Opt(Parser):

    def __init__(self,p):
        self.p    = p

    def parseImpl(self,s,i):
        match self.p.parse(s,i):
            case Success() as succ:
                return succ
            case _ as fail:
                return Success(None,i)

class Recursive(Parser):

    def __init__(self):
        self.p    = None

    def parseImpl(self,s,i):
        return self.p.parse(s,i)

    def defined(self,q):
        self.p = q
        return self

        
class Empty(Parser):

    def __init__(self,c=None):
        self.c    = c

    def parseImpl(self,s,i):
        return Success(self.c,i)


################################################################################
# special parser for string


class StrP(Parser):

    def __init__(self,str):
        self.str = str

    def parseImpl(self,s,i):
        pos = i+len(self.str)
        if s[i:i+len(self.str)] == self.str:
            return Success(self.str,pos)
        else:
            return Failure(i)

class RegexpP(Parser):

    def __init__(self,str,group=0,**kwargs):
        self.re = re.compile(str,**kwargs)
        self.group = group

    def parseImpl(self,s,i):
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
