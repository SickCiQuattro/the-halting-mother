#!/usr/bin/env python3
"""Ridisegna la campagna di densità come esperimento multi-seme (Piano di miglioramento, §2.A).

La versione a seme singolo (results/density_results.json, seed=100) mediava, sulla stessa
griglia, sia la coppia d'angolo sia quattro coppie casuali: questo diluisce sistematicamente il
caso difficile nella mediana. La campagna multi-seme (results/multiseme_results.json) mostra
sulla stessa combinazione taglia/densità tempi mediani di 2-3 ordini di grandezza superiori.
Qui si isola la sola coppia d'angolo (il caso strutturalmente più difficile) su 8 semi di
griglia indipendenti, riportando mediana e IQR. Una singola griglia di riferimento (lo stesso
seed=100 della versione precedente), con tre coppie casuali, resta solo per confrontare la
FORMA della curva, non per il valore headline.

Costo atteso (sulla macchina di riferimento): 10-25 minuti, dominato dalle densità 0.15-0.25,
dove la campagna a 5 semi ha già mostrato timeout parziali (multiseme_results.json).

Produce results/density_results_multiseme.json e sovrascrive results/1_time_vs_density.png.
"""
import json
import os

import numpy as np

from _common import plt
from src.generator import GridGenerator
from src.experiment_runner import run_single_benchmark, _coppie_casuali

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")

SEEDS = [401, 402, 403, 404, 405, 406, 407, 408]
SEED_RIFERIMENTO_FORMA = 100  # stesso seed della vecchia density_results.json
DENSITA = [0.05, 0.15, 0.25, 0.35]
TAGLIA = 50
TIMEOUT = 20.0
ORIGIN, DEST = (0, 0), (TAGLIA - 1, TAGLIA - 1)


def _iqr(valori: list[float]) -> tuple[float, float, float]:
    """Ritorna (mediana, 25° percentile, 75° percentile)."""
    return (float(np.median(valori)), float(np.percentile(valori, 25)), float(np.percentile(valori, 75)))


def _campagna_angolo() -> list[dict[str, object]]:
    risultati = []
    for dens in DENSITA:
        tempi, chiamate, per_seme = [], [], []
        for seed in SEEDS:
            grid = GridGenerator.generate_grid(TAGLIA, TAGLIA, ["simple", "cluster"], density=dens, seed=seed)
            grid.clear_cell(*ORIGIN)
            grid.clear_cell(*DEST)
            esito = run_single_benchmark(grid, ORIGIN, DEST, use_strong_pruning=True, timeout=TIMEOUT)
            tempi.append(esito["elapsed_time_s"])
            chiamate.append(esito["recursive_calls"])
            per_seme.append({"seed": seed, **esito})
        mediana_t, q1_t, q3_t = _iqr(tempi)
        mediana_c, q1_c, q3_c = _iqr(chiamate)
        risultati.append({
            "density": dens,
            "n_semi": len(SEEDS),
            "tempo_mediano_s": mediana_t, "tempo_q1_s": q1_t, "tempo_q3_s": q3_t,
            "chiamate_mediane": mediana_c, "chiamate_q1": q1_c, "chiamate_q3": q3_c,
            "timeout_su_semi": sum(1 for r in per_seme if r["timed_out"]),
            "campioni": per_seme
        })
    return risultati


def _campagna_forma_riferimento() -> list[dict[str, object]]:
    """Coppia d'angolo + 3 coppie casuali su una singola griglia di riferimento, solo per
    confrontare la forma della curva con la vecchia figura a seme singolo."""
    rng = np.random.default_rng(SEED_RIFERIMENTO_FORMA)
    risultati = []
    for dens in DENSITA:
        grid = GridGenerator.generate_grid(
            TAGLIA, TAGLIA, ["simple", "cluster"], density=dens, seed=SEED_RIFERIMENTO_FORMA
        )
        grid.clear_cell(*ORIGIN)
        grid.clear_cell(*DEST)
        coppie = [(ORIGIN, DEST)] + _coppie_casuali(grid, 3, rng)
        tempi = [
            run_single_benchmark(grid, o, d, use_strong_pruning=True, timeout=TIMEOUT)["elapsed_time_s"]
            for o, d in coppie
        ]
        risultati.append({"density": dens, "tempo_mediano_s": float(np.median(tempi))})
    return risultati


def _plot(angolo: list[dict[str, object]], forma: list[dict[str, object]]) -> None:
    dens = [r["density"] for r in angolo]
    mediane = [r["tempo_mediano_s"] for r in angolo]
    err_basso = [max(0, r["tempo_mediano_s"] - r["tempo_q1_s"]) for r in angolo]
    err_alto = [max(0, r["tempo_q3_s"] - r["tempo_mediano_s"]) for r in angolo]
    n_semi = angolo[0]["n_semi"]

    plt.figure(figsize=(8, 5))
    plt.errorbar(dens, mediane, yerr=[err_basso, err_alto], fmt='o-', capsize=5,
                 color='#e056fd', ecolor='#576574', markersize=8, linewidth=2, zorder=3,
                 label=f"Coppia d'angolo, mediana + IQR su {n_semi} semi (50x50, potatura forte)")
    for r, m in zip(angolo, mediane):
        if r["timeout_su_semi"] > 0:
            plt.scatter([r["density"]], [m], marker='x', s=140, color='#d63031', linewidths=2.5, zorder=4)
    plt.scatter([], [], marker='x', s=140, color='#d63031', linewidths=2.5,
                label='Almeno un seme in timeout a questa densità')

    dens_forma = [r["density"] for r in forma]
    tempi_forma = [r["tempo_mediano_s"] for r in forma]
    plt.plot(dens_forma, tempi_forma, linestyle='--', color='#636e72', alpha=0.7, zorder=1,
              label="Riferimento a seme singolo (angolo + 3 coppie casuali, forma soltanto)")

    plt.yscale('log')
    plt.xlabel("Densità ostacoli", fontsize=10)
    plt.ylabel("Tempo di esecuzione (secondi, scala log)", fontsize=10)
    plt.title(f"Tempo vs densità — coppia d'angolo su {n_semi} semi indipendenti (mediana + IQR)",
              fontsize=11, fontweight='bold')
    plt.grid(True, which="both", linestyle='--', alpha=0.5)
    plt.legend(fontsize=8.5)
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, "1_time_vs_density.png"), dpi=200)
    plt.close()


def main() -> None:
    angolo = _campagna_angolo()
    forma = _campagna_forma_riferimento()

    esito = {
        "semi_usati": SEEDS,
        "seed_riferimento_forma": SEED_RIFERIMENTO_FORMA,
        "timeout_s": TIMEOUT,
        "per_densita": angolo,
        "riferimento_forma_seme_singolo": forma
    }
    out_path = os.path.join(RESULTS_DIR, "density_results_multiseme.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(esito, f, indent=2, default=str, ensure_ascii=False)

    _plot(angolo, forma)

    print(f"=== Densità multi-seme, coppia d'angolo ({len(SEEDS)} semi, 50x50, potatura forte) ===")
    for r in angolo:
        print(f"  densità={r['density']:.2f} mediana={r['tempo_mediano_s']:.4f}s "
              f"IQR=[{r['tempo_q1_s']:.4f}, {r['tempo_q3_s']:.4f}] "
              f"timeout_su_semi={r['timeout_su_semi']}/{r['n_semi']}")
    print(f"\nSalvati: {out_path}, results/1_time_vs_density.png")


if __name__ == "__main__":
    main()
