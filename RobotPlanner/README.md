# CSAI 301 · Robot Path Planning

Four manual graph searches navigate a static warehouse floor. Start with the main map in the Phase I report, then reproduce it with the commands below. The archived results contain the exact routes and individual trials used in the report.

## Run from the project directory

Extract the ZIP. Open a terminal in the folder containing main.py. Use Python 3.10 or newer. On Windows PowerShell:

~~~powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python main.py --renderer matplotlib --out my_run
.\.venv\Scripts\python -m unittest discover -s tests -v
~~~

On macOS or Linux, create the environment with python3 -m venv .venv and substitute .venv/bin/python for the Windows interpreter path. In an environment with dependencies already installed:

~~~sh
python main.py --out my_run
python -m unittest discover -s tests -v
~~~

Open my_run/main_paths.pdf for the maps and my_run/main_comparison.pdf for the charts. The detour and blocked maps have matching files. summary.csv contains every map and algorithm. Each map's JSON includes its walls, routes as ordered [row, column] pairs, distinct expanded cells, trial timings and runtime environment. Empty paths and null costs indicate failure. Chart panels each have their own linear scale. Figures are static and work in a PDF viewer during the demo.

The default run uses five trials per algorithm and map, tries Matplotlib first, and uses ReportLab when Matplotlib is absent. Select --renderer pdf to request ReportLab, or --renderer none to run the simulator and tests with the Python standard library alone. Change trial count with --repeats 9. The default output is results. Choose a fresh --out folder to preserve the reference measurements. Timings vary with hardware and load.

## Project files

| Entry | Purpose |
|---|---|
| problem.py | Grid, actions, step costs, route validation and the three fixed maps |
| algorithms/ | One file per search, plus the registry in __init__.py |
| metrics.py | Search result, event counters and predecessor reconstruction |
| main.py | Trials, timing, command-line options and result export |
| visualize.py | Map and comparison layouts, Matplotlib and PDF rendering |
| tests/test_search.py | Independent distance oracle, path checks and algorithm edge cases |
| tests/test_second_map.py | Explicit per-algorithm tests on the detour map (second-map validation) |
| tests/test_visualize.py | draw_grid and plot() output tests for all maps and renderers |
| results/ | Measured reference data and six figures |
| docs/ | Report, fillable contribution sheet, oral guide, timed demo and checklist |

## Extending the model

Edit maps() to define a new grid. Rows increase downward. Columns increase rightward. Both endpoints must be free. All algorithms receive the same Grid and return a Result. A future informed graph search can call neighbors and step_cost and return the same result type. Register a single-argument wrapper in SEARCHES to bind its heuristic. The four-panel layouts target Phase I; extend their layout for a nine-way comparison.

For local search, represent a candidate as a move sequence from start. Decode it using the grid rules. Score candidates by violations, final distance to goal and route length, in that order; validate a feasible winner with path_cost. Keep local-search iteration, fitness and seed histories separately, since an optimization iteration has a different meaning from a graph expansion. See the report for two heuristic choices. Document any model changes in Phase II.

## Team handoff

Read docs/Checklist.md before submission and docs/Oral_guide.md before the individual discussion. The course requires the team to implement the core algorithms. This package discloses AI-generated work. Each member must accurately establish their own implementation and contributions and confirm the permitted use of this draft with the instructor.

