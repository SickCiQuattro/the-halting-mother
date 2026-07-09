#!/usr/bin/env python3
"""Grafico memoria in funzione della taglia dell'algoritmo CAMMINOMIN (Piano di miglioramento, sezione 2.C).

La specifica richiede prestazioni sia temporali sia spaziali; peak_memory_kb è
già raccolto in ogni benchmark ma non è mai stato tracciato contro la dimensione della griglia.
Nessuna nuova esecuzione: i dati sono già in results/scaling_results.json.

Produce results/10_memory_vs_size.png.
"""
import json
import os

from _common import plt
from src.plot_style import COLOR_DEBOLE, COLOR_FORTE

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")


def main() -> None:
    with open(os.path.join(RESULTS_DIR, "scaling_results.json"), encoding="utf-8") as f:
        scaling_res = json.load(f)

    sizes = [r["size"] for r in scaling_res]
    mem_weak = [r["weak"]["peak_memory_kb"] for r in scaling_res]
    mem_strong = [r["strong"]["peak_memory_kb"] for r in scaling_res]

    plt.figure(figsize=(8, 5))
    plt.plot(sizes, mem_weak, marker='s', color=COLOR_DEBOLE, linewidth=2, label='Potatura debole (riga 16)')
    plt.plot(sizes, mem_strong, marker='^', color=COLOR_FORTE, linewidth=2, label='Potatura forte (riga 17)')
    plt.xscale('log')
    plt.xlabel("Dimensione griglia (lato R = C)", fontsize=10)
    plt.ylabel("Picco di memoria (KB)", fontsize=10)
    plt.title("Occupazione di memoria in funzione della dimensione della griglia", fontsize=12, fontweight='bold')
    plt.grid(True, which="both", linestyle='--', alpha=0.5)
    plt.legend()
    plt.tight_layout()
    out_path = os.path.join(RESULTS_DIR, "10_memory_vs_size.png")
    plt.savefig(out_path, dpi=200)
    plt.close()

    print("Picco di memoria (KB) per lato:")
    for s, mw, ms in zip(sizes, mem_weak, mem_strong):
        print(f"  lato {s:>4}: debole={mw:>10.2f} KB  forte={ms:>10.2f} KB")
    print(f"\nSalvato in: {out_path}")


if __name__ == "__main__":
    main()
