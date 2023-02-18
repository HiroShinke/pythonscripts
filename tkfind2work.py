

import sys
import os
import multiprocessing as mp
import concurrent.futures
import queue

def func(f):
    print(f"{f}")

def do_rec_file(fp,queue):

    try:
        func(fp)
        if fp.is_dir():
            for c in fp.iterdir():
                queue.put(c)
    except Exception as e:
        print(f"{fp} {e}")


def call_do_grep(top,patStr,type,functext=None,callback=None):
                
    if patStr:
        pat = re.compile(patStr)
    else:
        pat = None
    
    if not type:
        def pred(f):
            return True
    elif type == "f":
        def pred(f):
            return f.is_file()
    elif type == "d":
        def pred(f):
            return f.is_dir()
        
    of = sys.stdout
    que = mp.Manager().Queue()
    que.put(top)

    count_processing = 0
    count_done = 0

    with concurrent.futures.ProcessPoolExecutor(
            max_workers = os.cpu_count()-1) as executor:
        
        DONE = False

        while not DONE:

            if que.empty():
                break

            futures = set()
            
            try:                
                while fp := que.get(False):
                    count_processing += 1
                    fut = executor.submit(do_rec_file,fp,que)
                    futures.add(fut)
                    if callback(count_processing,count_done):
                        print(f"executor.shutdown() future count = {len(futures)}")
                        executor.shutdown()                            
                        for fut in futures:
                            fut.cancel()
                        DONE = True
                        break
            except queue.Empty:
                pass

            for fut in concurrent.futures.as_completed(futures):
                err = fut.exception()
                count_done += 1
                callback(count_processing,count_done)
                if err is None:
                    pass
                else:
                    print(f"{fut}: err = {err}",file=sys.stderr)

    if callback:
        callback(None,None)


def compileFuncObj(text):
    l = dict()
    exec(text,globals(),l)
    if l:
        return list(l.values())[0]

