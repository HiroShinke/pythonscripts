
from threading import Lock, Thread
import tempfile
import time
import argparse
import tracemalloc
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
import asyncio

ALIVE = '*'
EMPTY = '-'
FILEWORK = 10000
COUNT_NEIGHBOR_WORK = False


class Grid:
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.rows = []
        for _ in range(self.height):
            self.rows.append([EMPTY]*self.width)

    def get(self, y, x):
        return self.rows[ y % self.height ][ x % self.width ]

    def set(self, y, x, state):
        self.rows[ y % self.height ][ x % self.width ] = state

    def __str__(self):
        str_row = [ "".join(r) for r in self.rows ]
        return "\n".join(str_row)


class LockingGrid(Grid):
    def __init__(self, height, width):
        super().__init__(height, width)
        self.lock = Lock()

    def __str__(self):
        with self.lock:
            return super().__str__()

    def get(self, x, y):
        with self.lock:
            return super().get(x, y)

    def set(self, x, y, v):
        with self.lock:
            return super().set(x, y, v)


class ClosableQueue(Queue):

    SENTINEL = object()

    def __init__(self):
        super().__init__()

    def close(self):
        self.put(self.SENTINEL)
        
        
class QueueWorker(Thread):

    SENTINEL = object()
    
    def __init__(self,func,in_q,out_q,print_log=False):
        super().__init__()
        self.func = func
        self.in_q  = in_q
        self.out_q = out_q
        self.print_log = print_log
        
    def run(self):
        print(f"Start Worker: {self.name}")
        while True:
            item = self.in_q.get()
            if self.print_log : print(f"Worker works: {self.name} {item}")
            match item:
                case self.SENTINEL:
                    self.in_q.task_done()                    
                    break
                case _:
                    ret = self.func(item)
                    self.out_q.put(ret)
                    self.in_q.task_done()
                    
        print(f"Stop Worker: {self.name}")

    def stop(self):
        self.in_q.put(self.SENTINEL)


class SimulationError(Exception):
    pass


class ColumnPrinter:

    def __init__(self):
        self.rows = []

    def __str__(self):
        head0 = [ f"{i}".center(len(v))
                  for (i,v) in enumerate(self.rows[0]) ]
        rows1 = [ head0 ]
        rows1.extend(self.rows)
        rows2 = [ "|".join(r) for r in rows1 ]
        return "\n".join(rows2)

    def append(self,text):
        rows0 = text.split("\n")
        if len(self.rows) < len(rows0):
            for _ in range(len(rows0)-len(self.rows)):
                self.rows.append([])
        for i,r in enumerate(rows0):
            self.rows[i].append(r)

def filework():
    f = tempfile.TemporaryFile()
    for i in range(FILEWORK):
        f.write(b'x')
    f.close()

async def co_filework():
    f = tempfile.TemporaryFile()
    for i in range(FILEWORK):
        f.write(b'x')
    f.close()

    
def count_neighbors(y, x, get):
    if COUNT_NEIGHBOR_WORK : filework()
    n_ = get(y - 1, x + 0)
    ne = get(y - 1, x + 1)
    e_ = get(y + 0, x + 1)
    se = get(y + 1, x + 1)
    s_ = get(y + 1, x + 0)
    sw = get(y + 1, x - 1)
    w_ = get(y + 0, x - 1)
    nw = get(y - 1, x - 1)
    neighbor_states = [ n_, ne, e_, se, s_, sw, w_, nw]
    alives = [ s for s in neighbor_states if s == ALIVE ]
    return len(alives)

def count_neighbors_thread(item):
    y, x, state, get = item
    try:
        neighbors = count_neighbors(y, x, get)
    except Exception as e:
        neighbors = e
    return (y, x, state, neighbors)


def game_logic(state,neighbors):
    filework()
    if state == ALIVE:
        if neighbors < 2:
            return EMPTY
        elif neighbors > 3:
            return EMPTY
    else:
        if neighbors == 3:
            return ALIVE
    return state


async def co_game_logic(state,neighbors):
    await co_filework()
    if state == ALIVE:
        if neighbors < 2:
            return EMPTY
        elif neighbors > 3:
            return EMPTY
    else:
        if neighbors == 3:
            return ALIVE
    return state


