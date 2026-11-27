"""
Member 2 – Task 9: Test all four algorithms on the 'detour' second map.

The 'detour' grid (5 × 7) has a wall column at col=3 for rows 0-3, forcing
the robot to go around the bottom before reaching the right side.

    . . . # . . .
    . . . # . . .
    . . . # . . .
    . . . # . . .
    . . . . . . .
    S=(0,0)  G=(0,6)

Expected optimal path cost: 14 steps.
DFS is not required to be optimal, but must find *a* valid path.
"""

import sys
import os
import unittest

# Allow running from the project root directly.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from algorithms import SEARCHES
from problem import maps

DETOUR = maps()["detour"]
OPTIMAL_COST = 14  # Manhattan distance forced around the wall


class SecondMapTests(unittest.TestCase):
    """Explicit per-algorithm tests on the detour map (Member 2 – Task 9)."""

    # ------------------------------------------------------------------ helpers
    def _run(self, label):
        search = SEARCHES[label]
        result = search(DETOUR)
        return result

    def _assert_valid_path(self, result, label):
        self.assertEqual(result.status, "found",
                         f"{label}: expected 'found', got '{result.status}'")
        path = result.path
        self.assertTrue(len(path) >= 2,
                        f"{label}: path too short ({len(path)} nodes)")
        self.assertEqual(path[0], DETOUR.start,
                         f"{label}: path does not begin at start")
        self.assertEqual(path[-1], DETOUR.goal,
                         f"{label}: path does not end at goal")
        # No node visited twice
        self.assertEqual(len(path), len(set(path)),
                         f"{label}: path contains duplicate nodes")
        # Every step is a legal unit move
        for (r, c), (rr, cc) in zip(path, path[1:]):
            self.assertEqual(abs(r - rr) + abs(c - cc), 1,
                             f"{label}: illegal move from ({r},{c}) to ({rr},{cc})")
        # No wall or out-of-bounds cell on the path
        for r, c in path:
            self.assertFalse((r, c) in DETOUR.walls,
                             f"{label}: path passes through wall at ({r},{c})")
            self.assertTrue(0 <= r < DETOUR.rows and 0 <= c < DETOUR.cols,
                            f"{label}: path goes out of bounds at ({r},{c})")

    # ------------------------------------------------------------------ tests
    def test_bfs_finds_optimal_path(self):
        result = self._run("BFS")
        self._assert_valid_path(result, "BFS")
        cost = DETOUR.path_cost(result.path)
        self.assertEqual(cost, OPTIMAL_COST,
                         f"BFS path cost {cost} ≠ optimal {OPTIMAL_COST}")

    def test_dfs_finds_a_valid_path(self):
        result = self._run("DFS")
        self._assert_valid_path(result, "DFS")
        # DFS is not optimal – just check it found something ≥ optimal length
        cost = DETOUR.path_cost(result.path)
        self.assertGreaterEqual(cost, OPTIMAL_COST,
                                f"DFS cost {cost} is below the theoretical minimum")

    def test_ids_finds_optimal_path(self):
        result = self._run("IDS")
        self._assert_valid_path(result, "IDS")
        cost = DETOUR.path_cost(result.path)
        self.assertEqual(cost, OPTIMAL_COST,
                         f"IDS path cost {cost} ≠ optimal {OPTIMAL_COST}")

    def test_ucs_finds_optimal_path(self):
        """UCS included for a complete four-way comparison on the second map."""
        result = self._run("UCS")
        self._assert_valid_path(result, "UCS")
        cost = DETOUR.path_cost(result.path)
        self.assertEqual(cost, OPTIMAL_COST,
                         f"UCS path cost {cost} ≠ optimal {OPTIMAL_COST}")

    def test_metrics_are_sane(self):
        """generated ≥ expanded for every algorithm; peak frontier > 0.

        IDS re-expands nodes across depth iterations by design, so its
        expanded count is allowed to exceed the number of free cells.
        BFS, DFS, and UCS each visit every node at most once.
        """
        free_cells = DETOUR.size
        single_pass = {"BFS", "DFS", "UCS"}
        for label, search in SEARCHES.items():
            with self.subTest(algorithm=label):
                result = search(DETOUR)
                if label in single_pass:
                    self.assertLessEqual(
                        result.expanded, free_cells,
                        f"{label}: expanded {result.expanded} > free cells {free_cells}")
                self.assertGreaterEqual(result.generated, result.expanded,
                                        f"{label}: generated < expanded")
                self.assertGreater(result.peak, 0,
                                   f"{label}: peak frontier size should be positive")

    def test_explored_set_excludes_walls(self):
        """No algorithm should ever expand a wall or out-of-bounds cell."""
        for label, search in SEARCHES.items():
            with self.subTest(algorithm=label):
                result = search(DETOUR)
                self.assertTrue(result.explored.isdisjoint(DETOUR.walls),
                                f"{label}: explored set contains a wall cell")

    def test_bfs_vs_ucs_agree_on_cost(self):
        """On a uniform-cost grid BFS and UCS must return the same path cost."""
        bfs_result = SEARCHES["BFS"](DETOUR)
        ucs_result = SEARCHES["UCS"](DETOUR)
        bfs_cost = DETOUR.path_cost(bfs_result.path)
        ucs_cost = DETOUR.path_cost(ucs_result.path)
        self.assertEqual(bfs_cost, ucs_cost,
                         f"BFS cost {bfs_cost} ≠ UCS cost {ucs_cost} on uniform grid")


# --------------------------------------------------------------------------- #
# Standalone runner: prints a human-readable summary table when executed       #
# directly (python tests/test_second_map.py), mimicking Task 9's intent of    #
# showing results "on a second map".                                           #
# --------------------------------------------------------------------------- #
def _print_summary():
    print(f"\n{'='*62}")
    print(f"  Second-map test  |  Grid: {DETOUR.rows}×{DETOUR.cols}"
          f"  |  Optimal cost: {OPTIMAL_COST}")
    print(f"{'='*62}")
    header = f"{'Algorithm':<10} {'Status':<12} {'Cost':<6} {'Expanded':<10} {'Generated':<11} {'Peak':<6}"
    print(header)
    print("-" * 62)
    for label, search in SEARCHES.items():
        r = search(DETOUR)
        cost = DETOUR.path_cost(r.path) if r.path else "—"
        optimal = "" if label == "DFS" else (" ✓" if cost == OPTIMAL_COST else " ✗")
        print(f"{label:<10} {r.status:<12} {str(cost):<6} {r.expanded:<10} {r.generated:<11} {r.peak:<6}{optimal}")
    print("=" * 62)
    print("  ✓ = optimal path found   (DFS not required to be optimal)")
    print()


if __name__ == "__main__":
    _print_summary()
    unittest.main(verbosity=2)
