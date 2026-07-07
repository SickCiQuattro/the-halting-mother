#!/usr/bin/env python3
"""Copertura della tipologia 'mix' (Relazione, §5.4 — requisito Compito 4: tutte le tipologie).

Le cinque tipologie singole (simple, cluster, diagonal, enclosure, bar) sono già coperte dalle
campagne di potatura, ordinamento e simmetria per tipo (results/pruning_comparison.json,
results/ordering_comparison.json, results/symmetry_per_type.json), tutte a 50x50 o 20x20.
Manca la tipologia combinata 'mix' (più tipologie di ostacolo sulla stessa griglia, generata da
GridGenerator.generate_grid quando i tipi includono più voci contemporaneamente). Questo script
mirror la stessa metodologia già usata per le tipologie singole in src/experiment_runner.py,
limitata a 'mix', per chiudere la copertura richiesta dallo spec senza rieseguire l'intera
run_campaign().

Produce results/mix_comparison.json.
"""
import json
import os

import numpy as np

from src.generator import GridGenerator
from src.experiment_runner import run_single_benchmark, run_benchmark_coppia, _coppie_casuali, _mediana_metriche
from src.experiment_verifica import verify_symmetry

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")
MIX_TYPES = ["simple", "cluster", "diagonal", "enclosure", "bar"]


def main() -> None:
    # Stessi parametri (taglia, densità, seme) della campagna di potatura/ordinamento per tipo,
    # così i tempi restano direttamente confrontabili con quelli già in pruning_comparison.json.
    grid = GridGenerator.generate_grid(50, 50, MIX_TYPES, density=0.2, seed=2026)
    grid.clear_cell(0, 0)
    grid.clear_cell(49, 49)
    # La sovrapposizione di più tipologie macro-strutturate può superare la densità nominale
    # (src/generator.py, GridGenerator.generate_grid): la registriamo per rendere il confronto
    # "a parità di densità" con le tipologie singole verificabile, non solo qualitativo.
    densita_effettiva = float(np.sum(grid.state == 1) / (50 * 50))

    rng = np.random.default_rng(13)
    coppie = [((0, 0), (49, 49))]
    coppie += _coppie_casuali(grid, 4, rng)

    campioni_weak = [
        run_single_benchmark(grid, o, d, use_strong_pruning=False, timeout=20.0)
        for o, d in coppie
    ]
    dettagli_strong = [
        run_benchmark_coppia(grid, o, d, use_strong_pruning=True, timeout=20.0)
        for o, d in coppie
    ]
    campioni_random = [
        run_single_benchmark(grid, o, d, use_strong_pruning=True, randomize_frontier=True, timeout=20.0)
        for o, d in coppie
    ]

    # Verifica di simmetria dedicata (diapositiva 64) su una griglia mix più piccola, per avere
    # risultati definitivi senza rischio di timeout, in linea con run_symmetry_per_type.
    grid_sym = GridGenerator.generate_grid(20, 20, MIX_TYPES, density=0.15, seed=99)
    punti_sym: list[tuple[tuple[int, int], tuple[int, int]]] = []
    rng_sym = np.random.default_rng(101)
    for _ in range(5):
        for _ in range(1000):
            o = (int(rng_sym.integers(0, 20)), int(rng_sym.integers(0, 20)))
            d = (int(rng_sym.integers(0, 20)), int(rng_sym.integers(0, 20)))
            if o != d and grid_sym.is_traversable(*o) and grid_sym.is_traversable(*d):
                punti_sym.append((o, d))
                break
    risultati_sym = verify_symmetry(grid_sym, punti_sym, use_strong=True)
    falliti_sym = [r for r in risultati_sym if not r["symmetry_ok"]]

    esito = {
        "obstacle_type": "mix",
        "tipologie_incluse": MIX_TYPES,
        "densita_nominale": 0.2,
        "densita_effettiva": densita_effettiva,
        "weak": _mediana_metriche(campioni_weak),
        "strong": _mediana_metriche([c["andata"] for c in dettagli_strong]),
        "random": _mediana_metriche(campioni_random),
        "simmetrie_fallite_potatura": sum(1 for c in dettagli_strong if not c["simmetria_ok"]),
        "simmetria_dedicata": {
            "total_pairs": len(risultati_sym),
            "failed": len(falliti_sym),
            "excluded_timeout": sum(1 for r in risultati_sym if r["timed_out_od"] or r["timed_out_do"]),
            "pairs": risultati_sym
        },
        "campioni_weak": campioni_weak,
        "coppie_strong": dettagli_strong,
        "campioni_random": campioni_random
    }

    out_path = os.path.join(RESULTS_DIR, "mix_comparison.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(esito, f, indent=2, default=str, ensure_ascii=False)

    print(f"Mix 50x50 — potatura debole:  tempo mediano={esito['weak']['elapsed_time_s']:.4f}s "
          f"timed_out={esito['weak']['timed_out']}")
    print(f"Mix 50x50 — potatura forte:   tempo mediano={esito['strong']['elapsed_time_s']:.4f}s "
          f"timed_out={esito['strong']['timed_out']}")
    print(f"Mix 50x50 — ordinamento casuale: tempo mediano={esito['random']['elapsed_time_s']:.4f}s "
          f"timed_out={esito['random']['timed_out']}")
    print(f"Simmetria dedicata (20x20, {len(risultati_sym)} coppie): {len(falliti_sym)} fallimenti")
    print(f"Densità nominale: {esito['densita_nominale']:.2f}  Densità effettiva: {densita_effettiva:.4f}")
    print(f"Salvato in: {out_path}")


if __name__ == "__main__":
    main()
