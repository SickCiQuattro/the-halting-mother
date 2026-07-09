#!/usr/bin/env python3
"""Ridisegna potatura (riga 16 contro riga 17) e ordinamento (euristico contro casuale) come
campagna multi-seme (Piano di miglioramento, sezione 2.A). Le versioni a seme singolo
(pruning_comparison.json, ordering_comparison.json, seed=2026) restano come riferimento più
fine (5 coppie per griglia, incluse quelle casuali); qui si isola la coppia d'angolo su 8 semi
di griglia indipendenti per tipologia, con mediana e IQR: lo stesso protocollo di
campagna_densita_multiseme.py, per lo stesso motivo (C1/C2 in ValutazioneEsperimenti.md).

L'ordinamento euristico riusa le corse "forte" già eseguite per la potatura (nella campagna
sono la stessa configurazione), evitando di duplicare l'esecuzione.

Costo atteso: dominato dalla potatura debole, che secondo multiseme_results.json può superare
i 10s su alcune tipologie/semi; con 5 tipologie x 8 semi il tempo totale realistico è
15-35 minuti.

Produce results/pruning_comparison_multiseme.json e results/ordering_comparison_multiseme.json,
sovrascrive results/2_pruning_comparison_boxplot.png.
"""
import json
import os

import numpy as np

from _common import plt
from src.generator import GridGenerator
from src.experiment_runner import run_single_benchmark, run_benchmark_coppia
from src.plot_style import COLOR_DEBOLE, COLOR_FORTE

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")

SEEDS = [401, 402, 403, 404, 405, 406, 407, 408]  # stessi semi della campagna densità
TIPI = ["simple", "cluster", "diagonal", "enclosure", "bar"]
TAGLIA = 50
TIMEOUT = 20.0
ORIGIN, DEST = (0, 0), (TAGLIA - 1, TAGLIA - 1)


def _iqr(valori: list[float]) -> tuple[float, float, float]:
    return (float(np.median(valori)), float(np.percentile(valori, 25)), float(np.percentile(valori, 75)))


def _aggrega(corse: list[dict[str, object]]) -> dict[str, object]:
    tempi = [c["elapsed_time_s"] for c in corse]
    chiamate = [c["recursive_calls"] for c in corse]
    mediana_t, q1_t, q3_t = _iqr(tempi)
    mediana_c, q1_c, q3_c = _iqr(chiamate)
    return {
        "n_semi": len(corse),
        "tempo_mediano_s": mediana_t, "tempo_q1_s": q1_t, "tempo_q3_s": q3_t,
        "chiamate_mediane": mediana_c, "chiamate_q1": q1_c, "chiamate_q3": q3_c,
        "timeout_su_semi": sum(1 for c in corse if c["timed_out"]),
        "campioni": corse
    }


def _campagna() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    pruning: list[dict[str, object]] = []
    ordering: list[dict[str, object]] = []
    simmetrie_fallite_totali = 0

    for tipo in TIPI:
        corse_weak, corse_strong, corse_random = [], [], []
        for seed in SEEDS:
            grid = GridGenerator.generate_grid(TAGLIA, TAGLIA, [tipo], density=0.2, seed=seed)
            grid.clear_cell(*ORIGIN)
            grid.clear_cell(*DEST)

            esito_weak = run_single_benchmark(grid, ORIGIN, DEST, use_strong_pruning=False, timeout=TIMEOUT)
            corse_weak.append({"seed": seed, **esito_weak})

            # La doppia invocazione O<->D avviene qui, sulla configurazione forte.
            coppia = run_benchmark_coppia(grid, ORIGIN, DEST, use_strong_pruning=True, timeout=TIMEOUT)
            corse_strong.append({"seed": seed, **coppia["andata"]})
            if coppia["simmetria_verificabile"] and not coppia["simmetria_ok"]:
                simmetrie_fallite_totali += 1

            esito_random = run_single_benchmark(
                grid, ORIGIN, DEST, use_strong_pruning=True, randomize_frontier=True, timeout=TIMEOUT
            )
            corse_random.append({"seed": seed, **esito_random})

        pruning.append({"obstacle_type": tipo, "weak": _aggrega(corse_weak), "strong": _aggrega(corse_strong)})
        ordering.append({"obstacle_type": tipo, "heuristic": _aggrega(corse_strong), "random": _aggrega(corse_random)})

    if simmetrie_fallite_totali:
        print(f"ATTENZIONE: {simmetrie_fallite_totali} fallimenti di simmetria O<->D rilevati.")

    return pruning, ordering


