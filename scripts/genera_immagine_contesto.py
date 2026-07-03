#!/usr/bin/env python3
"""Genera la figura illustrativa di contesto/complemento/frontiera per la Relazione (Compito 2)."""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.grid import Grid
from src.free_paths import compute_context_rays, compute_complement_rays, compute_frontier

# Griglia dimostrativa 15x15 con un ostacolo che spezza un quadrante,
# analoga per struttura all'esempio delle diapositive 18/20/24/25 della traccia.
grid = Grid(15, 15)
for r, c in [(4, 9), (5, 9), (6, 9), (6, 10), (6, 11), (9, 4), (10, 4), (10, 5)]:
    grid.set_obstacle(r, c)

origin = (7, 7)
context = compute_context_rays(origin, grid.state)
complement = compute_complement_rays(origin, grid.state, context)
frontier = compute_frontier(context, complement, grid.state)
closure = context | complement


def cast_ray(origin, direction, grid_state):
    """Ritorna la cella libera più lontana raggiunta da un raggio, per la sola visualizzazione."""
    dr, dc = direction
    r, c = origin
    rows, cols = grid_state.shape
    end = origin
    while True:
        r, c = r + dr, c + dc
        if not (0 <= r < rows and 0 <= c < cols) or grid_state[r, c] > 0:
            break
        end = (r, c)
    return end


# Gli 8 raggi primari (4 cardinali + 4 diagonali) proiettati dall'origine: sono il passo
# geometrico esplicito che l'algoritmo di ray-casting esegue prima delle espansioni a gomito
# che riempiono il resto di contesto e complemento (già visibili come colore pieno).
direzioni = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (-1, -1), (1, -1), (1, 1)]
raggi = [(origin, cast_ray(origin, d, grid.state)) for d in direzioni]

fig, axes = plt.subplots(1, 2, figsize=(13, 6.2))

for ax, mostra_frontiera in zip(axes, [False, True]):
    ax.set_xlim(-0.5, grid.cols - 0.5)
    ax.set_ylim(grid.rows - 0.5, -0.5)
    ax.set_xticks(range(grid.cols))
    ax.set_yticks(range(grid.rows))
    ax.grid(True, linestyle="--", alpha=0.4, zorder=0)

    for r in range(grid.rows):
        for c in range(grid.cols):
            cell = (r, c)
            if grid.state[r, c] == 1:
                colore = "#2d3436"
            elif cell in context:
                colore = "#2ed573"
            elif cell in complement:
                colore = "#ffb545"
            else:
                colore = "#ffffff"
            ax.add_patch(plt.Rectangle((c - 0.5, r - 0.5), 1, 1, facecolor=colore, edgecolor="#dfe6e9", zorder=1))

    if mostra_frontiera:
        for (r, c), _tipo in frontier:
            ax.add_patch(plt.Circle((c, r), 0.32, facecolor="none", edgecolor="#d63031", linewidth=2.2, zorder=3))
        ax.set_title("Frontiera della chiusura di $O$", fontsize=12, fontweight="bold")
    else:
        for (r0, c0), (r1, c1) in raggi:
            ax.annotate(
                "", xy=(c1, r1), xytext=(c0, r0),
                arrowprops=dict(arrowstyle="->", color="#0652DD", linewidth=1.6, alpha=0.85),
                zorder=3
            )
        ax.set_title("Contesto (verde), complemento (arancio) e raggi primari da $O$", fontsize=12, fontweight="bold")

    ax.scatter(*origin[::-1], marker="o", s=180, facecolor="#0984e3", edgecolor="black", zorder=4)
    ax.text(origin[1], origin[0], "O", color="white", fontsize=10, fontweight="bold", ha="center", va="center", zorder=5)
    ax.set_aspect("equal")

plt.tight_layout()
out_path = os.path.join(os.path.dirname(__file__), "..", "Relazione", "images", "contesto_complemento_frontiera.png")
plt.savefig(out_path, dpi=200, bbox_inches="tight")
plt.close()
print(f"Salvata: {out_path}")
