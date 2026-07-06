#!/usr/bin/env python3
"""Oracolo A* sulla campagna di scaling: conferma di ottimalità e divario anytime (Relazione).

Rigenera le stesse griglie della sezione di scaling della campagna sperimentale (seed 42,
taglie 10-200, tipologie simple+cluster+bar, densità 0.2), calcola la lunghezza ottima esatta
con A* (euristica octile `dlib`, ammissibile e consistente) e la confronta con le lunghezze
già salvate in `results/scaling_results.json`:

  - esecuzioni completate: la lunghezza di CAMMINOMIN deve coincidere con l'ottimo di A*
    (verifica di correttezza indipendente, più forte della sola simmetria O-D / D-O);
  - esecuzioni interrotte al tempo limite: divario percentuale del risultato anytime
    rispetto al vero ottimo (incluso il caso "nessun cammino trovato").

Produce `results/divario_anytime.json` e la figura `Relazione/images/divario_anytime.png`.
Non riesegue la campagna (~2 h): usa solo i risultati già salvati.
"""
import os
import sys
import json
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.generator import GridGenerator
from src.astar import astar

BASE = os.path.join(os.path.dirname(__file__), "..")
RESULTS = os.path.join(BASE, "results", "scaling_results.json")
OUT_JSON = os.path.join(BASE, "results", "divario_anytime.json")
OUT_PNG = os.path.join(BASE, "Relazione", "images", "divario_anytime.png")

CONFIGS = [("weak", "Potatura debole (riga 16)"), ("strong", "Potatura forte (riga 17)"),
           ("ritorno", "Forte, ritorno D-O")]
# Tonalità coerenti con le figure esistenti della relazione, scurite per leggibilità su bianco
COLORS = {"weak": "#b8860b", "strong": "#1d8348", "ritorno": "#2f6fdb"}


def main() -> None:
    with open(RESULTS, encoding="utf-8") as f:
        scaling = json.load(f)

    report: list[dict[str, object]] = []
    for entry in scaling:
        size = int(entry["size"])
        grid = GridGenerator.generate_grid(
            size, size, ["simple", "cluster", "bar"], density=0.2, seed=42
        )
        o, d = (0, 0), (size - 1, size - 1)
        grid.clear_cell(*o)
        grid.clear_cell(*d)

        start = time.time()
        ottimo = astar(o, d, grid.state)
        t_astar = time.time() - start

        riga: dict[str, object] = {"size": size, "ottimo_astar": ottimo, "tempo_astar_s": t_astar}
        for key, _label in CONFIGS:
            lunghezza = float(entry[key]["path_length"])
            timed_out = bool(entry[key]["timed_out"])
            if not timed_out:
                confermato = abs(lunghezza - ottimo) < 1e-9
                riga[key] = {"lunghezza": lunghezza, "interrotto": False, "confermato": confermato}
                stato = "CONFERMATO" if confermato else "DIVERGENTE!"
                print(f"{size:>4} {key:<8} completato: {lunghezza:.6f} vs A* {ottimo:.6f} -> {stato}")
            elif lunghezza == float("inf"):
                riga[key] = {"lunghezza": None, "interrotto": True, "divario_pct": None}
                print(f"{size:>4} {key:<8} interrotto: nessun cammino trovato (ottimo {ottimo:.6f})")
            else:
                divario = (lunghezza - ottimo) / ottimo * 100.0
                riga[key] = {"lunghezza": lunghezza, "interrotto": True, "divario_pct": divario}
                print(f"{size:>4} {key:<8} interrotto: anytime {lunghezza:.6f} vs A* {ottimo:.6f} "
                      f"-> divario {divario:.2f}%")
        report.append(riga)

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport salvato in {OUT_JSON}")

    # ── Figura: divario percentuale anytime sulle sole esecuzioni interrotte ── #
    interrotte = [r for r in report if any(r[k]["interrotto"] for k, _ in CONFIGS)]
    sizes = [r["size"] for r in interrotte]
    x = range(len(sizes))
    width = 0.24

    plt.figure(figsize=(8, 5))
    for i, (key, label) in enumerate(CONFIGS):
        offset = (i - 1) * (width + 0.04)
        for xi, r in zip(x, interrotte):
            dati = r[key]
            if not dati["interrotto"]:
                continue
            pos = xi + offset
            if dati["divario_pct"] is None:
                plt.text(pos, 0.3, "nessun cammino", ha="center", va="bottom", rotation=90,
                         fontsize=8, color=COLORS[key], fontweight="bold")
            else:
                plt.bar(pos, dati["divario_pct"], width=width, color=COLORS[key],
                        label=label if label else None)
                plt.text(pos, dati["divario_pct"] + 0.3, f"{dati['divario_pct']:.1f}%",
                         ha="center", va="bottom", fontsize=8, color="#333333")
            label = ""  # una sola voce di legenda per configurazione

    plt.xticks(list(x), [f"{s}x{s}" for s in sizes], fontsize=10)
    plt.xlabel("Dimensione griglia (lato R = C)", fontsize=10)
    plt.ylabel("Divario dal cammino ottimo (%)", fontsize=10)
    plt.title("Divario di ottimalità del risultato anytime alle esecuzioni interrotte (600 s)",
              fontsize=12, fontweight="bold")
    plt.grid(True, axis="y", linestyle="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT_PNG, dpi=200)
    plt.close()
    print(f"Figura salvata in {OUT_PNG}")


if __name__ == "__main__":
    main()