def _plot(pruning: list[dict[str, object]]) -> None:
    categorie = [r["obstacle_type"] for r in pruning]
    weak_med = [r["weak"]["tempo_mediano_s"] for r in pruning]
    weak_err = [
        [max(0, r["weak"]["tempo_mediano_s"] - r["weak"]["tempo_q1_s"]) for r in pruning],
        [max(0, r["weak"]["tempo_q3_s"] - r["weak"]["tempo_mediano_s"]) for r in pruning]
    ]
    strong_med = [r["strong"]["tempo_mediano_s"] for r in pruning]
    strong_err = [
        [max(0, r["strong"]["tempo_mediano_s"] - r["strong"]["tempo_q1_s"]) for r in pruning],
        [max(0, r["strong"]["tempo_q3_s"] - r["strong"]["tempo_mediano_s"]) for r in pruning]
    ]

    x = np.arange(len(categorie))
    width = 0.35
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x - width / 2, weak_med, width, yerr=weak_err, capsize=4,
           label=f'Potatura debole (mediana + IQR, {len(SEEDS)} semi)', color=COLOR_DEBOLE)
    ax.bar(x + width / 2, strong_med, width, yerr=strong_err, capsize=4,
           label=f'Potatura forte (mediana + IQR, {len(SEEDS)} semi)', color=COLOR_FORTE)
    ax.set_title(f"Tempi di esecuzione per tipologia: {len(SEEDS)} semi indipendenti (coppia d'angolo)",
                 fontsize=12, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(categorie)
    ax.set_ylabel("Tempo di esecuzione mediano (secondi)")
    ax.set_yscale('log')
    ax.grid(True, which="both", linestyle='--', alpha=0.4)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.08), ncol=2)
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, "2_pruning_comparison_boxplot.png"), dpi=200, bbox_inches='tight')
    plt.close()


def main() -> None:
    pruning, ordering = _campagna()

    with open(os.path.join(RESULTS_DIR, "pruning_comparison_multiseme.json"), "w", encoding="utf-8") as f:
        json.dump(
            {"semi_usati": SEEDS, "timeout_s": TIMEOUT, "per_tipo": pruning},
            f, indent=2, default=str, ensure_ascii=False
        )
    with open(os.path.join(RESULTS_DIR, "ordering_comparison_multiseme.json"), "w", encoding="utf-8") as f:
        json.dump(
            {"semi_usati": SEEDS, "timeout_s": TIMEOUT, "per_tipo": ordering},
            f, indent=2, default=str, ensure_ascii=False
        )

    _plot(pruning)

    print(f"=== Potatura debole contro forte, {len(SEEDS)} semi, coppia d'angolo (50x50) ===")
    for r in pruning:
        print(f"  {r['obstacle_type']:10s} debole={r['weak']['tempo_mediano_s']:.4f}s "
              f"(timeout {r['weak']['timeout_su_semi']}/{len(SEEDS)})  "
              f"forte={r['strong']['tempo_mediano_s']:.4f}s (timeout {r['strong']['timeout_su_semi']}/{len(SEEDS)})")

    print(f"\n=== Ordinamento euristico contro casuale, {len(SEEDS)} semi, coppia d'angolo (50x50, potatura forte) ===")
    for r in ordering:
        print(f"  {r['obstacle_type']:10s} euristico={r['heuristic']['tempo_mediano_s']:.4f}s  "
              f"casuale={r['random']['tempo_mediano_s']:.4f}s "
              f"(timeout {r['random']['timeout_su_semi']}/{len(SEEDS)})")

    print("\nSalvati: results/pruning_comparison_multiseme.json, "
          "results/ordering_comparison_multiseme.json, results/2_pruning_comparison_boxplot.png")


if __name__ == "__main__":
    main()
