"""Deterministic four-connected point-robot model. Coordinates are (row, column)."""
from dataclasses import dataclass

# Try moves in a fixed order: Up, Down, Left, Right.
DIRECTIONS = ((-1, 0), (1, 0), (0, -1), (0, 1))


# The grid stores the problem itself, not the search algorithm.
@dataclass(frozen=True)
class Grid:
    rows: int
    cols: int
    walls: frozenset
    start: tuple
    goal: tuple

    # Validate the map immediately after creating a Grid object.
    def __post_init__(self):
        if self.rows < 1 or self.cols < 1 or any(not self.inside(p) for p in self.walls):
            raise ValueError("Invalid grid dimensions or wall coordinates")
        if not self.free(self.start) or not self.free(self.goal):
            raise ValueError("Start and goal must both be free cells")

    # Only cells outside the walls count as reachable candidate states.
    @property
    def size(self):
        return self.rows * self.cols - len(self.walls)

    # A cell is inside if its row and column are within the grid bounds.
    def inside(self, p):
        return 0 <= p[0] < self.rows and 0 <= p[1] < self.cols

    # The robot can enter a cell only if it is inside and not blocked.
    def free(self, p):
        return self.inside(p) and p not in self.walls

    # Generate legal next states, ignoring walls and out-of-bounds moves.
    def neighbors(self, p):
        for dr, dc in DIRECTIONS:
            q = (p[0] + dr, p[1] + dc)
            if self.free(q):
                yield q

    # All legal moves have equal cost in our Phase I main model.
    def step_cost(self, p, q):
        """Cost of a legal transition supplied by neighbors."""
        return 1

    # Reject invalid paths and add up the costs of legal moves.
    def path_cost(self, path):
        if not path or path[0] != self.start or path[-1] != self.goal:
            raise ValueError("Path must connect the endpoints")
        cost = 0
        for p, q in zip(path, path[1:]):
            if q not in self.neighbors(p):
                raise ValueError("Illegal move")
            cost += self.step_cost(p, q)
        return cost


# Prepare the main warehouse and two small maps for testing.
def maps():
    # Two doorways per shelf. Every free aisle connects through a doorway.
    walls = set()
    for col, door in [(5, 9), (11, 3), (17, 12), (23, 7), (29, 16), (35, 4)]:
        for row in range(40):
            if row not in (door, 32):
                walls.add((row, col))
    # detour is solvable; blocked has no route through its dividing wall.
    return {
        "main": Grid(40, 40, frozenset(walls), (2, 2), (12, 19)),
        "detour": Grid(5, 7, frozenset((r, 3) for r in range(4)), (0, 0), (0, 6)),
        "blocked": Grid(5, 7, frozenset((r, 3) for r in range(5)), (0, 0), (0, 6)),
    }

