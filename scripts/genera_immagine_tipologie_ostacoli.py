#!/usr/bin/env python3
"""Genera il pannello delle 5 tipologie di ostacolo isolate per la Relazione (Compito 1)."""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.grid import Grid
from src.generator import GridGenerator

SIZE = 20
SEED = 42

griglie = []

g = Grid(SIZE, SIZE)
GridGenerator.generate_simple(g, density=0.15, seed=SEED)
griglie.append(("simple", g))

g = Grid(SIZE, SIZE)
GridGenerator.generate_cluster(g, num_clusters=3, min_size=5, max_size=12, seed=SEED)
griglie.append(("cluster", g))

g = Grid(SIZE, SIZE)
GridGenerator.generate_diagonal(g, count=5, seed=SEED)
griglie.append(("diagonal", g))

g = Grid(SIZE, SIZE)
GridGenerator.generate_enclosure(g, count=2, min_side=4, max_side=7, seed=SEED)
griglie.append(("enclosure", g))

g = Grid(SIZE, SIZE)
GridGenerator.generate_bar(g, count=2, thickness=1, min_len=6, max_len=12, seed=SEED)
griglie.append(("bar", g))

fig, axes = plt.subplots(1, 5, figsize=(21, 4.6))

for ax, (nome, grid) in zip(axes, griglie):
    for r in range(SIZE):
        for c in range(SIZE):
            colore = "#2d3436" if grid.state[r, c] == 1 else "#ffffff"
            ax.add_patch(plt.Rectangle((c - 0.5, r - 0.5), 1, 1, facecolor=colore, edgecolor="#dfe6e9", linewidth=0.4, zorder=1))
    ax.set_xlim(-0.5, SIZE - 0.5)
    ax.set_ylim(SIZE - 0.5, -0.5)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect("equal")
    ax.set_title(nome, fontsize=13, fontweight="bold", fontfamily="monospace")

axes[2].set_xlabel("celle unite solo per lo spigolo:\nattraversamento diagonale ammesso", fontsize=8.5, style="italic")

plt.tight_layout()
out_path = os.path.join(os.path.dirname(__file__), "..", "Relazione", "images", "tipologie_ostacoli.png")
plt.savefig(out_path, dpi=200, bbox_inches="tight")
plt.close()
print(f"Salvata: {out_path}")
