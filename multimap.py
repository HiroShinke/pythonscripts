

from collections.abc import Mapping

def multi_map_do(m, proc, *args):
    for k in m.keys():
        c = m[k]
        if isinstance(c,Mapping):
            multi_map_do(c,proc,*args,k)
        else:
            proc(*args,k,c)

## for python3.10 or later
            
def multi_map_do2(m, proc, *args):
    for k in m.keys():
        match (c := m[k]):
            case Mapping():
                multi_map_do2(c,proc,*args,k)
            case _:
                proc(*args,k,c)
            
def test():

    x = { "a" : 1,
          "b" : 2,
          "c" : 3 }
    
    multi_map_do(x,
                 lambda *x : print(f"x = {x}")
                 )
    
    def func(*args):
        print(f"args = {args}")
        
    def func2(x,y):
        print(f"x,y = {x},{y}")
            
    multi_map_do(x,func)
    multi_map_do(x,func2)
        
    x = { "a" : { "x" : "11" , "y" : "12", "z" : "13" },
          "b" : { "x" : "21" , "y" : "22", "z" : "23" },
          "c" : { "x" : "31" , "y" : "32", "z" : "33" } }
            
    def func3(x,y,z):
        print(f"x,y,z= {x},{y},{z}")
            
    multi_map_do(x,func)
    multi_map_do(x,func3)

    multi_map_do2(x,func3)

if __name__ == "__main__":
    test()

