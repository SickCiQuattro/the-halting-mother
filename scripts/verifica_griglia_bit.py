#!/usr/bin/env python3
"""Compromesso spazio/tempo della griglia a bit impacchettati (Relazione).

Confronta la matrice `uint8` (1 byte/cella) e `BitPackedGrid` (2 bit/cella) su taglie
crescenti: memoria effettiva della rappresentazione e tempo del calcolo di una chiusura
(contesto + complemento + frontiera dal centro), più un CAMMINOMIN completo su griglia
piccola. I numeri alimentano la valutazione critica del confronto di strutture dati
(pag. 63 e 72 dell'elaborato).
"""
import time

from src.generator import GridGenerator
from src.bitgrid import BitPackedGrid
from src.free_paths import compute_context_rays, compute_complement_rays, compute_frontier
from src.camminomin import camminomin

SIZES = [50, 100, 200, 400]
RIPETIZIONI = 20


def tempo_chiusura(origin, grid_state) -> float:
    start = time.perf_counter()
    for _ in range(RIPETIZIONI):
        context = compute_context_rays(origin, grid_state)
        complement = compute_complement_rays(origin, grid_state, context)
        compute_frontier(context, complement, grid_state)
    return (time.perf_counter() - start) / RIPETIZIONI


if __name__ == "__main__":
    print("--- Memoria e tempo di chiusura su taglie crescenti ---")
    for size in SIZES:
        grid = GridGenerator.generate_grid(size, size, ["simple", "cluster"], density=0.2, seed=42)
        bit_grid = BitPackedGrid.from_array(grid.state)
        centro = (size // 2, size // 2)
        grid.clear_cell(*centro)
        bit_grid[centro] = 0

        t_u8 = tempo_chiusura(centro, grid.state)
        t_bit = tempo_chiusura(centro, bit_grid)
        print(
            f"{size}x{size}: memoria uint8={grid.state.nbytes}B bit={bit_grid.nbytes}B "
            f"(rapporto {grid.state.nbytes / bit_grid.nbytes:.1f}x) | "
            f"chiusura uint8={t_u8:.5f}s bit={t_bit:.5f}s (rallentamento {t_bit / t_u8:.1f}x)"
        )

    print("\n--- CAMMINOMIN completo su griglia 20x20 ---")
    grid = GridGenerator.generate_grid(20, 20, ["simple", "cluster"], density=0.2, seed=42)
    o, d = (0, 0), (19, 19)
    grid.clear_cell(*o)
    grid.clear_cell(*d)
    bit_grid = BitPackedGrid.from_array(grid.state)

    for nome, stato in [("uint8", grid.state.copy()), ("bit", bit_grid.copy())]:
        start = time.perf_counter()
        min_len, _, _ = camminomin(o, d, stato, use_strong_pruning=True)
        print(f"camminomin {nome}: lunghezza={min_len:.6f} tempo={time.perf_counter() - start:.4f}s")
