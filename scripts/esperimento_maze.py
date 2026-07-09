#!/usr/bin/env python3
"""Caso peggiore topologico: labirinto serpentino connesso (Relazione, §5.4 — spec, diapositiva
8: barre disposte "in modo da formare un labirinto").

A differenza delle campagne precedenti (ostacoli sparsi o a barre con varchi casuali), il
labirinto serpentino (GridGenerator.generate_maze) forza un'unica catena di landmark lunga e
tortuosa: la connessione è garantita per costruzione (si veda tests/test_generator.py), quindi
non serve alcun controllo preliminare di raggiungibilità per interpretare il risultato.

Produce results/maze_results.json, results/9_maze.png (confronto tempi/chiamate) e
results/maze_cammino.png (visualizzazione del cammino risolto).
"""
import json
import os
import time

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from src.grid import Grid
from src.generator import GridGenerator
from src.camminomin import camminomin, reconstruct_path
from src.visualization import save_grid_image
from src.plot_style import apply_style, COLOR_DEBOLE, COLOR_FORTE

apply_style()

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")
SIZE = 30
CORRIDOR_WIDTH = 3
TIMEOUT = 60.0


def _esegui(origin, dest, grid_state, forte: bool):
    stats: dict[str, int] = {}
    start = time.time()
    min_len, landmarks, timed_out = camminomin(
        origin, dest, grid_state.copy(), stats=stats,
        use_strong_pruning=forte, start_time=start, timeout=TIMEOUT
    )
    elapsed = time.time() - start
    return {
        "potatura_forte": forte,
        "tempo_s": elapsed,
        "lunghezza": min_len,
        "chiamate_ricorsive": stats.get("recursive_calls", 0),
        "celle_frontiera": stats.get("frontier_cells", 0),
        "max_depth": stats.get("max_depth", 0),
        "tempo_limite_raggiunto": timed_out
    }, landmarks


def main() -> None:
    grid = Grid(SIZE, SIZE)
    GridGenerator.generate_maze(grid, corridor_width=CORRIDOR_WIDTH)
    grid.types = ["maze"]

    origin, dest = (0, 0), (SIZE - 1, SIZE - 1)
    grid.clear_cell(*origin)
    grid.clear_cell(*dest)

    corse = []
    ultimo_landmarks = None
    for forte in (False, True):
        esito, landmarks = _esegui(origin, dest, grid.state, forte)
        corse.append(esito)
        if forte:
            ultimo_landmarks = landmarks

    esito_completo = {
        "size": SIZE,
        "corridor_width": CORRIDOR_WIDTH,
        "corse": corse
    }
    out_path = os.path.join(RESULTS_DIR, "maze_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(esito_completo, f, indent=2, default=str, ensure_ascii=False)

    for c in corse:
        print(
            f"potatura={'forte' if c['potatura_forte'] else 'debole':6s} "
            f"tempo={c['tempo_s']:.4f}s lunghezza={c['lunghezza']:.4f} "
            f"chiamate={c['chiamate_ricorsive']} profondita_max={c['max_depth']} "
            f"limite_raggiunto={c['tempo_limite_raggiunto']}"
        )

    # Figura 1: confronto a barre debole vs forte
    fig, ax = plt.subplots(figsize=(6.5, 5))
    nomi = ["debole (riga 16)", "forte (riga 17)"]
    valori = [max(1, c["chiamate_ricorsive"]) for c in corse]
    ax.bar(nomi, valori, color=[COLOR_DEBOLE, COLOR_FORTE])
    ax.set_yscale("log")
    ax.set_ylabel("Invocazioni ricorsive (scala log)")
    ax.set_title(f"Labirinto serpentino {SIZE}x{SIZE}: potatura debole vs forte")
    ax.grid(True, which="both", linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, "9_maze.png"), dpi=200)
    plt.close()

    # Figura 2: cammino risolto sul labirinto, se ricostruibile
    if ultimo_landmarks and corse[1]["lunghezza"] < float("inf"):
        path = reconstruct_path(ultimo_landmarks, grid.state)
        save_grid_image(
            grid, os.path.join(RESULTS_DIR, "maze_cammino.png"),
            origin=origin, dest=dest, path=path, landmarks=ultimo_landmarks,
            title=f"Labirinto serpentino {SIZE}x{SIZE} — cammino minimo (potatura forte)"
        )

    print(f"\nSalvati: results/maze_results.json, results/9_maze.png, results/maze_cammino.png")


if __name__ == "__main__":
    main()
