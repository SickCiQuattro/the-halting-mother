#!/usr/bin/env python3
"""Genera la figura di apertura a 4 pannelli per l'Introduzione della Relazione."""
import os

from src.grid import Grid
from src.generator import GridGenerator
from src.free_paths import compute_context_rays, compute_complement_rays, compute_frontier
from src.camminomin import camminomin, reconstruct_path
from _common import plt

SIZE = 20
grid_vuota = Grid(SIZE, SIZE)

grid = GridGenerator.generate_grid(SIZE, SIZE, ["simple", "cluster", "bar"], density=0.18, seed=7)
origin = (0, 0)
dest = (SIZE - 1, SIZE - 1)
grid.clear_cell(*origin)
grid.clear_cell(*dest)

context = compute_context_rays(origin, grid.state)
complement = compute_complement_rays(origin, grid.state, context)
frontier = compute_frontier(context, complement, grid.state)


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


direzioni = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (-1, -1), (1, -1), (1, 1)]
raggi = [(origin, cast_ray(origin, d, grid.state)) for d in direzioni]

min_len, landmarks, _timed_out = camminomin(
    origin, dest, grid.state.copy(), start_time=None, timeout=None, use_strong_pruning=True
)
path = reconstruct_path(landmarks, grid.state) if min_len < float("inf") else []

fig, axes = plt.subplots(1, 4, figsize=(21, 5.6))


def disegna_griglia_base(ax, stato):
    for r in range(SIZE):
        for c in range(SIZE):
            colore = "#2d3436" if stato[r, c] == 1 else "#ffffff"
            ax.add_patch(plt.Rectangle((c - 0.5, r - 0.5), 1, 1, facecolor=colore, edgecolor="#dfe6e9", linewidth=0.4, zorder=1))
    ax.set_xlim(-0.5, SIZE - 0.5)
    ax.set_ylim(SIZE - 0.5, -0.5)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect("equal")


# Pannello 1: griglia vuota
disegna_griglia_base(axes[0], grid_vuota.state)
axes[0].set_title("1. Griglia vuota", fontsize=12, fontweight="bold")

# Pannello 2: griglia con ostacoli generati (Compito 1)
disegna_griglia_base(axes[1], grid.state)
axes[1].set_title("2. Ostacoli generati (Compito 1)", fontsize=12, fontweight="bold")

# Pannello 3: chiusura e raggi da O (Compito 2)
ax = axes[2]
for r in range(SIZE):
    for c in range(SIZE):
        cell = (r, c)
        if grid.state[r, c] == 1:
            colore = "#2d3436"
        elif cell in context:
            colore = "#2ed573"
        elif cell in complement:
            colore = "#ffb545"
        else:
            colore = "#ffffff"
        ax.add_patch(plt.Rectangle((c - 0.5, r - 0.5), 1, 1, facecolor=colore, edgecolor="#dfe6e9", linewidth=0.4, zorder=1))
for (r0, c0), (r1, c1) in raggi:
    ax.annotate("", xy=(c1, r1), xytext=(c0, r0), arrowprops=dict(arrowstyle="->", color="#0652DD", linewidth=1.2, alpha=0.85), zorder=3)
for (r, c), _tipo in frontier:
    ax.add_patch(plt.Circle((c, r), 0.32, facecolor="none", edgecolor="#d63031", linewidth=1.6, zorder=4))
ax.set_xlim(-0.5, SIZE - 0.5)
ax.set_ylim(SIZE - 0.5, -0.5)
ax.set_xticks([])
ax.set_yticks([])
ax.set_aspect("equal")
ax.set_title("3. Chiusura e raggi da $O$ (Compito 2)", fontsize=12, fontweight="bold")

# Pannello 4: cammino minimo risolto (Compito 3)
disegna_griglia_base(axes[3], grid.state)
if path:
    for r, c in path:
        axes[3].add_patch(plt.Rectangle((c - 0.5, r - 0.5), 1, 1, facecolor="#0984e3", alpha=0.35, edgecolor="none", zorder=2))
lm_cols = [coord[1] for coord, _ in landmarks]
lm_rows = [coord[0] for coord, _ in landmarks]
axes[3].plot(lm_cols, lm_rows, color="#0984e3", linewidth=2.5, zorder=3)
axes[3].scatter(lm_cols, lm_rows, color="#fdcb6e", edgecolor="#d63031", s=90, marker="D", zorder=4)
axes[3].set_title(f"4. Cammino minimo risolto (Compito 3)", fontsize=12, fontweight="bold")

for ax, coord, label in [(axes[2], origin, "O"), (axes[3], origin, "O"), (axes[3], dest, "D")]:
    ax.scatter(coord[1], coord[0], marker="o", s=140, facecolor="#0984e3", edgecolor="black", zorder=5)
    ax.text(coord[1], coord[0], label, color="white", fontsize=8, fontweight="bold", ha="center", va="center", zorder=6)

plt.tight_layout()
out_path = os.path.join(os.path.dirname(__file__), "..", "Relazione", "images", "panoramica_sistema.png")
plt.savefig(out_path, dpi=200, bbox_inches="tight")
plt.close()
print(f"Salvata: {out_path}")
