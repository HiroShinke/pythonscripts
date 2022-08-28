


import itertools

def mergesort(iterable):
    try:
        a = next(iterable)
        it1,it2 = itertools.tee(iterable)
        yield from mergesort( filter(lambda x: x <= a, it1) )
        yield a
        yield from mergesort( filter(lambda x: a < x, it2) )
    except:
        pass
    
if __name__ == "__main__":
    a = [2, 4, 6, 9, 10, 3, 8, 100, 75, 90, 30]
    print(list(mergesort(iter(a))))

    
