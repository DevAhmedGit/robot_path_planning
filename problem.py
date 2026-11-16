from collections import namedtuple

State = namedtuple("State", ["x", "y", "heading"])

HEADINGS = ["N", "E", "S", "W"]
DELTAS = {0: (0, -1), 1: (1, 0), 2: (0, 1), 3: (-1, 0)}

OBSTACLE = "#"
TERRAIN_COST = {".": 1, "r": 3, "m": 5}
TURN_COST = 2

ACTIONS = ("FORWARD", "LEFT", "RIGHT")


class RobotProblem:
    def __init__(self, map_rows, start_heading=1):
        self.rows = list(map_rows)
        self.height = len(self.rows)
        self.width = len(self.rows[0])
        assert all(len(r) == self.width for r in self.rows)

        self.grid = {}
        self.start_xy = None
        self.goal_xy = None
        for y, row in enumerate(self.rows):
            for x, ch in enumerate(row):
                if ch == "S":
                    self.start_xy = (x, y)
                    ch = "."
                elif ch == "G":
                    self.goal_xy = (x, y)
                    ch = "."
                if ch != OBSTACLE:
                    assert ch in TERRAIN_COST
                    self.grid[(x, y)] = ch
        assert self.start_xy and self.goal_xy
        self.start_heading = start_heading

    def initial_state(self):
        return State(self.start_xy[0], self.start_xy[1], self.start_heading)

    def goal_test(self, state):
        return (state.x, state.y) == self.goal_xy

    def successors(self, state):
        result = []
        dx, dy = DELTAS[state.heading]
        nxt = (state.x + dx, state.y + dy)
        if nxt in self.grid:
            cost = TERRAIN_COST[self.grid[nxt]]
            result.append(("FORWARD", State(nxt[0], nxt[1], state.heading), cost))
        result.append(("LEFT", State(state.x, state.y, (state.heading - 1) % 4), TURN_COST))
        result.append(("RIGHT", State(state.x, state.y, (state.heading + 1) % 4), TURN_COST))
        return result

    def state_space_size(self):
        return len(self.grid) * 4

    def terrain_at(self, x, y):
        return self.grid.get((x, y), OBSTACLE)


SAMPLE_MAP = [
    "S...#.....",
    ".##.#.rr..",
    ".#..#.rr#.",
    ".#.mm...#.",
    ".#.mm.###.",
    ".#....#...",
    ".####.#.#.",
    "......#.#.",
    ".######.#.",
    "........#G",
]


def make_problem():
    return RobotProblem(SAMPLE_MAP, start_heading=1)


if __name__ == "__main__":
    p = make_problem()
    print("Grid:", p.width, "x", p.height)
    print("Free cells:", len(p.grid), "-> states:", p.state_space_size())
    s0 = p.initial_state()
    print("Initial:", s0)
    for a, s, c in p.successors(s0):
        print(" ", a, s, "cost", c)