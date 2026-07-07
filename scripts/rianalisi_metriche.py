#!/usr/bin/env python3
"""Re-analisi a costo nullo dei dati già raccolti dalla campagna sperimentale (Relazione, §5.4).

Non esegue alcun nuovo benchmark: legge i JSON già presenti in results/ e calcola due metriche
derivate che oggi in relazione sono solo qualitative:
  - R^2 delle due regressioni bilogaritmiche (tempo vs celle di frontiera, tempo vs invocazioni
    ricorsive), oggi riportate solo con la pendenza;
  - rapporto fra invocazioni ricorsive della potatura debole e della potatura forte per ciascun
    lato della griglia nella campagna di scaling, per quantificare quanto la riga 17 sfolti
    l'albero di ricorsione.
"""
import json
import os

import numpy as np

from src.experiment_plots import _estrai_campioni

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")


def _carica(nome: str) -> list[dict[str, object]]:
    with open(os.path.join(RESULTS_DIR, nome), "r", encoding="utf-8") as f:
        return json.load(f)


def _r_quadro(log_x: np.ndarray, log_y: np.ndarray) -> tuple[float, float]:
    """Ritorna (pendenza, R^2) della regressione lineare log-log."""
    slope, intercept = np.polyfit(log_x, log_y, 1)
    y_pred = slope * log_x + intercept
    ss_res = float(np.sum((log_y - y_pred) ** 2))
    ss_tot = float(np.sum((log_y - np.mean(log_y)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return slope, r2


def main() -> None:
    scaling_res = _carica("scaling_results.json")
    density_res = _carica("density_results.json")
    pruning_res = _carica("pruning_comparison.json")
    ordering_res = _carica("ordering_comparison.json")

    frontier, tempo, _landmarks, ricorsive, _lunghezza = _estrai_campioni(
        scaling_res, density_res, pruning_res, ordering_res
    )

    log_frontier = np.log10(frontier)
    log_ricorsive = np.log10(ricorsive)
    log_tempo = np.log10(tempo)

    pendenza_frontiera, r2_frontiera = _r_quadro(log_frontier, log_tempo)
    pendenza_ricorsione, r2_ricorsione = _r_quadro(log_ricorsive, log_tempo)

    rapporto_nodi = []
    for r in scaling_res:
        weak_calls = r["weak"]["recursive_calls"]
        strong_calls = r["strong"]["recursive_calls"]
        rapporto = weak_calls / strong_calls if strong_calls > 0 else float("inf")
        rapporto_nodi.append({
            "size": r["size"],
            "recursive_calls_weak": weak_calls,
            "recursive_calls_strong": strong_calls,
            "rapporto_debole_forte": rapporto
        })

    esito = {
        "regressione_tempo_vs_frontiera": {
            "pendenza": pendenza_frontiera,
            "r_quadro": r2_frontiera,
            "n_campioni": len(frontier)
        },
        "regressione_tempo_vs_ricorsione": {
            "pendenza": pendenza_ricorsione,
            "r_quadro": r2_ricorsione,
            "n_campioni": len(ricorsive)
        },
        "rapporto_nodi_esplorati_per_taglia": rapporto_nodi
    }

    out_path = os.path.join(RESULTS_DIR, "rianalisi_metriche.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(esito, f, indent=2, ensure_ascii=False)

    print(f"Regressione tempo/frontiera:  pendenza={pendenza_frontiera:.4f}  R^2={r2_frontiera:.4f}  (n={len(frontier)})")
    print(f"Regressione tempo/ricorsione: pendenza={pendenza_ricorsione:.4f}  R^2={r2_ricorsione:.4f}  (n={len(ricorsive)})")
    print("\nRapporto invocazioni ricorsive (debole / forte) per taglia:")
    for r in rapporto_nodi:
        print(f"  lato {r['size']:>4}: debole={r['recursive_calls_weak']:>12} "
              f"forte={r['recursive_calls_strong']:>12}  rapporto={r['rapporto_debole_forte']:.2f}x")
    print(f"\nSalvato in: {out_path}")


if __name__ == "__main__":
    main()
