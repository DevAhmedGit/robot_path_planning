"""Draw identical map and chart layouts on a Matplotlib or ReportLab canvas."""

INK = "#183447"
FREE = "#F1F4F5"
SEEN = "#A0D8DB"
ROUTE = "#D85B19"
START = "#186739"
GOAL = "#743897"


class MatplotlibPage:
    def __init__(self, w, h):
        from matplotlib.figure import Figure
        from matplotlib.patches import Rectangle
        self.rectangle = Rectangle
        self.fig = Figure(figsize=(w / 75, h / 75))
        self.ax = self.fig.add_axes([0, 0, 1, 1], xlim=(0, w), ylim=(h, 0))
        self.ax.set_axis_off()

    def box(self, x, y, w, h, color):
        self.ax.add_patch(self.rectangle((x, y), w, h, color=color, linewidth=0,
                                         zorder=3 if color in (START, GOAL) else 1))

    def line(self, x, y, xx, yy, color, width):
        self.ax.plot([x, xx], [y, yy], color=color, linewidth=width, solid_capstyle="round")

    def text(self, x, y, value, size=11, color=INK):
        self.ax.text(x, y, value, fontsize=size, color=color, va="baseline")

    def save(self, path):
        self.fig.savefig(path)
        self.fig.clear()


class PdfPage:
    def __init__(self, w, h):
        from io import BytesIO
        from reportlab.pdfgen.canvas import Canvas
        self.buffer = BytesIO()
        self.h = h
        self.canvas = Canvas(self.buffer, pagesize=(w, h))

    def box(self, x, y, w, h, color):
        c = self.canvas
        c.setFillColor(color)
        c.rect(x, self.h - y - h, w, h, stroke=0, fill=1)

    def line(self, x, y, xx, yy, color, width):
        c = self.canvas
        c.setStrokeColor(color)
        c.setLineWidth(width)
        c.setLineCap(1)
        c.line(x, self.h - y, xx, self.h - yy)

    def text(self, x, y, value, size=11, color=INK):
        self.canvas.setFillColor(color)
        self.canvas.setFont("Helvetica", size)
        self.canvas.drawString(x, self.h - y, str(value))

    def save(self, path):
        self.canvas.save()
        path.write_bytes(self.buffer.getvalue())


def draw_grid(page, grid, record, x, y):
    """Paint one algorithm's result onto *page* at canvas offset (x, y).

    Parameters
    ----------
    page  : MatplotlibPage or PdfPage
    grid  : Grid  – supplies wall positions, start, goal and dimensions
    record: dict  – must contain ``"explored"`` (iterable of (row, col)),
                    ``"path"`` (list of (row, col) in travel order)
    x, y  : float – top-left canvas origin for this panel (pixels)
    """
    unit = min(220 / grid.rows, 265 / grid.cols)
    page.box(x, y, unit * grid.cols, unit * grid.rows, FREE)
    for cells, color in [(grid.walls, INK), (record["explored"], SEEN)]:
        for r, c in cells:
            page.box(x + c * unit, y + r * unit, unit, unit, color)
    route = record["path"]
    for (r, c), (rr, cc) in zip(route, route[1:]):
        page.line(x + (c + .5) * unit, y + (r + .5) * unit,
                  x + (cc + .5) * unit, y + (rr + .5) * unit, ROUTE, min(3, unit * .5))
    for (r, c), color in [(grid.start, START), (grid.goal, GOAL)]:
        page.box(x + c * unit, y + r * unit, unit, unit, color)


def plot(grid, records, name, output, renderer="auto"):
    """Render two figures for one map and write them to *output*.

    Figure 1 – ``<name>_paths.pdf``
        A 2×2 panel showing, for each algorithm, the explored-cell heat-map
        (blue) overlaid with the final path (orange) and start/goal markers.

    Figure 2 – ``<name>_comparison.pdf``
        Four horizontal bar charts comparing median time, path cost,
        expansion events and peak frontier size across all algorithms.

    Parameters
    ----------
    grid     : Grid
    records  : dict[str, dict]  – keyed by algorithm label; each value is the
               dict returned by ``main.measure()`` and must contain at least:
               ``explored``, ``path``, ``cost``, ``median_ms``, ``expanded``,
               ``peak``.
    name     : str   – map name used in titles and output file stems
    output   : Path  – directory that receives the two PDF files
    renderer : str   – ``"auto"`` (prefer matplotlib), ``"matplotlib"``,
               ``"pdf"`` (ReportLab), or ``"none"`` (skip; not handled here)
    """
    factory = PdfPage
    if renderer in ("auto", "matplotlib"):
        try:
            from matplotlib.figure import Figure
        except ModuleNotFoundError as exc:
            if renderer == "matplotlib" or exc.name != "matplotlib":
                raise
        else:
            factory = MatplotlibPage
    page = factory(640, 620)
    page.text(25, 29, f"Search on the {name} map", 22)
    for i, (label, color) in enumerate([("Free", FREE), ("Wall", INK), ("Expanded", SEEN),
                                        ("Route", ROUTE), ("Start", START), ("Goal", GOAL)]):
        page.box(25 + i * 99, 44, 10, 10, color)
        page.text(39 + i * 99, 53, label)
    for i, (label, record) in enumerate(records.items()):
        x, y = 25 + i % 2 * 313, 86 + i // 2 * 264
        cost = record["cost"]
        page.text(x, y, f"{label}  /  " + (f"{cost} steps" if cost is not None else "unreachable"), 14)
        draw_grid(page, grid, record, x, y + 8)
    page.save(output / f"{name}_paths.pdf")

    page = factory(640, 450)
    page.text(25, 33, f"Search measurements on the {name} map", 21)
    for i, (key, title) in enumerate([("median_ms", "Median time (ms)"), ("cost", "Path cost (units)"),
                                       ("expanded", "Expansion events"), ("peak", "Peak pending entries")]):
        x, y = 25 + i % 2 * 312, 78 + i // 2 * 185
        page.text(x, y, title, 15)
        values = [r.get(key) for r in records.values() if r.get(key) is not None]
        scale = max(values, default=1) or 1
        for j, (label, record) in enumerate(records.items()):
            value = record.get(key)
            yy = y + 27 + j * 30
            page.text(x, yy, label)
            if value is None:
                page.text(x + 38, yy, "No solution")
            else:
                width = 155 * value / scale
                page.box(x + 36, yy - 10, width, 11, "#267B83")
                number = f"{value:.3f}" if key == "median_ms" else str(value)
                page.text(x + 40 + width, yy, number, 10)
    page.save(output / f"{name}_comparison.pdf")

