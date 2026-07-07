#!/usr/bin/env python3
"""Genera la figura del cammino libero di tipo 1 vs tipo 2 per la Relazione (Compito 2)."""
import os

from src.grid import Grid
from src.free_paths import free_path_type1, free_path_type2
from _common import plt

ROWS, COLS = 10, 13
grid = Grid(ROWS, COLS)

origin = (1, 1)
dest = (6, 10)

path1 = free_path_type1(origin, dest, grid.state)
path2 = free_path_type2(origin, dest, grid.state)

# Ostacoli puramente decorativi, verificati per non ricadere su nessuno dei due cammini.
occupate = set(path1) | set(path2)
for r, c in [(0, 12), (9, 0), (8, 12), (0, 0)]:
    if (r, c) not in occupate:
        grid.set_obstacle(r, c)

fig, ax = plt.subplots(figsize=(8, 6.2))
for r in range(ROWS):
    for c in range(COLS):
        colore = "#2d3436" if grid.state[r, c] == 1 else "#ffffff"
        ax.add_patch(plt.Rectangle((c - 0.5, r - 0.5), 1, 1, facecolor=colore, edgecolor="#dfe6e9", linewidth=0.5, zorder=1))

cols1 = [c for _, c in path1]
rows1 = [r for r, _ in path1]
cols2 = [c for _, c in path2]
rows2 = [r for r, _ in path2]

ax.plot(cols1, rows1, color="#0984e3", linewidth=4, alpha=0.85, solid_capstyle="round", zorder=2, label="Tipo 1 (diagonale poi cardinale)")
ax.plot(cols2, rows2, color="#c0392b", linewidth=2.5, linestyle="--", zorder=3, label="Tipo 2 (cardinale poi diagonale)")

ax.scatter(*origin[::-1], marker="o", s=200, facecolor="#2ed573", edgecolor="black", zorder=4)
ax.text(origin[1], origin[0], "O", color="black", fontsize=10, fontweight="bold", ha="center", va="center", zorder=5)
ax.scatter(*dest[::-1], marker="o", s=200, facecolor="#ff4757", edgecolor="black", zorder=4)
ax.text(dest[1], dest[0], "D", color="white", fontsize=10, fontweight="bold", ha="center", va="center", zorder=5)

ax.set_xlim(-0.5, COLS - 0.5)
ax.set_ylim(ROWS - 0.5, -0.5)
ax.set_xticks(range(COLS))
ax.set_yticks(range(ROWS))
ax.set_aspect("equal")
ax.set_title("Cammino libero di tipo 1 e di tipo 2 fra $O$ e $D$", fontsize=12, fontweight="bold")
ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.18), ncol=2, fontsize=9)

plt.tight_layout()
out_path = os.path.join(os.path.dirname(__file__), "..", "Relazione", "images", "cammini_liberi_tipo1_tipo2.png")
plt.savefig(out_path, dpi=200, bbox_inches="tight")
plt.close()
print(f"Salvata: {out_path}")
