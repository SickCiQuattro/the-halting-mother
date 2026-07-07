#!/usr/bin/env python3
"""Verifica empirica del limite di ricorsione di CAMMINOMIN (Relazione, Conclusioni).

Costruisce una griglia "a pettine": barriere verticali a piena altezza con un unico
varco che alterna fra il bordo superiore e quello inferiore, forzando un cammino a
zig-zag con un landmark per barriera. All'aumentare del numero di barriere, la
profondità di ricorsione cresce linearmente ma il numero di chiamate ricorsive cresce
in modo esponenziale (il ramo di frontiera scartato a ogni barriera non viene
scartato immediatamente dalla potatura, e viene comunque esplorato fino in fondo prima
del ritracciamento): il tempo limite viene quindi sempre raggiunto molto prima che la
profondità di ricorsione si avvicini al limite di Python (15000, impostato in main.py).
"""
import sys
import time
sys.setrecursionlimit(15000)

from src.grid import Grid
from src.camminomin import camminomin


def build_comb_grid(n_bars: int, rows: int = 7):
    cols = 2 * n_bars + 1
    grid = Grid(rows, cols)
    for i in range(n_bars):
        bar_col = 2 * i + 1
        gap_row = 0 if i % 2 == 0 else rows - 1
        for r in range(rows):
            if r != gap_row:
                grid.set_obstacle(r, bar_col)
    return grid, (rows // 2, 0), (rows // 2, cols - 1)


if __name__ == "__main__":
    for n_bars in [12, 14, 16, 18, 30]:
        grid, origin, dest = build_comb_grid(n_bars)
        stats: dict[str, int] = {}
        start = time.time()
        timeout = 30.0 if n_bars == 30 else 10.0
        min_len, landmarks, timed_out = camminomin(
            origin, dest, grid.state, stats=stats,
            use_strong_pruning=True, start_time=start, timeout=timeout
        )
        elapsed = time.time() - start
        print(
            f"barriere={n_bars} landmark={len(landmarks)} "
            f"chiamate_ricorsive={stats.get('recursive_calls')} "
            f"profondita_massima={stats.get('max_depth')} "
            f"tempo_limite_raggiunto={timed_out} tempo={elapsed:.3f}s"
        )
