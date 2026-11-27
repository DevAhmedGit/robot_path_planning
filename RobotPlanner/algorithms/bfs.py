"""Breadth-first search over a Grid."""
from collections import deque
from metrics import Result


def bfs(grid):
    result = Result()
    queue = deque([grid.start])
    result.pushed(1)
    parent = {grid.start: None}
    while queue:
        state = queue.popleft()
        if state == grid.goal:
            return result.solve(parent, state)
        result.expand(state)
        for child in grid.neighbors(state):
            if child not in parent:  # Mark on enqueue to avoid duplicate pending entries.
                parent[child] = state
                queue.append(child)
                result.pushed(len(queue))
    return result