def game_logic_thread(item):
    y, x, state, neighbors = item
    if isinstance(neighbors, Exception):
        return (y, x, neighbors)
    else:
        pass
    try:
        # print(f"@game_logic_thread x,y = ({x},{y})")
        next_state = game_logic(state, neighbors)
    except Exception as e:
        next_state = e
    return (y, x, next_state)

def step_cell(y, x, get, set):
    state = get(y, x)
    neighbors = count_neighbors(y, x, get)
    next_state = game_logic(state, neighbors)
    set(y, x, next_state)


async def co_step_cell(y, x, get, set):
    state = get(y, x)
    neighbors = count_neighbors(y, x, get)
    next_state = await co_game_logic(state, neighbors)
    set(y, x, next_state)

    
def simulate(grid):
    next_grid = Grid(grid.height, grid.width)
    for y in range(grid.height):
        for x in range(grid.width):
            step_cell(y, x, grid.get, next_grid.set)
    return next_grid

async def co_simulate(grid):
    next_grid = Grid(grid.height, grid.width)

    tasks = []
    for y in range(grid.height):
        for x in range(grid.width):
            task = co_step_cell(y, x, grid.get, next_grid.set)
            tasks.append(task)

    await asyncio.gather(*tasks)
            
    return next_grid


def simulate_threaded(grid):
    next_grid = LockingGrid(grid.height, grid.width)
    threads = []
    for y in range(grid.height):
        for x in range(grid.width):
            def work():
                step_cell(y, x, grid.get, next_grid.set)
            thread = Thread(target=work)
            thread.start()
            threads.append(thread)
    for t in threads:
        t.join()
    return next_grid

def simulate_pool(pool, grid):

    next_grid = LockingGrid(grid.height, grid.width)

    futures = []
    for y in range(grid.height):
        for x in range(grid.width):
            args = (y, x, grid.get, next_grid.set)
            future = pool.submit(step_cell, *args)
            futures.append(future)

    for f in futures:
        f.result()

    return next_grid

def simulate_pipeline(grid, in_queue, out_queue):
    for y in range(grid.height):
        for x in range(grid.width):
            state = grid.get(y, x)
            neighbors = count_neighbors(y, x, grid.get)
            # print(f"(x,y)=({x},{y})")
            in_queue.put((y, x, state, neighbors))

    in_queue.join()
    out_queue.close()

    next_grid = Grid(grid.height, grid.width)

    while (item := out_queue.get()):
        match item:
            case (y, x, next_state):
                next_grid.set(y, x, next_state)
            case ClosableQueue.SENTINEL:
                break
            case _:
                print(f"item = {item}")
                raise SimulationError(y, x) from next_state

    return next_grid

def simulate_phased_pipeline(grid, in_queue, middle_queue, out_queue):
    for y in range(grid.height):
        for x in range(grid.width):
            state = grid.get(y, x)
            in_queue.put((y, x, state, grid.get))

    in_queue.join()
    middle_queue.join()
    out_queue.close()

    next_grid = LockingGrid(grid.height, grid.width)

    while (item := out_queue.get()):
        match item:
            case (y, x, next_state):
                next_grid.set(y, x, next_state)
            case ClosableQueue.SENTINEL:
                break
            case _:
                print(f"item = {item}")
                raise SimulationError(y, x) from next_state

    return next_grid

def testGrid0():
    grid = Grid(5,9)
    grid.set(0, 3, ALIVE)
    grid.set(1, 4, ALIVE)
    grid.set(2, 2, ALIVE)
    grid.set(2, 3, ALIVE)
    grid.set(2, 4, ALIVE)

    columns = ColumnPrinter()
    for i in range(15):
        columns.append(str(grid))
        grid = simulate(grid)

    columns.append(str(grid))        
    print(columns)


def testGrid1():
    grid = LockingGrid(5,9)
    grid.set(0, 3, ALIVE)
    grid.set(1, 4, ALIVE)
    grid.set(2, 2, ALIVE)
    grid.set(2, 3, ALIVE)
    grid.set(2, 4, ALIVE)

    columns = ColumnPrinter()
    for i in range(15):
        columns.append(str(grid))
        grid = simulate_threaded(grid)

    columns.append(str(grid))
    print(columns)

