

from threading import Thread
from queue import Queue
from pathlib import Path
import argparse
import time


SENTINEL = object()

class QueueWorker(Thread):

    def __init__(self,name,in_q,out_q,print_log=False,work=None):
        super().__init__()
        self.name = name
        self.in_q  = in_q
        self.out_q = out_q
        self.print_log = print_log
        self.work = work
        
    def run(self):
        print(f"Start Worker: {self.name}")
        while True:
            item = self.in_q.get()
            if self.print_log : print(f"Worker works: {self.name} {item}")
            if self.work : self.work()
            self.out_q.put(item)
            if item is SENTINEL:
                break
        print(f"Stop Worker: {self.name}")

    def filework(self):
        f = Path(self.name).open("w")
        f.write("xxxxxx")
        f.close()
        f.delete()

class Consumer(Thread):

    def __init__(self,name,in_q,print_log=False):
        super().__init__()
        self.name = name
        self.in_q  = in_q
        self.print_log = print_log
            
    def run(self):
        if self.print_log : print(f"Start Consumer: {self.name}")
        while True:
            item = self.in_q.get()
            if self.print_log : print(f"Consumer Consumes: {self.name} {item}")
            if item is SENTINEL:
                break
        if self.print_log : print(f"Stop Consumer: {self.name}")
        

def do_pipeline(queue_spec,worker_spec,item_num,work_type):

    start_t = time.time()
    print(f"start time {start_t}: queue={queue_spec} worker={worker_spec}")

    queues = [ Queue(qs) for qs in queue_spec ]

    work = QueueWorker.filework if work_type == "file" else None
    
    pipeline = []
    count = 0
    for q1,q2 in zip(queues,queues[1:]):
        pipeline.append( QueueWorker(f"step{count}",q1,q2,work=work) )

    c = Consumer("consumer0",queues[-1])
        
    for w in pipeline :
        w.start()

    c.start()

    for _ in range(item_num):
        queues[0].put(object())
        
    queues[0].put(SENTINEL)
    
    for w in pipeline :
        w.join()

    end_t = time.time()
    print(f"end time {end_t}")
    print(f"diff time {end_t - start_t}")

def intlist(str):
    r = [ int(n) for n in str.split(",") ]
    return r

# class ParseList(argparse.Action):
#     def __call__(self, parser, namespace, values, option_string=None):
#         vs = [ int(x) for x in values.split(",")]
#         current = getattr(namespace, self.dest)
#         current.extend(vs)
#         setattr(namespace, self.dest, current)

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--queue" ,  type=intlist, action="store", default=[1,1,1,1])
    parser.add_argument("--worker",  type=intlist, action="store", default=[1,1,1,1])
    parser.add_argument("--item",    type=int, action="store", default=100)
    parser.add_argument("--worktype",type=str, action="store", default=None)
    args = parser.parse_args()

    do_pipeline(queue_spec=args.queue,
                worker_spec=args.worker,
                item_num=args.item,
                work_type=args.worktype)
    
if __name__ == "__main__":
    main()




