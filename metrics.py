import time
from dataclasses import dataclass, field


@dataclass
class Result:
    algorithm: str
    solved: bool = False
    path: list = field(default_factory=list)
    actions: list = field(default_factory=list)
    cost: float = float("inf")
    generated: int = 0
    expanded: int = 0
    max_frontier: int = 0
    time_sec: float = 0.0
    explored: set = field(default_factory=set)


def reconstruct(parents, goal_state):
    states, actions = [], []
    s = goal_state
    while parents[s] is not None:
        parent, action = parents[s]
        states.append(s)
        actions.append(action)
        s = parent
    states.append(s)
    states.reverse()
    actions.reverse()
    return states, actions


def run(algo, problem):
    t0 = time.perf_counter()
    result = algo(problem)
    result.time_sec = time.perf_counter() - t0
    return result


def print_table(results):
    header = f"{'Algorithm':<10}{'Solved':<8}{'Cost':>8}{'Generated':>12}{'Expanded':>10}{'MaxFrontier':>13}{'Time(s)':>10}"
    print(header)
    print("-" * len(header))
    for r in results:
        cost = r.cost if r.solved else "-"
        print(f"{r.algorithm:<10}{str(r.solved):<8}{cost:>8}{r.generated:>12}{r.expanded:>10}{r.max_frontier:>13}{r.time_sec:>10.4f}")