def testGrid2():
    in_queue = ClosableQueue()
    out_queue = ClosableQueue()
    
    threads = []
    for _ in range(5):
        thread = QueueWorker(
            game_logic_thread, in_queue, out_queue)
        thread.start()
        threads.append(thread)
        
    grid = Grid(5,9)
    grid.set(0, 3, ALIVE)
    grid.set(1, 4, ALIVE)
    grid.set(2, 2, ALIVE)
    grid.set(2, 3, ALIVE)
    grid.set(2, 4, ALIVE)

    columns = ColumnPrinter()
    for i in range(15):
        columns.append(str(grid))
        grid = simulate_pipeline(grid,in_queue,out_queue)

    columns.append(str(grid))
    print(columns)

    for t in threads:
        t.stop()

    for t in threads:
        t.join()


def testGrid3():

    in_queue = ClosableQueue()
    middle_queue = ClosableQueue()
    out_queue = ClosableQueue()

    threads = []
    for _ in range(5):
        thread = QueueWorker(
            count_neighbors_thread, in_queue, middle_queue)
        thread.start()
        threads.append(thread)

    for _ in range(5):
        thread = QueueWorker(
            game_logic_thread, middle_queue, out_queue)
        thread.start()
        threads.append(thread)
        
    grid = LockingGrid(5,9)
    grid.set(0, 3, ALIVE)
    grid.set(1, 4, ALIVE)
    grid.set(2, 2, ALIVE)
    grid.set(2, 3, ALIVE)
    grid.set(2, 4, ALIVE)

    columns = ColumnPrinter()
    for i in range(15):
        columns.append(str(grid))
        grid = simulate_phased_pipeline(grid,in_queue,
                                        middle_queue,
                                        out_queue)

    columns.append(str(grid))
    print(columns)

    for t in threads:
        t.stop()

    for t in threads:
        t.join()

def testGrid4():

    grid = LockingGrid(5,9)
    grid.set(0, 3, ALIVE)
    grid.set(1, 4, ALIVE)
    grid.set(2, 2, ALIVE)
    grid.set(2, 3, ALIVE)
    grid.set(2, 4, ALIVE)

    columns = ColumnPrinter()
    with ThreadPoolExecutor(max_workers=10) as pool:
        for i in range(15):
            columns.append(str(grid))
            grid = simulate_pool(pool, grid)

    columns.append(str(grid))
    print(columns)

def testGrid5():

    grid = LockingGrid(5,9)
    grid.set(0, 3, ALIVE)
    grid.set(1, 4, ALIVE)
    grid.set(2, 2, ALIVE)
    grid.set(2, 3, ALIVE)
    grid.set(2, 4, ALIVE)

    columns = ColumnPrinter()

    for i in range(15):
        columns.append(str(grid))
        grid = asyncio.run(co_simulate(grid))
        
    columns.append(str(grid))
    print(columns)
    
def main():

    global FILEWORK
    global COUNT_NEIGHBOR_WORK

    parser = argparse.ArgumentParser()
    parser.add_argument("--type", action="store", default="0")
    parser.add_argument("--filework", type=int, action="store",default=FILEWORK)
    parser.add_argument("--cnwork", action="store_const", const=True)
    args = parser.parse_args()

    if args.filework: FILEWORK = args.filework
    if args.cnwork: COUNT_NEIGHBOR_WORK = True
        
    tracemalloc.start()
    start = time.time()
    
    match args.type:
        case "0":
            testGrid0()
        case "1":
            testGrid1()
        case "2":
            testGrid2()
        case "3":
            testGrid3()
        case "4":
            testGrid4()
        case "5":
            testGrid5()
        case _:
            parser.print_help()

    size, peak = tracemalloc.get_traced_memory()
    end = time.time()
    print("")
    print(f"time diff={end - start:,}")
    print(f"filework = {FILEWORK:,}")
    print(f"count_neighbor work = {COUNT_NEIGHBOR_WORK}")
    print(f"memory current,peek={size:,}, {peak:,}")
    
if __name__ == "__main__":
    main()
