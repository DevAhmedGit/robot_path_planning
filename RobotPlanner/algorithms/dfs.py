"""Depth-first search over a Grid (graph version; cycle suppression via parent dict)."""
from metrics import Result


def dfs(grid):
    result = Result()
    stack = [grid.start]
    result.pushed(1)
    parent = {grid.start: None}
    while stack:
        state = stack.pop()
        if state == grid.goal:
            return result.solve(parent, state)
        result.expand(state)
        # Push in reverse so Up has first priority when popped.
        for child in reversed(list(grid.neighbors(state))):
            if child not in parent:
                parent[child] = state
                stack.append(child)
                result.pushed(len(stack))
    return result

