

import re
import abc
from dataclasses import dataclass

SUCCESS = True
FAILED  = False

class Parser(abc.ABC):
    @abc.abstractmethod
    def parse(self,seq,i):
        pass

    def __call__(self,*args,**keys):
        return self.parser(*args,**keys)

    def __add__(self,b):
        if isinstance(self,Seq):
            return Seq(*self.parsers,b)
        else:
            return Seq(self,b)

    def __or__(self,b):
        if isinstance(self,Or):
            return Or(*self.parsers,b)
        else:
            return Or(self,b)
        
    def __rshift__(self,func):
         return Action(self,func)

    def __getitem__(self,key):
         return Many(self,key)

    
@dataclass
class Success:
    value : any
    ind   : int

@dataclass
class Failure:
    ind   : int


class Pred(Parser):
    def __init__(self,pred):
        self.pred = pred
    def parse(self,s,i):
        if i < len(s) and self.pred(s[i]):
            return Success(s[i],i+1)
        else:
            return Failure(i)

class Seq(Parser):

    def __init__(self,*parsers,splicing=False):
        self.parsers = [ p for p in parsers]
        self._splicing = splicing

    def parse(self,s,i):
        ret = []
        for p in self.parsers:
            match p.parse(s,i):
                case Success(v,j):
                    if (self._splicing and
                        isinstance(v,list)):
                        ret.extend(v)
                    else:
                        ret.append(v)
                    i = j
                case _ as fail:
                    return fail
        return Success(ret,i)

    def splicing(self,splicing=True):
        self._splicing = splicing
        return self
    
class Or(Parser):

    def __init__(self,*parsers):
        self.parsers = [ p for p in parsers]

    def parse(self,s,i):
        maxi = i
        for p in self.parsers:
            match p.parse(s,i):
                case Success(v,j):
                    return Success(v,j)
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

    def __init__(self,p,key,splicing=False):
        self.p    = p
        self._splicing = splicing
        match key:
            case int(n):
                self.min = n
                self.max = n
            case n if isinstance(n,type(...)):
                self.min = 0
                self.max = None
            case (int(n),int(m)):
                self.min = n
                self.max = m
            case (_,int(n)):
                self.min = 0
                self.max = n
            case (int(n),_):
                self.min = n
                self.max = None
    
    def parse(self,s,i):

        ret = []
        while True:
            match self.p.parse(s,i):
                case Success(v,j):
                    if (self._splicing and
                        isinstance(v,list)):
                        ret.extend(v)
                    else:
                        ret.append(v)
                    i = j
                    if self.max == len(ret):
                        break
                case _ as fail:
                    break

        if self.min <= len(ret):
            return Success(ret,i)
        else:
            return Failure(i)

    def splicing(self,splicing=True):
        self._splicing = splicing
        return self
        
class Recursive(Parser):

    def __init__(self):
        self.p    = None

    def parse(self,s,i):
        match self.p.parse(s,i):
            case Success(v,j):
                return Success(v,j)
            case _ as fail:
                return fail
    
    def __ilshift__(self,q):
        self.p = q
        return self


################################################################################
# special parser for string

class strP(Parser):

    def __init__(self,str):
        self.str = str

    def parse(self,s,i):
        pos = i+len(self.str)
        if s[i:i+len(self.str)] == self.str:
            return Success(self.str,pos)
        else:
            return Failure(i)

class regexpP(Parser):

    def __init__(self,str,*args,**kwargs):
        self.re = re.compile(str,*args,**kwargs)

    def parse(self,s,i):
        if m := self.re.match(s,i):
            str = m.group(0)
            return Success(str,i+len(str))
        else:
            return Failure(i)


