

import subprocess
from ctypes import *

def make_csource(p,contents):

    fh = open(p,"w")
    fh.write(contents)

def make_lib():

    srccode = r"""
#include <stdio.h>
#include <string.h>

struct Point {
    int x;
    int y;
};


void test1(int i){
    printf("test1 called: %d\n",i);
}

int test2(int i){
    printf("test2 called: %d\n",i);
    return i+1;
}

void test3(char *str){
    printf("test3 called: %s\n",str);
    memcpy(str,"Bye  ",5);
}

int test4(int n,int(*func)(int)){
    printf("test4 called: %d\n",func(n));
    return n;
}

int test5(struct Point p){
    printf("test5 called: point = (%d,%d)\n",p.x,p.y);
    return 0;
}

int test6(struct Point *p){
    printf("test6 called: point = (%d,%d)\n",p->x,p->y);
    return 0;
}

int test7(struct Point *p){
    printf("test7 called: point = (%d,%d)\n",p->x,p->y);
    p->x = 30;
    p->y = 40;
    return 0;
}

int test8(long *d){
    printf("test8 called: long = %lx\n",*d);
    *d = 0x10000000;
    return 0;
}

    
"""
    make_csource("test1.c",srccode)
    args = "gcc test1.c -shared -o libctypestest.so".split(" ")
    subprocess.run(args)


class POINT(Structure):
    _fields_ = [("x", c_int),("y", c_int)]

    
def main():

    make_lib()

    libtest = cdll.LoadLibrary("libctypestest.so")


    print(f"{libtest.test1(10)}")
    print(f"{libtest.test2(10)}")

    buffer = create_string_buffer(b"Hello, World!")
    print(f"{buffer.value}")
    print(f"{libtest.test3(buffer)}")
    print(f"{buffer.value}")

    TESTFUNC = CFUNCTYPE(c_int,c_int)

    def testcallback(n):
        print(f"callback called with {n}")
        return n*2

    funcobj = TESTFUNC(testcallback)

    print(f"{libtest.test4(10,funcobj)}")

    point = POINT(10,20)

    print(f"{point.x},{point.y}")

    print(f"{libtest.test5(point)}")

    print(f"{libtest.test6(pointer(point))}")

    print(f"{libtest.test7(pointer(point))}")

    print(f"{point.x} {point.y}")

    lp = pointer(c_long(0x20000000))
    print(f"lp.contents = {lp.contents}")

    print(f"{libtest.test8(lp)}")
    print(f"lp.contents = {lp.contents}")

    buff = create_string_buffer(b"\x00\x00\x00\x20",4)
    print(f"{libtest.test8(buff)}")
    n = int.from_bytes(buff.raw,"little")
    print(f"n = {n}")

    pn = cast(buff,POINTER(c_long))
    print(f"pn.contents = {pn.contents}")

    
    libc    = cdll.LoadLibrary("libSystem.B.dylib") 
    libc.printf(b"libc called %s, %d\n", b"Hello, libc", 10)

    COMPFUNC = CFUNCTYPE(c_int, POINTER(POINT), POINTER(POINT))

    def cmp_point(p1,p2):
        if d1 := p1.contents.x - p2.contents.x:
            return d1
        elif d2 := p1.contents.y - p2.contents.y:
            return d2
        else:
            return 0
    
    cmp_func = COMPFUNC(cmp_point)
    TenPointArrayType = POINT * 6
    array = TenPointArrayType(POINT(10,20),
                              POINT(10,30),
                              POINT(5,20),
                              POINT(15,10),
                              POINT(10,25),
                              POINT(5,5))

    libc.qsort(array,6,sizeof(POINT),cmp_func)

    for p in array:
        print(f"{p.x} {p.y}")


    
if __name__ == "__main__":
    main()
