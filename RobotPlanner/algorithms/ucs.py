"""Uniform-cost search (Dijkstra's algorithm) over a Grid."""
from heapq import heappop, heappush
from itertools import count
from metrics import Result


def ucs(grid):
    result = Result()
    order = count()
    heap = [(0, next(order), grid.start)]
    result.pushed(1)
    best_cost = {grid.start: 0}
    parent = {grid.start: None}
    while heap:
        cost, _, state = heappop(heap)
        if cost != best_cost[state]:  # A cheaper entry replaced this one.
            continue
        if state == grid.goal:
            return result.solve(parent, state)
        result.expand(state)
        for child in grid.neighbors(state):
            new_cost = cost + grid.step_cost(state, child)
            if new_cost < best_cost.get(child, float("inf")):
                best_cost[child] = new_cost
                parent[child] = state
                heappush(heap, (new_cost, next(order), child))
                result.pushed(len(heap))
    return result

