"""
Member 3 – Task 8: Tests for visualize.py

Verifies that draw_grid and plot() produce valid output for every algorithm
on all three maps using the Matplotlib renderer (no network required).
"""

import sys
import os
import pathlib
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from algorithms import SEARCHES
from main import measure
from problem import maps
from visualize import MatplotlibPage, draw_grid, plot


def _make_records(grid, repeats=1):
    """Run all searches on grid and return a records dict like main.run()."""
    return {label: measure(grid, search, repeats) for label, search in SEARCHES.items()}


class DrawGridTests(unittest.TestCase):
    """Unit-level tests for draw_grid() – checks it doesn't crash and
    correctly places boxes for the start, goal and explored cells."""

    def _blank_page(self):
        return MatplotlibPage(640, 620)

    def test_draw_grid_found_path(self):
        """draw_grid must not raise for a solvable map."""
        grid = maps()["detour"]
        record = measure(grid, SEARCHES["BFS"], 1)
        page = self._blank_page()
        draw_grid(page, grid, record, 25, 86)   # should not raise

    def test_draw_grid_unreachable(self):
        """draw_grid must not raise when the goal is unreachable (empty path)."""
        grid = maps()["blocked"]
        record = measure(grid, SEARCHES["BFS"], 1)
        self.assertEqual(record["path"], [], "BFS on blocked map should return empty path")
        page = self._blank_page()
        draw_grid(page, grid, record, 25, 86)   # should not raise

    def test_draw_grid_all_algorithms(self):
        """draw_grid must work for every algorithm's output."""
        grid = maps()["detour"]
        for label, search in SEARCHES.items():
            with self.subTest(algorithm=label):
                record = measure(grid, search, 1)
                page = self._blank_page()
                draw_grid(page, grid, record, 0, 0)   # should not raise

    def test_draw_grid_explored_excludes_walls(self):
        """The explored set passed to draw_grid should never overlap walls."""
        grid = maps()["main"]
        for label, search in SEARCHES.items():
            with self.subTest(algorithm=label):
                record = measure(grid, search, 1)
                explored_set = set(map(tuple, record["explored"]))
                self.assertTrue(explored_set.isdisjoint(grid.walls),
                                f"{label}: explored set contains a wall cell")

    def test_draw_grid_path_endpoints(self):
        """When a path exists its first and last cell must be start and goal."""
        grid = maps()["detour"]
        for label, search in SEARCHES.items():
            with self.subTest(algorithm=label):
                record = measure(grid, search, 1)
                path = record["path"]
                if path:
                    self.assertEqual(tuple(path[0]), grid.start,
                                     f"{label}: path does not start at start")
                    self.assertEqual(tuple(path[-1]), grid.goal,
                                     f"{label}: path does not end at goal")


class PlotOutputTests(unittest.TestCase):
    """Integration tests for plot() – verifies the two output PDFs are created
    and have non-trivial file sizes for every map."""

    def setUp(self):
        self.out = pathlib.Path(tempfile.mkdtemp())

    def _run_plot(self, map_name):
        grid = maps()[map_name]
        records = _make_records(grid)
        plot(grid, records, map_name, self.out, renderer="matplotlib")
        return map_name

    def test_plot_produces_two_files_detour(self):
        """plot() must write both _paths and _comparison PDFs for detour."""
        self._run_plot("detour")
        paths_pdf = self.out / "detour_paths.pdf"
        comp_pdf  = self.out / "detour_comparison.pdf"
        self.assertTrue(paths_pdf.exists(),   "detour_paths.pdf not created")
        self.assertTrue(comp_pdf.exists(),    "detour_comparison.pdf not created")
        self.assertGreater(paths_pdf.stat().st_size, 1024,
                           "detour_paths.pdf is suspiciously small")
        self.assertGreater(comp_pdf.stat().st_size, 1024,
                           "detour_comparison.pdf is suspiciously small")

    def test_plot_produces_two_files_blocked(self):
        """plot() must handle the unreachable (blocked) map without crashing."""
        self._run_plot("blocked")
        self.assertTrue((self.out / "blocked_paths.pdf").exists())
        self.assertTrue((self.out / "blocked_comparison.pdf").exists())

    def test_plot_produces_two_files_main(self):
        """plot() must work on the full 40×40 main map."""
        self._run_plot("main")
        self.assertTrue((self.out / "main_paths.pdf").exists())
        self.assertTrue((self.out / "main_comparison.pdf").exists())

    def test_plot_all_maps_summary(self):
        """Running plot() for all three maps must produce exactly 6 PDF files."""
        for name in ["main", "detour", "blocked"]:
            grid = maps()[name]
            records = _make_records(grid)
            plot(grid, records, name, self.out, renderer="matplotlib")
        pdfs = sorted(p.name for p in self.out.glob("*.pdf"))
        self.assertEqual(len(pdfs), 6, f"Expected 6 PDFs, got {pdfs}")

    def test_plot_minimal_record_no_crash(self):
        """plot() must not crash when records lack optional timing keys.

        A caller that builds a minimal record (only explored/path/cost) should
        not get a KeyError – the .get() defensive fix covers this.
        """
        grid = maps()["detour"]
        result = SEARCHES["BFS"](grid)
        minimal = {
            "BFS": {
                "explored": sorted(result.explored),
                "path": result.path,
                "cost": len(result.path) - 1 if result.path else None,
            }
        }
        # Should not raise KeyError for missing median_ms/expanded/peak
        plot(grid, minimal, "detour", self.out, renderer="matplotlib")


class MatplotlibPageTests(unittest.TestCase):
    """Smoke-tests for the MatplotlibPage drawing backend."""

    def test_matplotlibpage_save(self):
        """MatplotlibPage.save() must write a non-empty file."""
        out = pathlib.Path(tempfile.mkdtemp()) / "smoke.pdf"
        page = MatplotlibPage(200, 200)
        page.box(10, 10, 50, 50, "#FF0000")
        page.line(0, 0, 100, 100, "#0000FF", 2)
        page.text(10, 100, "hello", 12)
        page.save(out)
        self.assertTrue(out.exists())
        self.assertGreater(out.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
