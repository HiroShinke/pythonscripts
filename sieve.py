

import itertools

def sieve(n):
    yield from itertools.chain([n],
                               filter(lambda x: x % n != 0,
                                      sieve(n+1)))
def sieve_gen(n):
    yield n
    yield from filter(lambda x: x % n != 0,
                      sieve_gen(n+1))
    
def take(itr,n):
    return list(itertools.islice(itr,n))

print(list(take(sieve(2), 20)))
print(list(take(sieve_gen(2), 20)))
