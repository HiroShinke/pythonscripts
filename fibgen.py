


import itertools


def fib_gen(a,b):
    yield a
    yield from fib_gen(b,a + b)

def fib_iter(a,b):
    yield from itertools.chain([a],fib_iter(b,a+b))

def take(n,iterable):
    return list(itertools.islice(iterable,n))
    
def main():
    print(take(10,fib_gen(1,2)))
    print(take(10,fib_iter(1,2)))
    
if __name__ == "__main__":
    main()

    


