


import itertools


def fib_gen(a,b):
    yield a
    yield from fib_gen(b,a + b)

def fib_iter(a,b):
    yield from itertools.chain([a],fib_iter(b,a+b))

    
def main():
    print(list(itertools.islice(fib_gen(1,2),0,10)))
    print(list(itertools.islice(fib_iter(1,2),0,10)))
    
if __name__ == "__main__":
    main()

    


