#!/usr/bin/env python3
"""Robustezza multi-seme sulle campagne veloci (Relazione, sezione 5.4: la specifica chiede istanze
significative e numerose).

Le campagne esistenti (potatura per tipo, densità) usano una griglia a seme fisso: le mediane
sono su più coppie origine-destinazione DENTRO la stessa topologia, non su più topologie
generate con semi diversi. Questo script ripete, solo sulle configurazioni a basso costo
temporale, la stessa misura su più semi di griglia, riportando mediana e scarto interquartile
(IQR) fra i semi. Non tocca la campagna di scaling pesante (una curva di crescita, non una
stima di variabilità) né le densità più alte (già a rischio di timeout con un solo seme).

Produce results/multiseme_results.json e results/8_multiseme_iqr.png.
"""
import json
import os

import numpy as np

from _common import plt
from src.generator import GridGenerator
from src.experiment_runner import run_single_benchmark

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")

# Semi distinti da quelli già usati altrove nella campagna (2026, 100, 7, 13, 42, 99, 2, 101, 999).
SEEDS = [301, 302, 303, 304, 305]
PER_RUN_TIMEOUT = 15.0


def _iqr(valori: list[float]) -> tuple[float, float, float]:
    """Ritorna (mediana, 25° percentile, 75° percentile)."""
    return (
        float(np.median(valori)),
        float(np.percentile(valori, 25)),
        float(np.percentile(valori, 75))
    )


def campagna_per_tipo() -> list[dict[str, object]]:
    tipi = ["simple", "cluster", "diagonal", "enclosure", "bar"]
    origin, dest = (0, 0), (49, 49)
    risultati = []
    for tipo in tipi:
        tempi = []
        chiamate = []
        per_seme = []
        for seed in SEEDS:
            grid = GridGenerator.generate_grid(50, 50, [tipo], density=0.2, seed=seed)
            grid.clear_cell(*origin)
            grid.clear_cell(*dest)
            esito = run_single_benchmark(
                grid, origin, dest,
                use_strong_pruning=True, timeout=PER_RUN_TIMEOUT
            )
            tempi.append(esito["elapsed_time_s"])
            chiamate.append(esito["recursive_calls"])
            per_seme.append({"seed": seed, **esito})
        mediana_t, q1_t, q3_t = _iqr(tempi)
        mediana_c, q1_c, q3_c = _iqr(chiamate)
        risultati.append({
            "obstacle_type": tipo,
            "n_semi": len(SEEDS),
            "tempo_mediano_s": mediana_t, "tempo_q1_s": q1_t, "tempo_q3_s": q3_t,
            "chiamate_mediane": mediana_c, "chiamate_q1": q1_c, "chiamate_q3": q3_c,
            "timeout_su_semi": sum(1 for r in per_seme if r["timed_out"]),
            "campioni": per_seme
        })
    return risultati


def campagna_densita() -> list[dict[str, object]]:
    densita = [0.05, 0.15, 0.25, 0.35]
    origin, dest = (0, 0), (49, 49)
    risultati = []
    for dens in densita:
        tempi = []
        per_seme = []
        for seed in SEEDS:
            grid = GridGenerator.generate_grid(50, 50, ["simple", "cluster"], density=dens, seed=seed)
            grid.clear_cell(*origin)
            grid.clear_cell(*dest)
            esito = run_single_benchmark(
                grid, origin, dest,
                use_strong_pruning=True, timeout=PER_RUN_TIMEOUT
            )
            tempi.append(esito["elapsed_time_s"])
            per_seme.append({"seed": seed, **esito})
        mediana_t, q1_t, q3_t = _iqr(tempi)
        risultati.append({
            "density": dens,
            "n_semi": len(SEEDS),
            "tempo_mediano_s": mediana_t, "tempo_q1_s": q1_t, "tempo_q3_s": q3_t,
            "timeout_su_semi": sum(1 for r in per_seme if r["timed_out"]),
            "campioni": per_seme
        })
    return risultati


def _plot(per_tipo: list[dict[str, object]], per_densita: list[dict[str, object]]) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    tipi = [r["obstacle_type"] for r in per_tipo]
    mediane = [r["tempo_mediano_s"] for r in per_tipo]
    err_basso = [max(0, r["tempo_mediano_s"] - r["tempo_q1_s"]) for r in per_tipo]
    err_alto = [max(0, r["tempo_q3_s"] - r["tempo_mediano_s"]) for r in per_tipo]
    ax1.errorbar(tipi, mediane, yerr=[err_basso, err_alto], fmt='o', capsize=5,
                 color='#2ed573', ecolor='#576574', markersize=8)
    ax1.set_yscale('log')
    ax1.set_ylabel("Tempo di esecuzione mediano (s, scala log)")
    ax1.set_title(f"Tempo per tipologia, {len(SEEDS)} semi (mediana + IQR)\ncoppia d'angolo, 50x50, potatura forte")
    ax1.grid(True, which="both", linestyle="--", alpha=0.4)

    dens = [r["density"] for r in per_densita]
    mediane_d = [r["tempo_mediano_s"] for r in per_densita]
    err_basso_d = [max(0, r["tempo_mediano_s"] - r["tempo_q1_s"]) for r in per_densita]
    err_alto_d = [max(0, r["tempo_q3_s"] - r["tempo_mediano_s"]) for r in per_densita]
    ax2.errorbar(dens, mediane_d, yerr=[err_basso_d, err_alto_d], fmt='o-', capsize=5,
                 color='#0984e3', ecolor='#576574', markersize=8)
    ax2.set_yscale('log')
    ax2.set_xlabel("Densità ostacoli")
    ax2.set_ylabel("Tempo di esecuzione mediano (s, scala log)")
    ax2.set_title(f"Tempo per densità, {len(SEEDS)} semi (mediana + IQR)\ncoppia d'angolo, 50x50, potatura forte")
    ax2.grid(True, which="both", linestyle="--", alpha=0.4)

    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, "8_multiseme_iqr.png"), dpi=200)
    plt.close()


def main() -> None:
    per_tipo = campagna_per_tipo()
    per_densita = campagna_densita()

    esito = {"semi_usati": SEEDS, "per_tipo": per_tipo, "per_densita": per_densita}
    out_path = os.path.join(RESULTS_DIR, "multiseme_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(esito, f, indent=2, ensure_ascii=False)

    _plot(per_tipo, per_densita)

    print("=== Multi-seme per tipologia (50x50, potatura forte, coppia d'angolo) ===")
    for r in per_tipo:
        print(f"  {r['obstacle_type']:10s} mediana={r['tempo_mediano_s']:.5f}s "
              f"IQR=[{r['tempo_q1_s']:.5f}, {r['tempo_q3_s']:.5f}] timeout_su_semi={r['timeout_su_semi']}/{r['n_semi']}")

    print("\n=== Multi-seme per densità (50x50, potatura forte, coppia d'angolo) ===")
    for r in per_densita:
        print(f"  densità={r['density']:.2f} mediana={r['tempo_mediano_s']:.5f}s "
              f"IQR=[{r['tempo_q1_s']:.5f}, {r['tempo_q3_s']:.5f}] timeout_su_semi={r['timeout_su_semi']}/{r['n_semi']}")

    print(f"\nSalvati: {out_path}, results/8_multiseme_iqr.png")


if __name__ == "__main__":
    main()
