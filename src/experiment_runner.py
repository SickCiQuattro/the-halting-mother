"""Esecuzione dei benchmark e della campagna sperimentale completa (Compito 4)."""
import json
import os
import time
import statistics
import tracemalloc
import logging

import numpy as np

from src.grid import Grid, Coordinate
from src.generator import GridGenerator
from src.camminomin import camminomin
from src.experiment_verifica import run_symmetry_per_type
from src.experiment_plots import generate_plots

logger = logging.getLogger(__name__)


def _coppie_casuali(
    grid: Grid,
    n_pairs: int,
    rng: np.random.Generator
) -> list[tuple[Coordinate, Coordinate]]:
    """
    Estrae coppie casuali distinte di celle attraversabili (origine, destinazione).

    Args:
        grid: La griglia da cui campionare.
        n_pairs: Numero di coppie richieste.
        rng: Generatore pseudo-casuale per la riproducibilità.

    Returns:
        Lista di coppie di coordinate attraversabili.
    """
    coppie: list[tuple[Coordinate, Coordinate]] = []
    for _ in range(n_pairs):
        for _ in range(2000):
            o: Coordinate = (int(rng.integers(0, grid.rows)), int(rng.integers(0, grid.cols)))
            d: Coordinate = (int(rng.integers(0, grid.rows)), int(rng.integers(0, grid.cols)))
            if o != d and grid.is_traversable(o[0], o[1]) and grid.is_traversable(d[0], d[1]):
                coppie.append((o, d))
                break
    return coppie


def _mediana_metriche(campioni: list[dict[str, object]]) -> dict[str, object]:
    """
    Aggrega per mediana le metriche numeriche di più esecuzioni sulla stessa configurazione.

    Args:
        campioni: Lista di dizionari prodotti da `run_single_benchmark`.

    Returns:
        Dizionario con le mediane delle metriche e il numero di campioni aggregati.
    """
    chiavi = [
        "elapsed_time_s", "peak_memory_kb", "frontier_cells", "pruning_false",
        "recursive_calls", "max_depth", "path_length", "landmarks_count"
    ]
    aggregato: dict[str, object] = {}
    for k in chiavi:
        valori = [
            c[k] for c in campioni
            if not (isinstance(c[k], float) and np.isinf(c[k]))
        ]
        aggregato[k] = statistics.median(valori) if valori else float('inf')
    aggregato["timed_out"] = any(c["timed_out"] for c in campioni)
    aggregato["numero_campioni"] = len(campioni)
    return aggregato


def run_single_benchmark(
    grid: Grid,
    origin: Coordinate,
    destination: Coordinate,
    use_strong_pruning: bool = False,
    randomize_frontier: bool = False,
    timeout: float = 30.0
) -> dict[str, object]:
    """
    Esegue un singolo benchmark di cammino minimo con raccolta di metriche.

    Args:
        grid: L'oggetto Griglia.
        origin: Coordinata di partenza.
        destination: Coordinata di arrivo.
        use_strong_pruning: Se True, abilita la potatura forte (riga 17).
        randomize_frontier: Se True, ordina la frontiera casualmente anziché euristicamente.
        timeout: Tempo limite di esecuzione in secondi.

    Returns:
        Dizionario con metriche di percorso, tempo, memoria e nodi esplorati.
    """
    # --- Misura temporale: esecuzione pulita, senza profilatura della memoria ---
    # tracemalloc, se attivo durante il cronometraggio, introduce un sovraccarico di
    # circa cinque volte e falserebbe i tempi: la misura della memoria viene perciò
    # tenuta separata da quella del tempo (vedi passata successiva).
    state_copy = grid.state.copy()
    stats: dict[str, int] = {
        'frontier_cells': 0,
        'pruning_false': 0,
        'recursive_calls': 0,
        'max_depth': 0
    }

    start_time = time.time()

    try:
        l_min, landmarks, timed_out = camminomin(
            origin, destination, state_copy, depth=0, stats=stats,
            start_time=start_time, timeout=timeout,
            use_strong_pruning=use_strong_pruning,
            randomize_frontier=randomize_frontier
        )
    except Exception as e:
        logger.error(f"Errore critico durante benchmark: {e}", exc_info=True)
        l_min, landmarks, timed_out = float('inf'), [], False

    elapsed = time.time() - start_time

    # --- Misura spaziale: passata separata e profilata con tracemalloc ---
    # Limitata nel tempo per non raddoppiare il costo delle esecuzioni che raggiungono
    # il tempo limite; il picco di memoria si stabilizza presto, poiché il ritracciamento
    # sul posto mantiene l'occupazione a O(profondità) più la chiusura corrente.
    mem_state = grid.state.copy()
    mem_start = time.time()
    tracemalloc.start()
    try:
        camminomin(
            origin, destination, mem_state, depth=0, stats=None,
            start_time=mem_start, timeout=min(timeout, 3.0),
            use_strong_pruning=use_strong_pruning,
            randomize_frontier=randomize_frontier
        )
    except Exception:
        pass
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "path_length": float(l_min) if not np.isinf(l_min) else float('inf'),
        "landmarks_count": len(landmarks),
        "landmarks": landmarks,
        "timed_out": timed_out,
        "elapsed_time_s": elapsed,
        "peak_memory_kb": peak / 1024.0,
        "frontier_cells": stats.get('frontier_cells', 0),
        "pruning_false": stats.get('pruning_false', 0),
        "recursive_calls": stats.get('recursive_calls', 0),
        "max_depth": stats.get('max_depth', 0)
    }


