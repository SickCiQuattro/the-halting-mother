#!/usr/bin/env python3
"""Effetto dell'innesco goloso del limite superiore globale (Relazione, Compito 3).

Confronta chiamate ricorsive e tempo con e senza `greedy_seed=True`, per la potatura debole
e per quella forte, su tre istanze di difficoltà crescente: la stessa griglia 18x18 usata per
la figura di esplorazione della potatura, la griglia 40x40 dell'esempio di cammino complesso
e una griglia 100x100 (stessa usata da `verifica_potatura_100.py`).
"""
import os
import sys
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.grid import Grid
from src.generator import GridGenerator
from src.camminomin import camminomin

ISTANZE = [
    ("18x18 cluster", GridGenerator.generate_grid(18, 18, ["cluster"], density=0.2, seed=2026), (0, 0), (17, 17), 30.0),
    ("40x40 misto", Grid.load(os.path.join(os.path.dirname(__file__), "..", "grids", "grid_report_esempio.json")), (0, 0), (39, 39), 30.0),
    ("100x100 cluster", GridGenerator.generate_grid(100, 100, ["cluster"], density=0.2, seed=2026), (0, 0), (99, 99), 60.0),
]

if __name__ == "__main__":
    for nome_istanza, grid, origin, dest, timeout in ISTANZE:
        grid.clear_cell(*origin)
        grid.clear_cell(*dest)
        print(f"--- {nome_istanza} ---")
        for nome_potatura, forte in [("debole", False), ("forte", True)]:
            for nome_seed, seed in [("senza innesco", False), ("con innesco", True)]:
                stats: dict[str, int] = {}
                start = time.time()
                min_len, _landmarks, timed_out = camminomin(
                    origin, dest, grid.state.copy(), stats=stats,
                    use_strong_pruning=forte, greedy_seed=seed,
                    start_time=start, timeout=timeout
                )
                elapsed = time.time() - start
                print(
                    f"  potatura={nome_potatura:6s} {nome_seed:14s} "
                    f"tempo={elapsed:.4f}s chiamate_ricorsive={stats.get('recursive_calls')} "
                    f"lunghezza={min_len} tempo_limite_raggiunto={timed_out}"
                )
