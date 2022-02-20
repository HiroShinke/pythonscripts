


ALIVE = '*'
EMPTY = '-'

class Grid:
    def __init__(self, height, width):
        self.height = height
        self.width  = width
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

class ColumnPrinter:

    def __init__(self):
        self.rows = [];

    def __str__(self):
        head0 = [ f"{i}".center(len(v))
                  for (i,v) in enumerate(self.rows[0]) ]
        rows1 = [ head0 ]
        rows1.extend(self.rows)
        rows2 = [ "|".join(r) for r in rows1 ]
        return "\n".join(rows2)

    def append(self,text):
        rows0 = text.split("\n");
        if len(self.rows) < len(rows0):
            for _ in range(len(rows0)-len(self.rows)):
                self.rows.append([])
        for i,r in enumerate(rows0):
            self.rows[i].append(r)
        
def count_neighbors(y, x, get):
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

def game_logic(state,neighbors):
    if state == ALIVE:
        if neighbors < 2:
            return EMPTY
        elif neighbors > 3:
            return EMPTY
    else:
        if neighbors == 3:
            return ALIVE
    return state

def step_cell(y, x, get, set):
    state = get(y, x)
    neighbors = count_neighbors(y, x, get)
    next_state = game_logic(state, neighbors)
    set(y, x, next_state)

def simulate(grid):
    next_grid = Grid(grid.height, grid.width)
    for y in range(grid.height):
        for x in range(grid.width):
            step_cell(y, x, grid.get, next_grid.set)
    return next_grid

def test():
    grid = Grid(5,9)
    grid.set(0, 3, ALIVE)
    grid.set(1, 4, ALIVE)
    grid.set(2, 2, ALIVE)
    grid.set(2, 3, ALIVE)
    grid.set(2, 4, ALIVE)
    print(grid)
    print(f"count={count_neighbors(1,4,grid.get)}")

    columns = ColumnPrinter()
    for i in range(5):
        print(f"step={i}")
        columns.append(str(grid))
        grid = simulate(grid)

    print(columns)
        

if __name__ == "__main__":
    test()
