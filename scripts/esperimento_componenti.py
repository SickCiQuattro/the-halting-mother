#!/usr/bin/env python3
"""Effetto del controllo delle componenti connesse su una coppia irraggiungibile (recinto 50x50).

Produce:
  - results/component_check_results.json
  - results/7_ottimizzazioni.png
"""
import json
import os
import time

import numpy as np

from _common import plt
from src.grid import compute_components
from src.generator import GridGenerator
from src.camminomin import camminomin

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")
COMPONENT_TIMEOUT = 600.0


def esperimento_component_check() -> dict[str, object]:
    size = 50
    grid = GridGenerator.generate_grid(size, size, ["simple", "cluster"], density=0.2, seed=2026)

    # Recinto chiuso 11x11 con destinazione interna libera: origine e destinazione in
    # componenti connesse diverse per costruzione.
    r0, c0, lato = 20, 20, 11
    for i in range(lato):
        grid.set_obstacle(r0, c0 + i)
        grid.set_obstacle(r0 + lato - 1, c0 + i)
        grid.set_obstacle(r0 + i, c0)
        grid.set_obstacle(r0 + i, c0 + lato - 1)
    for r in range(r0 + 1, r0 + lato - 1):
        for c in range(c0 + 1, c0 + lato - 1):
            grid.clear_cell(r, c)

    origin = (0, 0)
    dest = (25, 25)
    grid.clear_cell(*origin)

    labels = compute_components(grid.state)
    assert labels[origin] != labels[dest], "la coppia deve essere irraggiungibile per costruzione"

    start = time.time()
    compute_components(grid.state)
    tempo_etichettatura = time.time() - start

    corse = []
    for nome, check in [("con controllo componenti", True), ("senza controllo", False)]:
        stats: dict[str, int] = {}
        start = time.time()
        min_len, _landmarks, timed_out = camminomin(
            origin, dest, grid.state.copy(), stats=stats,
            start_time=start, timeout=COMPONENT_TIMEOUT,
            use_strong_pruning=True, use_component_check=check
        )
        elapsed = time.time() - start
        corse.append({
            "descrizione": nome,
            "controllo_componenti": check,
            "tempo_s": elapsed,
            "lunghezza": None if np.isinf(min_len) else min_len,
            "chiamate_ricorsive": stats.get("recursive_calls", 0),
            "celle_frontiera": stats.get("frontier_cells", 0),
            "tempo_limite_raggiunto": timed_out
        })

    return {
        "tempo_sola_etichettatura_s": tempo_etichettatura,
        "corse": corse
    }


def _plot(component_res: dict[str, object]) -> None:
    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    corse = component_res["corse"]
    ax.bar([c["descrizione"] for c in corse], [max(1, c["chiamate_ricorsive"]) for c in corse],
           color=["#2ed573", "#ff7979"])
    ax.set_yscale('log')
    ax.set_ylabel("Invocazioni ricorsive (scala log)")
    ax.set_title("Effetto del controllo delle componenti\nsu una coppia irraggiungibile (50x50)")
    ax.grid(True, which="both", linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, "7_ottimizzazioni.png"), dpi=200)
    plt.close()


def main() -> None:
    component_res = esperimento_component_check()
    with open(os.path.join(RESULTS_DIR, "component_check_results.json"), "w", encoding="utf-8") as f:
        json.dump(component_res, f, indent=2, ensure_ascii=False)

    _plot(component_res)

    print(f"sola etichettatura componenti: {component_res['tempo_sola_etichettatura_s']:.6f}s")
    for c in component_res["corse"]:
        print(
            f"  {c['descrizione']:28s} tempo={c['tempo_s']:.6f}s "
            f"chiamate={c['chiamate_ricorsive']} limite_raggiunto={c['tempo_limite_raggiunto']}"
        )
    print("\nSalvati: results/component_check_results.json, results/7_ottimizzazioni.png")


if __name__ == "__main__":
    main()
