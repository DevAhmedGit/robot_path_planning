"""Manual graph searches with a shared Grid -> Result interface."""
from .bfs import bfs
from .dfs import dfs
from .ucs import ucs
from .ids import ids

SEARCHES = {"BFS": bfs, "DFS": dfs, "UCS": ucs, "IDS": ids}

