#!/usr/bin/env python3
"""Rigenera la sola figura 4 (scatter combinato tempo/complessità) senza rilanciare l'intera
campagna sperimentale (Piano di miglioramento, sezione 2.F).

In precedenza le figure 4 e 5 erano due scatter separati (tempo contro frontiera, tempo contro
invocazioni ricorsive) con correlazione praticamente identica (R^2=0.93 e 0.84): le due metriche crescono
insieme per costruzione (ogni chiamata ricorsiva aggiunge la propria frontiera al totale), quindi
la seconda figura non aggiungeva informazione strutturale. src/experiment_plots.py ora produce
un'unica figura a due pannelli (_plot_scatter_combined); questo script la rigenera dai JSON già
presenti in results/, senza rieseguire alcun benchmark (costo: pochi secondi, solo plotting).

Nota: i campioni vengono estratti dalle versioni "storiche" di density_results.json,
pruning_comparison.json e ordering_comparison.json. Questo è corretto per lo scopo della
regressione (i singoli campioni raccolti sono dati validi indipendentemente dalla loro
aggregazione), anche se la campagna densità/potatura/ordinamento a seme singolo non è più la
fonte della figura headline (si veda campagna_densita_multiseme.py e
campagna_potatura_ordinamento_multiseme.py per quello).
"""
import json
import os

from src.experiment_plots import _estrai_campioni, _plot_scatter_combined

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")


def _carica(nome: str) -> list[dict[str, object]]:
    with open(os.path.join(RESULTS_DIR, nome), "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    scaling_res = _carica("scaling_results.json")
    density_res = _carica("density_results.json")
    pruning_res = _carica("pruning_comparison.json")
    ordering_res = _carica("ordering_comparison.json")

    frontier, tempo, landmarks, ricorsive, lunghezza = _estrai_campioni(
        scaling_res, density_res, pruning_res, ordering_res
    )
    _plot_scatter_combined(frontier, ricorsive, tempo, landmarks, lunghezza, RESULTS_DIR)

    print(f"Rigenerata results/4_scatter_time_vs_frontier.png ({len(tempo)} campioni).")
    print("results/5_scatter_time_vs_recursion.png è ora obsoleta (non più prodotta dalla pipeline).")


if __name__ == "__main__":
    main()
