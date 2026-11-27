"""Run comparable trials and write the measurements used by the figures."""
import argparse
import csv
import json
import platform
from pathlib import Path
from statistics import median
from time import perf_counter_ns

from algorithms import SEARCHES
from problem import maps


# Time one algorithm several times to reduce single-run timing noise.
def measure(grid, search, repeats):
    times = []
    # The grid and algorithm stay the same across repeated trials.
    for _ in range(repeats):
        start = perf_counter_ns()
        result = search(grid)
        times.append((perf_counter_ns() - start) / 1_000_000)
    # Validation, serialization and plotting are outside the timing window.
    return dict(found=result.status == "found", status=result.status, path=result.path,
                cost=grid.path_cost(result.path) if result.path else None,
                generated=result.generated, expanded=result.expanded,
                peak=result.peak, median_ms=median(times), trials_ms=times,
                explored=sorted(result.explored))


# Run every algorithm on every map and save one set of result files.
def run(output, repeats, renderer):
    # Create the destination folder if it does not exist yet.
    output.mkdir(parents=True, exist_ok=True)
    fields = ["map", "algorithm", "found", "status", "cost", "generated", "expanded", "peak", "median_ms"]
    # CSV contains compact metrics, while JSON also stores explored cells.
    with (output / "summary.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for name, grid in maps().items():
            records = {}
            # Use the same Grid object to compare all four algorithms fairly.
            for label, search in SEARCHES.items():
                record = measure(grid, search, repeats)
                records[label] = record
                row = dict(record, map=name, algorithm=label)
                writer.writerow({key: row[key] for key in fields})
                print(name, label, record["status"], "cost", record["cost"],
                      "expanded", record["expanded"], "ms", round(record["median_ms"], 3))
            # Keep system/version and full algorithm results for reproducibility.
            payload = dict(python=platform.python_version(), platform=platform.platform(),
                           repeats=repeats, grid=dict(rows=grid.rows, cols=grid.cols,
                           walls=sorted(grid.walls), start=grid.start, goal=grid.goal),
                           algorithms=records)
            (output / f"{name}.json").write_text(json.dumps(payload), encoding="utf-8")
            # PDF figures are optional, so search can run without drawing packages.
            if renderer != "none":
                from visualize import plot
                plot(grid, records, name, output, renderer)


# Parse command-line options only when main.py is executed directly.
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("results"))
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--renderer", choices=["auto", "matplotlib", "pdf", "none"], default="auto")
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error("--repeats must be positive")
    run(args.out, args.repeats, args.renderer)