def run_benchmark_coppia(
    grid: Grid,
    origin: Coordinate,
    destination: Coordinate,
    use_strong_pruning: bool = True,
    randomize_frontier: bool = False,
    timeout: float = 30.0
) -> dict[str, object]:
    """
    Esegue il riscontro completo su una coppia: invocazione O→D e D→O.

    La doppia invocazione con parametri scambiati è la verifica di correttezza richiesta
    dalla specifica: le due lunghezze minime devono coincidere.

    Returns:
        Dizionario con le metriche di andata, di ritorno e l'esito della verifica di simmetria.
    """
    andata = run_single_benchmark(
        grid, origin, destination,
        use_strong_pruning=use_strong_pruning,
        randomize_frontier=randomize_frontier,
        timeout=timeout
    )
    ritorno = run_single_benchmark(
        grid, destination, origin,
        use_strong_pruning=use_strong_pruning,
        randomize_frontier=randomize_frontier,
        timeout=timeout
    )

    verificabile = not (andata["timed_out"] or ritorno["timed_out"])
    simmetria_ok = True
    if verificabile:
        l_od, l_do = andata["path_length"], ritorno["path_length"]
        if not (np.isinf(l_od) and np.isinf(l_do)):
            simmetria_ok = abs(l_od - l_do) <= 1e-9
            if not simmetria_ok:
                logger.error(
                    f"SIMMETRIA FALLITA su {origin}↔{destination}: "
                    f"O→D={l_od:.6f}, D→O={l_do:.6f}"
                )

    return {
        "origine": origin,
        "destinazione": destination,
        "andata": andata,
        "ritorno": ritorno,
        "simmetria_verificabile": verificabile,
        "simmetria_ok": simmetria_ok
    }


