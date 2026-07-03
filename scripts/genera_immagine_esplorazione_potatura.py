#!/usr/bin/env python3
"""Genera la mappa delle celle esplorate: potatura debole vs forte (Relazione, Compito 3)."""
import os
import sys
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.generator import GridGenerator
from src.camminomin import camminomin

SIZE = 18
grid = GridGenerator.generate_grid(SIZE, SIZE, ["cluster"], density=0.2, seed=2026)
origin = (0, 0)
dest = (SIZE - 1, SIZE - 1)
grid.clear_cell(*origin)
grid.clear_cell(*dest)

risultati = {}
for nome, forte in [("debole", False), ("forte", True)]:
    visited = set()
    start = time.time()
    min_len, _landmarks, timed_out = camminomin(
        origin, dest, grid.state.copy(),
        start_time=start, timeout=30.0,
        use_strong_pruning=forte,
        visited_closures=visited
    )
    elapsed = time.time() - start
    risultati[nome] = {"visited": visited, "elapsed": elapsed, "timed_out": timed_out, "min_len": min_len}
    print(f"Potatura {nome}: {len(visited)} celle esplorate, {elapsed:.3f}s, timeout={timed_out}, lunghezza={min_len}")

fig, axes = plt.subplots(1, 2, figsize=(13, 6.4))
for ax, nome, colore in zip(axes, ["debole", "forte"], ["#e74c3c", "#2ed573"]):
    dati = risultati[nome]
    for r in range(SIZE):
        for c in range(SIZE):
            if grid.state[r, c] == 1:
                fc = "#2d3436"
            elif (r, c) in dati["visited"]:
                fc = colore
            else:
                fc = "#ffffff"
            ax.add_patch(plt.Rectangle((c - 0.5, r - 0.5), 1, 1, facecolor=fc, edgecolor="#dfe6e9", linewidth=0.3, zorder=1))
    ax.scatter(*origin[::-1], marker="o", s=110, facecolor="#0984e3", edgecolor="black", zorder=4)
    ax.scatter(*dest[::-1], marker="o", s=110, facecolor="#ffd32a", edgecolor="black", zorder=4)
    ax.set_xlim(-0.5, SIZE - 0.5)
    ax.set_ylim(SIZE - 0.5, -0.5)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect("equal")
    titolo = f"Potatura {nome} (riga {'16' if nome == 'debole' else '17'})\n{len(dati['visited'])} celle esplorate, {dati['elapsed']:.3f} s"
    ax.set_title(titolo, fontsize=11, fontweight="bold")

plt.tight_layout()
out_path = os.path.join(os.path.dirname(__file__), "..", "Relazione", "images", "esplorazione_potatura_debole_vs_forte.png")
plt.savefig(out_path, dpi=200, bbox_inches="tight")
plt.close()
print(f"Salvata: {out_path}")
