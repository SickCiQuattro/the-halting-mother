"""
Facciata di compatibilità per la campagna sperimentale (Compito 4).

L'implementazione è divisa per responsabilità in tre moduli:
  - src/experiment_verifica.py: verifica di correttezza per simmetria.
  - src/experiment_runner.py:   benchmark singoli e campagna sperimentale completa.
  - src/experiment_plots.py:    generazione dei sei grafici analitici.

Questa classe resta l'unico punto di importazione per main.py e per gli script, così da
non dover cambiare le chiamate già esistenti (`ExperimentRunner.metodo(...)`).
"""
from src.experiment_verifica import verify_symmetry, run_symmetry_per_type
from src.experiment_runner import run_benchmark_coppia, run_single_benchmark, run_campaign
from src.experiment_plots import generate_plots


class ExperimentRunner:
    """Facciata sottile sulle tre responsabilità della campagna sperimentale (Compito 4)."""

    verify_symmetry = staticmethod(verify_symmetry)
    run_symmetry_per_type = staticmethod(run_symmetry_per_type)
    run_benchmark_coppia = staticmethod(run_benchmark_coppia)
    run_single_benchmark = staticmethod(run_single_benchmark)
    run_campaign = staticmethod(run_campaign)
    generate_plots = staticmethod(generate_plots)
