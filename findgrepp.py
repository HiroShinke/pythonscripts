

import sys
from pathlib import Path
import argparse
import re
import multiprocessing as mp
import os

def do_path(path,proc,*args):
    if re.search(r"\.git",path.name):
        pass
    elif path.is_dir():
        do_dir(path,proc,*args)
    else:
        do_file(path,proc,*args)

def do_file(path,proc,*args):
    proc(path,*args)

def do_dir(path,proc,*args):
    for x in path.iterdir():
        do_path(x,proc,*args)

def proc1(path,pat,queue):
    queue.put((path,pat))

def work1(inputQueue,outputQueue):

    while m := inputQueue.get():
        path,pat = m
        if path:
            try:
                with path.open(mode='r') as f:
                    for x in f:
                        if pat.search(x):
                            outputQueue.put((path,x))
            except UnicodeDecodeError as e:
                print(f"Error: {str(path)} {e}")
        else:
            break
        
    print("work1 end")
    outputQueue.put((False,False))
        
def work2(outputQueue,n):

    while True:
        m = outputQueue.get()
        path, l = m
        if path:
            print(f"{str(path)}: {l}",end="")
        else:
            n -= 1
            if n == 0:
                break
        
def main():

    cpu_num = os.cpu_count()
    
    parser = argparse.ArgumentParser()
    parser.add_argument("target",action='append')
    parser.add_argument("-e" )
    parser.add_argument("-n", "--num", type=int, default=cpu_num)
    args = parser.parse_args()
    pat = re.compile(args.e)
    n   = args.num
    
    if n > 1:
        pass
    else:
        raise ValueError(f"num must be > 1")
    
    inputQueue = mp.Queue()
    outputQueue = mp.Queue()

    procs = []
    
    for i in range(n - 1):
        p = mp.Process(target=work1, args=(inputQueue, outputQueue))
        procs.append(p)
        p.start()

    q = mp.Process(target=work2, args=(outputQueue,n-1))
    q.start()
    
    for f in args.target:
        path = Path(f)
        do_path(path,proc1,pat,inputQueue)

    for _ in procs:
        inputQueue.put((False,False))
        
    for p in procs:
        p.join()

    q.join()

        
if __name__ == "__main__":
    main()
    
