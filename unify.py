

from dataclasses import dataclass

@dataclass
class Term:
    pass

@dataclass
class Var(Term):
    name : str

@dataclass
class Const(Term):
    value : object

@dataclass
class App(Term):
    name : str
    args : list[Term]

def app(n,*args):
    return App(n,args)
    
def unify(x,y,subst):
    if x == y:
        return subst
    elif isinstance(x,Var):
        return unify_variable(x,y,subst)
    elif isinstance(y,Var):
        return unify_variable(y,x,subst)
    elif isinstance(x,App) and isinstance(y,App):
        if ( x.name      != y.name or 
             len(x.args) != len(y.args) ):
            return None
        else:
            for a,b in zip(x.args,y.args):
                subst = unify(a,b,subst)
                if subst is None: return None
            return subst
    else:
        return None
            
def unify_variable(v,x,subst):
    assert(isinstance(v,Var))
    if v.name in subst:
        return unify(subst[v.name],x,subst)
    elif isinstance(x,Var) and x.name in subst:
        return unify(v,subst[x.name],subst)
    elif occurs_check(v,x,subst):
        return None
    else:
        return subst | { v.name : x }
    
def occurs_check(v,term,subst):
    assert isinstance(v, Var)
    if v == term:
        return True
    elif isinstance(term, Var) and term.name in subst:
        return occurs_check(v, subst[term.name], subst)
    elif isinstance(term, App):
        return any(occurs_check(v, arg, subst) for arg in term.args)
    else:
        return False    
