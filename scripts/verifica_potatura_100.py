#!/usr/bin/env python3
"""Confronto supplementare potatura debole/forte su una griglia 100x100 (Relazione, §5.4.2).

Non fa parte di `run_campaign` per non appesantire la Figura 10 con una terza dimensione
(taglia) oltre a tipologia di ostacolo e configurazione: usa un solo scenario rappresentativo
(`cluster`) e la sola coppia d'angolo, per verificare se il rapporto fra potatura debole e
forte osservato a 50x50 si mantiene anche a una taglia doppia.
"""
import os
import sys
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.generator import GridGenerator
from src.camminomin import camminomin

SIZE = 100
grid = GridGenerator.generate_grid(SIZE, SIZE, ["cluster"], density=0.2, seed=2026)
origin = (0, 0)
dest = (SIZE - 1, SIZE - 1)
grid.clear_cell(*origin)
grid.clear_cell(*dest)

if __name__ == "__main__":
    for nome, forte in [("debole", False), ("forte", True)]:
        stats: dict[str, int] = {}
        start = time.time()
        min_len, _landmarks, timed_out = camminomin(
            origin, dest, grid.state.copy(), stats=stats,
            use_strong_pruning=forte, start_time=start, timeout=60.0
        )
        elapsed = time.time() - start
        print(
            f"potatura={nome} tempo={elapsed:.3f}s "
            f"chiamate_ricorsive={stats.get('recursive_calls')} "
            f"lunghezza={min_len} tempo_limite_raggiunto={timed_out}"
        )