def run_campaign(output_dir: str = "results") -> None:
    """
    Esegue l'intera campagna di sperimentazione programmata e salva risultati e grafici.

    Campagne eseguite:
      1. Scaling delle prestazioni al crescere della dimensione (fino a 150x150).
      2. Prestazioni in funzione della densità degli ostacoli.
      3. Confronto potatura debole contro forte su tutti i tipi di ostacolo.
      4. Confronto ordinamento euristico contro casuale della frontiera.
      5. Test di simmetria per ogni tipologia di ostacolo su griglie 20x20.

    Args:
        output_dir: Cartella di destinazione per JSON e immagini PNG.
    """
    os.makedirs(output_dir, exist_ok=True)
    logger.info("Avvio della Campagna Sperimentale in corso...")

    # -------------------------------------------------------------- #
    # 1. Scalabilità con la dimensione della griglia: 10 → 150       #
    # -------------------------------------------------------------- #
    # La taglia 200x200 e' stata esclusa: entrambe le potature esauriscono il tempo
    # limite senza trovare alcun cammino completo, quindi non aggiunge informazione
    # rispetto alla 150x150 (si veda la nota metodologica del Compito 4).
    # Tempo limite di 600s (10 minuti): non costa nulla sulle taglie piccole (già
    # istantanee) e dà una possibilità reale a quelle grandi di completare, per
    # distinguere un limite strutturale dell'algoritmo da un semplice budget insufficiente.
    # Si confrontano la potatura debole (riga 16) e quella forte (riga 17); la configurazione
    # forte è eseguita in entrambe le direzioni (O→D e D→O) per la verifica di correttezza
    # richiesta dalla specifica.
    sizes = [10, 20, 30, 50, 100, 150]
    scaling_timeout = 600.0
    scaling_results: list[dict[str, object]] = []

    for size in sizes:
        logger.info(f"  Benchmark dimensione: {size}x{size}...")
        grid = GridGenerator.generate_grid(
            size, size, ["simple", "cluster", "bar"], density=0.2, seed=42
        )
        o: Coordinate = (0, 0)
        d: Coordinate = (size - 1, size - 1)
        grid.clear_cell(o[0], o[1])
        grid.clear_cell(d[0], d[1])

        res_weak = run_single_benchmark(grid, o, d, use_strong_pruning=False, timeout=scaling_timeout)
        coppia = run_benchmark_coppia(grid, o, d, use_strong_pruning=True, timeout=scaling_timeout)

        scaling_results.append({
            "size": size,
            "weak": res_weak,
            "strong": coppia["andata"],
            "ritorno": coppia["ritorno"],
            "simmetria_verificabile": coppia["simmetria_verificabile"],
            "simmetria_ok": coppia["simmetria_ok"]
        })

    with open(os.path.join(output_dir, "scaling_results.json"), "w", encoding='utf-8') as f:
        json.dump(scaling_results, f, indent=2, default=str)

    # -------------------------------------------------------------- #
    # 2. Prestazioni in funzione della densità di ostacoli           #
    # -------------------------------------------------------------- #
    # Per ogni densità si campionano più coppie casuali (oltre alla coppia
    # d'angolo, la più difficile) e si aggregano le metriche per mediana.
    # Ogni coppia è invocata in entrambe le direzioni. La campagna è
    # ripetuta su due taglie di griglia (50x50 e 100x100) per verificare se alle
    # densità più alte una griglia più grande produca tempi oltre il secondo.
    densities = [0.05, 0.15, 0.25, 0.35, 0.45]
    density_sizes = [50, 100]
    density_results: list[dict[str, object]] = []
    n_coppie_casuali = 4
    rng_coppie = np.random.default_rng(7)

    for size in density_sizes:
        for dens in densities:
            logger.info(f"  Benchmark densità: {dens:.2f} (griglia {size}x{size})...")
            grid = GridGenerator.generate_grid(
                size, size, ["simple", "cluster"], density=dens, seed=100
            )
            grid.clear_cell(0, 0)
            grid.clear_cell(size - 1, size - 1)
            coppie = [((0, 0), (size - 1, size - 1))]
            coppie += _coppie_casuali(grid, n_coppie_casuali, rng_coppie)

            dettagli = [
                run_benchmark_coppia(grid, o, d, use_strong_pruning=True, timeout=20.0)
                for o, d in coppie
            ]
            density_results.append({
                "size": size,
                "density": dens,
                "metrics": _mediana_metriche([c["andata"] for c in dettagli]),
                "coppie": dettagli,
                "simmetrie_fallite": sum(1 for c in dettagli if not c["simmetria_ok"])
            })

    with open(os.path.join(output_dir, "density_results.json"), "w", encoding='utf-8') as f:
        json.dump(density_results, f, indent=2, default=str)

    # -------------------------------------------------------------- #
    # 3. Confronto potatura debole (riga 16) contro forte (riga 17)  #
    # -------------------------------------------------------------- #
    obstacle_scenarios = ["simple", "cluster", "diagonal", "enclosure", "bar"]
    pruning_comp: list[dict[str, object]] = []

    rng_pruning = np.random.default_rng(13)
    for scenario in obstacle_scenarios:
        logger.info(f"  Benchmark potatura, tipo ostacolo: {scenario}...")
        grid = GridGenerator.generate_grid(50, 50, [scenario], density=0.2, seed=2026)
        grid.clear_cell(0, 0)
        grid.clear_cell(49, 49)
        coppie = [((0, 0), (49, 49))]
        coppie += _coppie_casuali(grid, n_coppie_casuali, rng_pruning)

        campioni_weak: list[dict[str, object]] = []
        dettagli_strong: list[dict[str, object]] = []
        for o, d in coppie:
            campioni_weak.append(
                run_single_benchmark(grid, o, d, use_strong_pruning=False, timeout=20.0)
            )
            # La doppia invocazione O↔D avviene sulla configurazione forte
            dettagli_strong.append(
                run_benchmark_coppia(grid, o, d, use_strong_pruning=True, timeout=20.0)
            )

        pruning_comp.append({
            "obstacle_type": scenario,
            "weak": _mediana_metriche(campioni_weak),
            "strong": _mediana_metriche([c["andata"] for c in dettagli_strong]),
            "campioni_weak": campioni_weak,
            "coppie_strong": dettagli_strong,
            "simmetrie_fallite": sum(1 for c in dettagli_strong if not c["simmetria_ok"]),
            "coppie": coppie
        })

    with open(os.path.join(output_dir, "pruning_comparison.json"), "w", encoding='utf-8') as f:
        json.dump(pruning_comp, f, indent=2, default=str)

    # -------------------------------------------------------------- #
    # 4. Confronto ordinamento della frontiera: euristico contro     #
    # casuale, sull'ordine di visita dei candidati di frontiera      #
    # -------------------------------------------------------------- #
    ordering_comp: list[dict[str, object]] = []

    for risultato_pruning in pruning_comp:
        scenario = risultato_pruning["obstacle_type"]
        logger.info(f"  Benchmark ordinamento, tipo ostacolo: {scenario}...")
        grid = GridGenerator.generate_grid(50, 50, [scenario], density=0.2, seed=2026)
        grid.clear_cell(0, 0)
        grid.clear_cell(49, 49)

        # Stesse coppie della campagna di potatura: l'ordinamento euristico con
        # potatura forte coincide con la configurazione "strong" già misurata.
        coppie = risultato_pruning["coppie"]
        campioni_random = [
            run_single_benchmark(
                grid, o, d,
                use_strong_pruning=True,
                randomize_frontier=True,
                timeout=20.0
            )
            for o, d in coppie
        ]

        ordering_comp.append({
            "obstacle_type": scenario,
            "heuristic": risultato_pruning["strong"],
            "random": _mediana_metriche(campioni_random),
            "campioni_random": campioni_random
        })

    with open(os.path.join(output_dir, "ordering_comparison.json"), "w", encoding='utf-8') as f:
        json.dump(ordering_comp, f, indent=2, default=str)

    # --------------------------------------------------------------   #
    # 5. Test di simmetria per ogni tipologia di ostacolo:             #
    # algoritmo invocato due volte con parametri invertiti             #
    # --------------------------------------------------------------   #
    run_symmetry_per_type(output_dir=output_dir, n_pairs=5, grid_size=20)

    # -------------------------------------------------------------- #
    # Riassunto complessivo della verifica di simmetria              #
    # su tutte le coppie considerate nelle campagne precedenti        #
    # -------------------------------------------------------------- #
    esiti: list[tuple[bool, bool]] = []
    esiti += [(r["simmetria_verificabile"], r["simmetria_ok"]) for r in scaling_results]
    for r in density_results:
        esiti += [(c["simmetria_verificabile"], c["simmetria_ok"]) for c in r["coppie"]]
    for r in pruning_comp:
        esiti += [(c["simmetria_verificabile"], c["simmetria_ok"]) for c in r["coppie_strong"]]

    riassunto_simmetria = {
        "coppie_totali": len(esiti),
        "verificabili": sum(1 for v, _ in esiti if v),
        "escluse_per_tempo_limite": sum(1 for v, _ in esiti if not v),
        "fallite": sum(1 for v, ok in esiti if v and not ok)
    }
    with open(os.path.join(output_dir, "simmetria_campagna.json"), "w", encoding='utf-8') as f:
        json.dump(riassunto_simmetria, f, indent=2, ensure_ascii=False)
    logger.info(
        f"Verifica di simmetria sulle coppie delle campagne: "
        f"{riassunto_simmetria['verificabili']}/{riassunto_simmetria['coppie_totali']} verificabili, "
        f"{riassunto_simmetria['fallite']} fallimenti."
    )

    # -------------------------------------------------------------- #
    # Generazione grafici                                            #
    # -------------------------------------------------------------- #
    generate_plots(
        scaling_results, density_results, pruning_comp, ordering_comp,
        output_dir
    )
    logger.info(f"Campagna sperimentale completata. Grafici salvati in: {output_dir}")
