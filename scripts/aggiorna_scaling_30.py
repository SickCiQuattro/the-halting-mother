#!/usr/bin/env python3
"""Aggiorna la campagna di scaling: aggiunge la taglia 30x30 e rimuove la 200x200.

Migrazione una tantum, già eseguita: non va rilanciata (l'ha già applicata a
`results/scaling_results.json`). Resta nel repository solo a scopo di documentazione,
per mostrare come sono stati ottenuti i dati attuali senza ripetere l'intera campagna.

La 200x200 non trova alcun cammino completo in 600s per nessuna delle due potature
(vedi Conclusioni), quindi non aggiunge informazione. Le taglie gia' calcolate
(10/20/50/100/150) restano valide cosi' come sono: il comportamento di default
dell'algoritmo non e' cambiato da quando sono state prodotte, quindi si riusano
senza ricalcolarle (ognuna costerebbe fino a 30 minuti in caso di timeout).
"""
import json
import os

from src.experiment import ExperimentRunner
from _common import griglia_campagna_scaling

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")
SCALING_TIMEOUT = 600.0

if __name__ == "__main__":
    path = os.path.join(RESULTS_DIR, "scaling_results.json")
    with open(path, encoding="utf-8") as f:
        scaling_results = json.load(f)

    scaling_results = [r for r in scaling_results if r["size"] != 200]

    size = 30
    grid, o, d = griglia_campagna_scaling(size)

    res_weak = ExperimentRunner.run_single_benchmark(grid, o, d, use_strong_pruning=False, timeout=SCALING_TIMEOUT)
    coppia = ExperimentRunner.run_benchmark_coppia(grid, o, d, use_strong_pruning=True, timeout=SCALING_TIMEOUT)
    scaling_results.append({
        "size": size,
        "weak": res_weak,
        "strong": coppia["andata"],
        "ritorno": coppia["ritorno"],
        "simmetria_verificabile": coppia["simmetria_verificabile"],
        "simmetria_ok": coppia["simmetria_ok"],
    })
    scaling_results.sort(key=lambda r: r["size"])

    with open(path, "w", encoding="utf-8") as f:
        json.dump(scaling_results, f, indent=2, default=str)

    with open(os.path.join(RESULTS_DIR, "density_results.json"), encoding="utf-8") as f:
        density_results = json.load(f)
    with open(os.path.join(RESULTS_DIR, "pruning_comparison.json"), encoding="utf-8") as f:
        pruning_comp = json.load(f)
    with open(os.path.join(RESULTS_DIR, "ordering_comparison.json"), encoding="utf-8") as f:
        ordering_comp = json.load(f)

    ExperimentRunner.generate_plots(
        scaling_results, density_results, pruning_comp, ordering_comp, RESULTS_DIR
    )
    print("scaling_results.json aggiornato (30 aggiunta, 200 rimossa); grafici rigenerati in results/.")
