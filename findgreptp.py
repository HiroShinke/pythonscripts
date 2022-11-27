

import sys
from pathlib import Path
import argparse
import re
import os
import queue
import concurrent.futures

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

    pid = os.getpid()

    print(f"work1.ppid = {os.getppid()}",file=sys.stderr)
    print(f"work1.pid = {pid}",file=sys.stderr)

    file_num = 0
    
    while m := inputQueue.get():
        path,pat = m
        if path:
            try:
                file_num += 1
                with path.open(mode='r') as f:
                    for x in f:
                        if pat.search(x):
                            outputQueue.put((path,x))
            except UnicodeDecodeError as e:
                print(f"Error: {str(path)} {e}")
        else:
            break
        
    print(f"work1 end: {pid} file_num = {file_num}",file=sys.stderr)
    outputQueue.put((False,pid))
        
def work2(outputQueue,n):

    print(f"work2.ppid = {os.getppid()}",file=sys.stderr)
    print(f"work2.pid = {os.getpid()}",file=sys.stderr)

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

    print(f"cpu_num = {os.cpu_count()}",file=sys.stderr)
    
    parser = argparse.ArgumentParser()
    parser.add_argument("target",action='append')
    parser.add_argument("-e" )
    parser.add_argument("-n", "--cpu_num", type=int, default=os.cpu_count())
    args = parser.parse_args()
    pat = re.compile(args.e)
    cpu_num  = args.cpu_num
    
    if cpu_num > 1:
        pass
    else:
        raise ValueError(f"num must be > 1")
    
    inputQueue = queue.Queue()
    outputQueue = queue.Queue()

    futures = set()

    with concurrent.futures.ThreadPoolExecutor(
            max_workers = cpu_num) as executor:

        for _ in range(cpu_num - 1):
            f = executor.submit(work1,inputQueue,outputQueue)
            print(f"{f}",file=sys.stderr)
            futures.add(f)

        f = executor.submit(work2,outputQueue,cpu_num-1)
        print(f"{f}",file=sys.stderr)        
        futures.add(f)

        for p in args.target:
            path = Path(p)
            do_path(path,proc1,pat,inputQueue)
        
        for _ in range(cpu_num-1):
            inputQueue.put((False,False))
            
        for future in concurrent.futures.as_completed(futures):
            err = future.exception()
            if err is None:
                pass
            else:
                print(f"{f}: err = {err}",file=sys.stderr)
                
if __name__ == "__main__":
    main()
    
