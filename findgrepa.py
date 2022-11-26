

import sys
from pathlib import Path
import argparse
import re
import threading as th
import os
import asyncio
import aiofiles

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
    queue.put_nowait((path,pat))

async def work1(inputQueue,outputQueue):

    tid = th.get_native_id()
    
    print(f"work1.pid = {os.getpid()}",file=sys.stderr)
    print(f"work1.tid = {tid}",file=sys.stderr)

    file_num = 0
    
    while m := await inputQueue.get():
        path,pat = m
        if path:
            try:
                file_num += 1
                async with aiofiles.open(path,mode='r') as f:
                    async for x in f:
                        if pat.search(x):
                            await outputQueue.put((path,x))
            except UnicodeDecodeError as e:
                print(f"Error: {str(path)} {e}")                
        else:
            break
        
    print(f"work1 end: {tid} file_num = {file_num}",file=sys.stderr)
    await outputQueue.put((False,tid))
        
async def work2(outputQueue,n):

    print(f"work2.pid = {os.getpid()}",file=sys.stderr)
    print(f"work2.tid = {th.get_native_id()}",file=sys.stderr)

    while True:
        m = await outputQueue.get()
        path, l = m
        if path:
            print(f"{str(path)}: {l}",end="")
        else:
            print(f"work2: work1 end: thread = {l}",file=sys.stderr)            
            n -= 1
            if n == 0:
                break

async def main_(inputQueue,outputQueue,targets,pat,cpu_num):

    tasks = []
    
    for i in range(cpu_num - 1):
        t = asyncio.create_task(work1(inputQueue, outputQueue))
        tasks.append(t)

    ot = asyncio.create_task(work2(outputQueue,cpu_num-1))
        
    for f in targets:
        path = Path(f)
        do_path(path,proc1,pat,inputQueue)
        
    for _ in tasks:
        inputQueue.put_nowait((False,False))

    await asyncio.gather(*tasks,ot)


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
    
    inputQueue = asyncio.Queue()
    outputQueue = asyncio.Queue()

    asyncio.run(main_(inputQueue,outputQueue,args.target,pat,cpu_num))
        
if __name__ == "__main__":
    main()
    
