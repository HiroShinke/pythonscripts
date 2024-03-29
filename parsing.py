

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

    def __call__(self,*args):

        if len(args) == 0:
            raise ValueError("args required in __call__")
        elif len(args) == 1:
            def helper(v):
                return v[args[0]]
        else:
            def helper(v):
                return [ v[i] for i in args ]

        return Action(self,helper)

    def __add__(self,b):
        if isinstance(self,Seq) and not self._defined:
            return Seq(*self.parsers,b)
        else:
            return Seq(self,b)

    def __or__(self,b):
        if isinstance(self,Or) and not self._defined:
            return Or(*self.parsers,b)
        else:
            return Or(self,b)
        
    def __rshift__(self,b):
        if isinstance(b,Configurator):
            return b.configure(self)
        else:
            return Action(self,b)

    def __lshift__(self,func):
        def helper(v):
            return func(*v)
        return Action(self,helper)

    def __getitem__(self,key):
         return Many(self,key)

    def __invert__(self):
         return Option(self)

    def __neg__(self):
        return Skip(self)

    def __iter__(self):
        return iter([])

    def splicing(self,splicing=True):
        for p in self:
            if hasattr(p,"splicing"):
                p.splicing(splicing)

    def rec_set_splicing(self,splicing=True):

        check = set()

        def helper(p):
            if p in check:
                return
            else:
                if hasattr(p,"splicing"):
                    p.splicing(splicing)
                check.add(p)
            for c in p:
                helper(c)
                        
        helper(self)


class Configurator(abc.ABC):
    @abc.abstractmethod
    def configure(self,parser:Parser) -> None:
        pass
    
            
    
@dataclass
class Success:
    value : any
    pos   : int
    splicing : bool = False

@dataclass
class Failure:
    pos   : int

def constAction(c):
    return lambda _: c

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
        self._defined = False

    def parse(self,s,i):
        ret = []
        for p in self.parsers:
            match p.parse(s,i):
                case Success(v,j,splicing):
                    if splicing:
                        ret.extend(v)
                    else:
                        ret.append(v)
                    i = j
                case _ as fail:
                    return fail
        return Success(ret,i,self._splicing)

    def splicing(self,splicing=True):
        self._splicing = splicing
        return self

    def defined(self,defined=True):
        self._defined = defined
        return self
    
    def __iter__(self):
        return iter(self.parsers)
    
class Or(Parser):

    def __init__(self,*parsers):
        self.parsers = [ p for p in parsers]
        self._defined = False
        
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

    def defined(self,defined=True):
        self._defined = defined
        return self

    def __iter__(self):
        return iter(self.parsers)
    
class Action(Parser):

    def __init__(self,p,func):
        self.p    = p
        self.func = func

    def parse(self,s,i):
        match self.p.parse(s,i):
            case Success(v,j,splicing):
                return Success(self.func(v),j,splicing)
            case _ as fail:
                return fail

    def __iter__(self):
        return iter([self.p])

class Many(Parser):

    def __init__(self,p,key,splicing=False):
        self.p    = p
        self._splicing = splicing
        ellipsis = type(...)
        match key:
            case int(n):
                self.min = n
                self.max = n
            case ellipsis():
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
        match_count = 0
        while True:
            match self.p.parse(s,i):
                case Success(v,j,splicing):
                    if splicing:
                        ret.extend(v)
                    else:
                        ret.append(v)
                    i = j
                    match_count += 1
                    if self.max == match_count:
                        break
                case _ as fail:
                    break

        if self.min <= match_count:
            return Success(ret,i,self._splicing)
        else:
            return Failure(i)

    def splicing(self,splicing=True):
        self._splicing = splicing
        return self

    def __iter__(self):
        return iter([self.p])


class Option(Parser):

    def __init__(self,p,splicing=False):
        self.p    = p
        self._splicing = splicing

    def parse(self,s,i):
        match self.p.parse(s,i):
            case Success() as succ:
                return succ
            case _ as fail:
                if self._splicing:
                    return Success([],i,True)
                else:
                    return Success(None,i)

    def splicing(self,splicing=True):
        self._splicing = splicing
        return self

    def __iter__(self):
        return iter([self.p])

class Skip(Parser):

    def __init__(self,p):
        self.p    = p

    def parse(self,s,i):
        match self.p.parse(s,i):
            case Success(_,j):
                return Success([],j,True)
            case _ as fail:
                return fail

    def __iter__(self):
        return iter([self.p])
            
                
class Recursive(Parser):

    def __init__(self):
        self.p    = None

    def parse(self,s,i):
        return self.p.parse(s,i)

    def __ilshift__(self,q):

        if ( isinstance(q,Or) and
             isinstance(q.parsers[0],Action) and
             isinstance(q.parsers[0].p,Seq) and
             q.parsers[0].p.parsers[0] is self ):
            self.do_left_recursion(q)
        elif ( isinstance(q,Or) and
             isinstance(q.parsers[0],Seq) and
             q.parsers[0].parsers[0] is  self ):
            self.do_left_recursion2(q)
        else:
            self.p = q

        return self

    def do_left_recursion(self,q):

        first,second = q.parsers
        func1        = first.func
        term         = second
        expr,*rest   = first.p.parsers

        alpha = Seq(*rest)
        expr2 = Recursive()

        def helper(v):
            *args,cont = v
            def tmpfunc(x):
                return cont(func1(x,*args))
            return tmpfunc

        expr2  <<= ( alpha + expr2 >> helper |
                     Empty() >> constAction(lambda x: x) )
        self.p = term + expr2  << (lambda a,cont: cont(a))

    def do_left_recursion2(self,q):

        first,second = q.parsers
        def func1(*args): return [*args]
        term         = second
        expr,*rest   = first.parsers

        alpha = Seq(*rest)
        expr2 = Recursive()

        def helper(v):
            *args,cont = v
            def tmpfunc(x):
                return cont(func1(x,*args))
            return tmpfunc

        expr2  <<= ( alpha + expr2 >> helper |
                     Empty() >> constAction(lambda x: x) )
        self.p = term + expr2  << (lambda a,cont: cont(a))

    def __iter__(self):
        if self.p:
            return iter(self.p)
        else:
            return iter([])
        
class Empty(Parser):

    def __init__(self,c=None):
        self.c    = c

    def parse(self,s,i):
        return Success(self.c,i)

################################################################################
#     Configurator
################################################################################

class Defined(Configurator):

    def __init__(self,defined=True):
        self.defined = defined

    def configure(self,parser):
        parser.defined(self.defined)
        return parser

class Splicing(Configurator):

    def __init__(self,splicing=True):
        self.splicing = splicing

    def configure(self,parser):
        parser.splicing(self.defined)
        return parser

class Tag(Configurator):

    def __init__(self,name):
        self.name = name

    def configure(self,parser):
        def helper(v):
            return [self.name,v]
        return (parser >> helper)
    

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
