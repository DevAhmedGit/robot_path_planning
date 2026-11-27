from metrics import Result


def depth_pass(grid, limit, result):
    """Return whether a depth boundary was encountered in this pass."""
    stack = [(grid.start, 0)]
    result.pushed(1)
    best_depth = {grid.start: 0}
    parent = {grid.start: None}
    boundary = False
    while stack:
        state, depth = stack.pop()
        if depth != best_depth[state]:
            continue
        if state == grid.goal:
            result.solve(parent, state)
            return False
        if depth == limit:
            boundary = True
            continue
        result.expand(state)
        for child in reversed(list(grid.neighbors(state))):
            # A shallower arrival leaves more moves available under this limit.
            if depth + 1 < best_depth.get(child, float("inf")):
                best_depth[child] = depth + 1
                parent[child] = state
                stack.append((child, depth + 1))
                result.pushed(len(stack))
    return boundary


def ids(grid, max_depth=None):
    if max_depth is not None and max_depth < 0:
        raise ValueError("Depth limit must be nonnegative")
    result = Result()
    # Every reachable goal has a simple path with at most V - 1 edges.
    last = grid.size - 1
    if max_depth is not None:
        last = min(last, max_depth)
    for limit in range(last + 1):
        boundary = depth_pass(grid, limit, result)
        if result.status == "found" or not boundary:
            return result
    if last < grid.size - 1:
        result.status = "cutoff"
    return result

