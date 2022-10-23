

import subprocess
from ctypes import *

def make_csource(p,contents):

    fh = open(p,"w")
    fh.write(contents)

def make_lib():

    srccode = r"""
#include <stdio.h>
#include <string.h>

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
    
"""
    make_csource("test1.c",srccode)
    args = "gcc test1.c -shared -o libctypestest.so".split(" ")
    subprocess.run(args)
    
    
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
    

if __name__ == "__main__":
    main()
