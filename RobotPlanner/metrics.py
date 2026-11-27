"""Count accepted frontier entries and successor enumerations."""
from dataclasses import dataclass, field


# Each algorithm reports its outcome with the same measurements.
@dataclass
class Result:
    path: list = field(default_factory=list)
    generated: int = 0
    expanded: int = 0
    peak: int = 0
    explored: set = field(default_factory=set)
    status: str = "unreachable"

    # Count accepted frontier entries, including the start state.
    # Peak is the largest number of pending entries at any one time.
    def pushed(self, size):
        self.generated += 1
        self.peak = max(self.peak, size)

    # A state is expanded when we examine its possible next moves.
    def expand(self, state):
        self.expanded += 1
        self.explored.add(state)

    # Reconstruct the final route by following parent links backward.
    def solve(self, parent, goal):
        # Follow predecessors back to the root, then put the route in travel order.
        state = goal
        while state is not None:
            self.path.append(state)
            state = parent[state]
        self.path.reverse()
        self.status = "found"
        return self

