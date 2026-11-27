import itertools
import unittest

from algorithms import SEARCHES, ids, ucs
from problem import Grid, maps


def reference_distances(grid):
    """Independent unit-cost oracle: relax edges in repeated full-grid sweeps."""
    dist = {grid.start: 0}
    changed = True
    while changed:
        changed = False
        for r in range(grid.rows):
            for c in range(grid.cols):
                if (r, c) in grid.walls:
                    continue
                # Only known in-bounds free cells can appear in dist.
                for adjacent in [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]:
                    if adjacent in dist and dist[adjacent] + 1 < dist.get((r, c), float("inf")):
                        dist[r, c] = dist[adjacent] + 1
                        changed = True
    return dist


class SearchTests(unittest.TestCase):
    def check_map(self, grid):
        optimum = reference_distances(grid).get(grid.goal)
        for label, search in SEARCHES.items():
            with self.subTest(algorithm=label, size=grid.size):
                result = search(grid)
                self.assertEqual(result.status, "unreachable" if optimum is None else "found")
                self.assertTrue(result.explored.isdisjoint(grid.walls))
                self.assertGreaterEqual(result.generated, result.expanded)
                if optimum is None:
                    self.assertEqual(result.path, [])
                    continue
                path = result.path
                self.assertEqual((path[0], path[-1]), (grid.start, grid.goal))
                self.assertEqual(len(path), len(set(path)))
                for r, c in path:
                    self.assertTrue(0 <= r < grid.rows and 0 <= c < grid.cols)
                    self.assertNotIn((r, c), grid.walls)
                for (r, c), (rr, cc) in zip(path, path[1:]):
                    self.assertEqual(abs(r-rr) + abs(c-cc), 1)
                self.assertEqual(grid.path_cost(path), len(path) - 1)
                if label != "DFS":
                    self.assertEqual(len(path) - 1, optimum)

    def test_main_and_connected_size(self):
        grid = maps()["main"]
        self.assertEqual(len(reference_distances(grid)), grid.size)
        self.assertEqual(grid.size, 1372)
        self.check_map(grid)

    def test_detour_and_sealed_door(self):
        for name in ["detour", "blocked"]:
            self.check_map(maps()[name])

    def test_all_three_by_three_layouts(self):
        cells = sorted(set(itertools.product(range(3), repeat=2)) - {(0, 0), (2, 2)})
        for mask in range(1 << len(cells)):
            walls = frozenset(cell for i, cell in enumerate(cells) if mask & (1 << i))
            self.check_map(Grid(3, 3, walls, (0, 0), (2, 2)))

    def test_start_is_goal(self):
        for search in SEARCHES.values():
            result = search(Grid(1, 1, frozenset(), (0, 0), (0, 0)))
            self.assertEqual((result.path, result.generated, result.expanded, result.peak),
                             ([(0, 0)], 1, 0, 1))

    def test_ids_limit_boundary(self):
        grid = maps()["detour"]
        for limit in (0, 13):
            result = ids(grid, limit)
            self.assertEqual((result.status, result.path), ("cutoff", []))
        self.assertEqual(grid.path_cost(ids(grid, 14).path), 14)
        with self.assertRaises(ValueError):
            ids(grid, -1)

    def test_counting_convention(self):
        grid = Grid(1, 2, frozenset(), (0, 0), (0, 1))
        for label, search in SEARCHES.items():
            result = search(grid)
            self.assertEqual(result.generated, 3 if label == "IDS" else 2)
            self.assertEqual((result.expanded, result.peak), (1, 1))
            self.assertEqual(result.explored, {(0, 0)})

    def test_weighted_ucs_improves_goal_before_pop(self):
        class TollGrid(Grid):
            def step_cost(self, p, q):
                return 10 if {p, q} == {(0, 0), (0, 1)} else 1
        grid = TollGrid(2, 2, frozenset(), (0, 0), (0, 1))
        self.assertEqual(grid.path_cost(ucs(grid).path), 3)
        self.assertEqual(grid.path_cost(SEARCHES["BFS"](grid).path), 10)

    def test_invalid_endpoints_and_moves(self):
        with self.assertRaises(ValueError):
            Grid(2, 2, frozenset({(0, 0)}), (0, 0), (1, 1))
        with self.assertRaises(ValueError):
            maps()["main"].path_cost([(2, 2), (12, 19)])

