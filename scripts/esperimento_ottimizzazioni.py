#!/usr/bin/env python3
"""Esperimento documentato per l'innesco goloso e il controllo dei componenti connessi
(Relazione, §4.4 e §4.5). Sostituisce gli script ad-hoc verifica_innesco_goloso.py e
verifica_componenti.py, che misuravano l'effetto delle due ottimizzazioni solo a schermo,
senza salvare risultati né produrre una figura.

Produce:
  - results/greedy_seed_results.json
  - results/component_check_results.json
  - results/7_ottimizzazioni.png
"""
import json
import os
import time

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from src.grid import Grid, compute_components
from src.generator import GridGenerator
from src.camminomin import camminomin

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")
GRIDS_DIR = os.path.join(os.path.dirname(__file__), "..", "grids")
# Stessi tempi limite già usati per i numeri citati in relazione (§4.4, §4.5), per non
# produrre risultati incoerenti con quanto già scritto nel testo.
COMPONENT_TIMEOUT = 600.0


def _esegui(origin, dest, grid_state, forte: bool, seed: bool, timeout: float):
    stats: dict[str, int] = {}
    start = time.time()
    min_len, _landmarks, timed_out = camminomin(
        origin, dest, grid_state.copy(), stats=stats,
        use_strong_pruning=forte, greedy_seed=seed,
        start_time=start, timeout=timeout
    )
    elapsed = time.time() - start
    return {
        "potatura_forte": forte,
        "innesco_goloso": seed,
        "tempo_s": elapsed,
        "lunghezza": None if np.isinf(min_len) else min_len,
        "chiamate_ricorsive": stats.get("recursive_calls", 0),
        "celle_frontiera": stats.get("frontier_cells", 0),
        "tempo_limite_raggiunto": timed_out
    }


def esperimento_greedy_seed() -> list[dict[str, object]]:
    # Stesse istanze e stessi tempi limite di scripts/verifica_innesco_goloso.py, i numeri
    # già discussi in relazione (§4.4): 30s per le prime due, 60s per la 100x100 più difficile.
    istanze = [
        ("18x18 cluster", GridGenerator.generate_grid(18, 18, ["cluster"], density=0.2, seed=2026), (0, 0), (17, 17), 30.0),
        ("40x40 misto", Grid.load(os.path.join(GRIDS_DIR, "grid_report_esempio.json")), (0, 0), (39, 39), 30.0),
        ("100x100 cluster", GridGenerator.generate_grid(100, 100, ["cluster"], density=0.2, seed=2026), (0, 0), (99, 99), 60.0),
    ]
    risultati = []
    for nome, grid, origin, dest, timeout in istanze:
        grid.clear_cell(*origin)
        grid.clear_cell(*dest)
        corse = [
            _esegui(origin, dest, grid.state, forte, seed, timeout)
            for forte in (False, True)
            for seed in (False, True)
        ]
        risultati.append({"istanza": nome, "corse": corse})
    return risultati


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


def _plot(greedy_res: list[dict[str, object]], component_res: dict[str, object]) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))

    istanze = [r["istanza"] for r in greedy_res]
    x = np.arange(len(istanze))
    width = 0.2
    config = [
        ("debole, senza innesco", False, False, "#ff7979"),
        ("debole, con innesco", False, True, "#feca57"),
        ("forte, senza innesco", True, False, "#a29bfe"),
        ("forte, con innesco", True, True, "#2ed573"),
    ]
    for i, (label, forte, seed, colore) in enumerate(config):
        valori = []
        for r in greedy_res:
            corsa = next(c for c in r["corse"] if c["potatura_forte"] == forte and c["innesco_goloso"] == seed)
            valori.append(max(1, corsa["chiamate_ricorsive"]))
        ax1.bar(x + (i - 1.5) * width, valori, width, label=label, color=colore)
    ax1.set_yscale('log')
    ax1.set_xticks(x)
    ax1.set_xticklabels(istanze)
    ax1.set_ylabel("Invocazioni ricorsive (scala log)")
    ax1.set_title("Effetto dell'innesco goloso sul numero di nodi esplorati")
    ax1.legend(fontsize=8)
    ax1.grid(True, which="both", linestyle="--", alpha=0.4)

    corse_comp = component_res["corse"]
    nomi = [c["descrizione"] for c in corse_comp]
    valori_comp = [max(1, c["chiamate_ricorsive"]) for c in corse_comp]
    colori_comp = ["#2ed573", "#ff7979"]
    ax2.bar(nomi, valori_comp, color=colori_comp)
    ax2.set_yscale('log')
    ax2.set_ylabel("Invocazioni ricorsive (scala log)")
    ax2.set_title("Effetto del controllo dei componenti\nsu una coppia irraggiungibile (50x50)")
    ax2.grid(True, which="both", linestyle="--", alpha=0.4)

    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, "7_ottimizzazioni.png"), dpi=200)
    plt.close()


def main() -> None:
    greedy_res = esperimento_greedy_seed()
    with open(os.path.join(RESULTS_DIR, "greedy_seed_results.json"), "w", encoding="utf-8") as f:
        json.dump(greedy_res, f, indent=2, ensure_ascii=False)

    component_res = esperimento_component_check()
    with open(os.path.join(RESULTS_DIR, "component_check_results.json"), "w", encoding="utf-8") as f:
        json.dump(component_res, f, indent=2, ensure_ascii=False)

    _plot(greedy_res, component_res)

    print("=== Innesco goloso ===")
    for r in greedy_res:
        print(f"-- {r['istanza']} --")
        for c in r["corse"]:
            print(
                f"  potatura={'forte' if c['potatura_forte'] else 'debole':6s} "
                f"innesco={'si' if c['innesco_goloso'] else 'no':3s} "
                f"tempo={c['tempo_s']:.4f}s chiamate={c['chiamate_ricorsive']} "
                f"limite_raggiunto={c['tempo_limite_raggiunto']}"
            )

    print("\n=== Controllo componenti connessi ===")
    print(f"sola etichettatura componenti: {component_res['tempo_sola_etichettatura_s']:.6f}s")
    for c in component_res["corse"]:
        print(
            f"  {c['descrizione']:28s} tempo={c['tempo_s']:.6f}s "
            f"chiamate={c['chiamate_ricorsive']} limite_raggiunto={c['tempo_limite_raggiunto']}"
        )

    print(f"\nSalvati: results/greedy_seed_results.json, results/component_check_results.json, "
          f"results/7_ottimizzazioni.png")


if __name__ == "__main__":
    main()
