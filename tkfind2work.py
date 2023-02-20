

import sys
import os
import multiprocessing as mp
import concurrent.futures
import queue
import re


def do_rec_file(fp,type,patStr,linePatStr,functext,queue):

    if not type:
        def pred(f):
            return True
    elif type == "f":
        def pred(f):
            return f.is_file()
    elif type == "d":
        def pred(f):
            return f.is_dir()

    if patStr:
        pat = re.compile(patStr)
    else:
        pat = None

    if functext:
        _func = compileFuncObj(functext)
        if _func:
            def func(f):
                if f.is_file():
                    _func(f)
    if not func:
        if linePatStr:
            linePat = re.compile(linePatStr)
        else:
            linePat = None

        if linePat:
            def func(f):
                if f.is_file():
                    with open(f) as fh:
                        contents = fh.read()
                        lines = contents.splitlines()
                        for l in lines:
                            if linePat.search(l):
                                print(f"{f}: {l}")
    if not func:
        def func(f):
            print(f"{f}")

    try:
        if pred(fp) and ( not pat or pat.search(fp.name) ):
            func(fp)
        if fp.is_dir() and fp.name != ".git":
            for c in fp.iterdir():
                queue.put(c)
    except Exception as e:
        print(f"{fp} {e}")


def call_do_grep(top,patStr,linePatStr,type,
                 functext=None,
                 callback=None):

    of = sys.stdout
    que = mp.Manager().Queue()
    que.put(top)

    count_processing = 0
    count_done = 0

    with concurrent.futures.ProcessPoolExecutor(
            max_workers = os.cpu_count()-1) as executor:
        
        done = False

        while not done:

            if que.empty():
                break

            futures = set()
            
            try:                
                while fp := que.get(False):
                    count_processing += 1
                    fut = executor.submit(do_rec_file,
                                          fp,
                                          type,
                                          patStr,
                                          linePatStr,
                                          functext,
                                          que)
                    futures.add(fut)
                    if callback(count_processing,count_done):
                        print("executor.shutdown() "
                              f"future count = {len(futures)}")
                        executor.shutdown()                            
                        for fut in futures:
                            fut.cancel()
                        done = True
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
        # return list(l.values())[0]
        return l["filefunc"]
