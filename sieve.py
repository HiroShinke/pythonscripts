

def fibonacci(a,b):
    """ Fibonacci generator """
    while True:
        yield a
        a, b = b, a + b

def stream_take(s,n):
    for i in range(n):
        yield(next(s))
        
print(list(stream_take(fibonacci(0,1), 20)))

