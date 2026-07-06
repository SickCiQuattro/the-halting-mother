#!/usr/bin/env python3
"""Effetto del controllo dei componenti connessi su una coppia irraggiungibile (Relazione).

Griglia 50x50 con ostacoli casuali (densità 0.2) più un recinto chiuso inserito manualmente:
la destinazione è all'interno del recinto, l'origine all'esterno. Confronta CAMMINOMIN con il
controllo preliminare dei componenti (esito immediato, O(R*C)) e senza (la ricerca ricorsiva
deve esaurire la frontiera, con costo potenzialmente esponenziale, o raggiungere il tempo
limite di 600 s usato nella campagna sperimentale).
"""
import os
import sys
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.generator import GridGenerator
from src.grid import compute_components
from src.camminomin import camminomin

SIZE = 50
TIMEOUT = 600.0

grid = GridGenerator.generate_grid(SIZE, SIZE, ["simple", "cluster"], density=0.2, seed=2026)

# Recinto chiuso 11x11 con destinazione interna libera
R0, C0, LATO = 20, 20, 11
for i in range(LATO):
    grid.set_obstacle(R0, C0 + i)
    grid.set_obstacle(R0 + LATO - 1, C0 + i)
    grid.set_obstacle(R0 + i, C0)
    grid.set_obstacle(R0 + i, C0 + LATO - 1)
for r in range(R0 + 1, R0 + LATO - 1):
    for c in range(C0 + 1, C0 + LATO - 1):
        grid.clear_cell(r, c)

origin = (0, 0)
dest = (25, 25)
grid.clear_cell(*origin)

if __name__ == "__main__":
    # Sanità: O e D devono stare in componenti diversi
    labels = compute_components(grid.state)
    assert labels[origin] != labels[dest], "la coppia deve essere irraggiungibile"

    start = time.time()
    compute_components(grid.state)
    print(f"solo etichettatura componenti: {time.time() - start:.6f}s")

    for nome, check in [("con controllo componenti", True), ("senza controllo", False)]:
        stats: dict[str, int] = {}
        start = time.time()
        min_len, _landmarks, timed_out = camminomin(
            origin, dest, grid.state.copy(), stats=stats,
            start_time=start, timeout=TIMEOUT,
            use_strong_pruning=True, use_component_check=check
        )
        elapsed = time.time() - start
        print(
            f"{nome}: tempo={elapsed:.6f}s lunghezza={min_len} "
            f"chiamate_ricorsive={stats.get('recursive_calls', 0)} "
            f"celle_frontiera={stats.get('frontier_cells', 0)} "
            f"tempo_limite_raggiunto={timed_out}"
        )
