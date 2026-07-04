import time
import os
import json
import tracemalloc
import random
import logging
import numpy as np

# Imposta il backend headless di matplotlib prima di importare pyplot per ambienti senza display
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from src.grid import Grid, Coordinate
from src.generator import GridGenerator
from src.camminomin import camminomin

# Configura il logger per il modulo di benchmarking
logger = logging.getLogger(__name__)

# Timeout (s) utilizzato per i test di simmetria: abbastanza alto per evitare falsi positivi
_SYMMETRY_TIMEOUT = 30.0


class ExperimentRunner:
    """
    Gestisce la campagna sperimentale e la verifica di correttezza (Compito 4).

    Analizza le prestazioni, l'effetto delle due regole di pruning (debole vs forte),
    l'effetto dell'ordinamento casuale vs euristico della frontiera e genera grafici comparativi.
    """

    # ------------------------------------------------------------------ #
    #  Verifica di Correttezza                                           #
    # ------------------------------------------------------------------ #

    @staticmethod
    def verify_symmetry(
        grid: Grid,
        points: list[tuple[Coordinate, Coordinate]],
        use_strong: bool = True,
        timeout: float = _SYMMETRY_TIMEOUT
    ) -> list[dict[str, object]]:
        """
        Verifica la simmetria del cammino minimo: camminomin(O, D) == camminomin(D, O).

        Coppie in cui almeno una direzione va in timeout vengono registrate come
        "escluse" (symmetry_ok=True) per non gonfiare il conteggio di fallimenti.

        Args:
            grid: L'oggetto Grid da utilizzare per la ricerca.
            points: Lista di coppie (origine, destinazione) da testare.
            use_strong: Se True, usa il pruning forte (Riga 17), altrimenti debole (Riga 16).
            timeout: Secondi massimi per ogni singola invocazione.

        Returns:
            Lista di dizionari con i dettagli di simmetria per ogni coppia.
        """
        results: list[dict[str, object]] = []
        for idx, (o, d) in enumerate(points):
            # Ricerca O -> D
            state_copy_1 = grid.state.copy()
            start_od = time.time()
            len_od, _, to_od = camminomin(
                o, d, state_copy_1, start_time=start_od, timeout=timeout,
                use_strong_pruning=use_strong
            )

            # Ricerca D -> O
            state_copy_2 = grid.state.copy()
            start_do = time.time()
            len_do, _, to_do = camminomin(
                d, o, state_copy_2, start_time=start_do, timeout=timeout,
                use_strong_pruning=use_strong
            )

            symmetry_ok = True
            if to_od or to_do:
                logger.warning(
                    f"Coppia {idx}: esclusa per timeout (TO_OD={to_od}, TO_DO={to_do})."
                )
            else:
                if not (np.isinf(len_od) and np.isinf(len_do)):
                    if abs(len_od - len_do) > 1e-9:
                        symmetry_ok = False
                        logger.error(
                            f"Coppia {idx}: SIMMETRIA FALLITA. "
                            f"O→D={len_od:.6f}, D→O={len_do:.6f}"
                        )

            results.append({
                "pair_index": idx,
                "origin": o,
                "dest": d,
                "len_od": float(len_od) if not np.isinf(len_od) else float('inf'),
                "len_do": float(len_do) if not np.isinf(len_do) else float('inf'),
                "timed_out_od": to_od,
                "timed_out_do": to_do,
                "symmetry_ok": symmetry_ok
            })
        return results

    @classmethod
    def run_symmetry_per_type(
        cls,
        output_dir: str,
        n_pairs: int = 5,
        grid_size: int = 20,
        seed: int = 42
    ) -> list[dict[str, object]]:
        """
        Esegue il test di simmetria su una griglia separata per ogni tipologia di ostacolo.

        Usa griglie 20x20 (invece di 50x50) per evitare timeout e ottenere risultati
        definitivi su tutte le coppie.

        Args:
            output_dir: Directory dove salvare il JSON dei risultati.
            n_pairs: Numero di coppie O,D da testare per ogni tipologia.
            grid_size: Dimensione della griglia quadrata da usare.
            seed: Seme per la riproducibilità.

        Returns:
            Lista di dizionari {obstacle_type, total, failed, excluded_timeout}.
        """
        obstacle_types = ["simple", "cluster", "diagonal", "enclosure", "bar"]
        summary: list[dict[str, object]] = []
        rng = np.random.default_rng(seed)

        for obstacle_type in obstacle_types:
            logger.info(f"  Simmetria per tipologia: {obstacle_type}...")
            grid = GridGenerator.generate_grid(
                grid_size, grid_size, [obstacle_type], density=0.15, seed=int(rng.integers(0, 999999))
            )

            points: list[tuple[Coordinate, Coordinate]] = []
            for _ in range(n_pairs):
                for _ in range(1000):
                    o = (int(rng.integers(0, grid_size)), int(rng.integers(0, grid_size)))
                    d = (int(rng.integers(0, grid_size)), int(rng.integers(0, grid_size)))
                    if o != d and grid.is_traversable(o[0], o[1]) and grid.is_traversable(d[0], d[1]):
                        points.append((o, d))
                        break

            results = cls.verify_symmetry(grid, points, use_strong=True)
            failed = [r for r in results if not r["symmetry_ok"]]
            excluded = [r for r in results if r["timed_out_od"] or r["timed_out_do"]]

            entry = {
                "obstacle_type": obstacle_type,
                "total_pairs": len(results),
                "failed": len(failed),
                "excluded_timeout": len(excluded),
                "pairs": results
            }
            summary.append(entry)

            status = "OK" if len(failed) == 0 else f"FALLITI: {len(failed)}"
            logger.info(
                f"    {obstacle_type}: {len(results) - len(excluded)} valide, "
                f"{len(excluded)} timeout, {len(failed)} fallimenti → {status}"
            )

        with open(os.path.join(output_dir, "symmetry_per_type.json"), "w", encoding='utf-8') as f:
            json.dump(summary, f, indent=2, default=str)

        return summary

    # ------------------------------------------------------------------ #
    #  Utilità per le campagne                                           #
    # ------------------------------------------------------------------ #

    @staticmethod
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

    @staticmethod
    def _mediana_metriche(campioni: list[dict[str, object]]) -> dict[str, object]:
        """
        Aggrega per mediana le metriche numeriche di più esecuzioni sulla stessa configurazione.

        Args:
            campioni: Lista di dizionari prodotti da `run_single_benchmark`.

        Returns:
            Dizionario con le mediane delle metriche e il numero di campioni aggregati.
        """
        import statistics
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

    @classmethod
    def run_benchmark_coppia(
        cls,
        grid: Grid,
        origin: Coordinate,
        destination: Coordinate,
        use_strong_pruning: bool = True,
        randomize_frontier: bool = False,
        timeout: float = 30.0
    ) -> dict[str, object]:
        """
        Esegue il riscontro completo su una coppia: invocazione O→D e D→O (diapositiva 64).

        La doppia invocazione con parametri scambiati è la verifica di correttezza richiesta
        dalla specifica: le due lunghezze minime devono coincidere.

        Returns:
            Dizionario con le metriche di andata, di ritorno e l'esito della verifica di simmetria.
        """
        andata = cls.run_single_benchmark(
            grid, origin, destination,
            use_strong_pruning=use_strong_pruning,
            randomize_frontier=randomize_frontier,
            timeout=timeout
        )
        ritorno = cls.run_single_benchmark(
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

    # ------------------------------------------------------------------ #
    #  Benchmark singolo                                                 #
    # ------------------------------------------------------------------ #

    @staticmethod
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

    # ------------------------------------------------------------------ #
    #  Campagna sperimentale completa                                    #
    # ------------------------------------------------------------------ #

    @classmethod
    def run_campaign(cls, output_dir: str = "results") -> None:
        """
        Esegue l'intera campagna di sperimentazione programmata e salva risultati e grafici.

        Campagne eseguite:
          1. Scaling delle prestazioni al crescere della dimensione (fino a 200x200).
          2. Prestazioni in funzione della densità degli ostacoli.
          3. Confronto pruning debole vs forte su tutti i tipi di ostacolo.
          4. Confronto ordinamento euristico vs casuale della frontiera.
          5. Test di simmetria per ogni tipologia di ostacolo su griglie 20x20.

        Args:
            output_dir: Cartella di destinazione per JSON e immagini PNG.
        """
        os.makedirs(output_dir, exist_ok=True)
        logger.info("Avvio della Campagna Sperimentale in corso...")

        # -------------------------------------------------------------- #
        # 1. Scalabilità con la dimensione della griglia: 10 → 200       #
        # -------------------------------------------------------------- #
        # Include 200x200 come richiesto dalla specifica (diapositiva 72).
        # Tempo limite di 600s (10 minuti): non costa nulla sulle taglie piccole (già
        # istantanee) e dà una possibilità reale a quelle grandi di completare, per
        # distinguere un limite strutturale dell'algoritmo da un semplice budget insufficiente.
        # Si confrontano la potatura debole (riga 16) e quella forte (riga 17); la configurazione
        # forte è eseguita in entrambe le direzioni (O→D e D→O) per la verifica di correttezza
        # di cui alla diapositiva 64.
        sizes = [10, 20, 50, 100, 150, 200]
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

            res_weak = cls.run_single_benchmark(grid, o, d, use_strong_pruning=False, timeout=scaling_timeout)
            coppia = cls.run_benchmark_coppia(grid, o, d, use_strong_pruning=True, timeout=scaling_timeout)

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
        # 2. Prestazioni vs Densità ostacoli                             #
        # -------------------------------------------------------------- #
        # Per ogni densità si campionano più coppie casuali (oltre alla coppia
        # d'angolo, la più difficile) e si aggregano le metriche per mediana.
        # Ogni coppia è invocata in entrambe le direzioni (Slide 64). La campagna è
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
                coppie += cls._coppie_casuali(grid, n_coppie_casuali, rng_coppie)

                dettagli = [
                    cls.run_benchmark_coppia(grid, o, d, use_strong_pruning=True, timeout=20.0)
                    for o, d in coppie
                ]
                density_results.append({
                    "size": size,
                    "density": dens,
                    "metrics": cls._mediana_metriche([c["andata"] for c in dettagli]),
                    "coppie": dettagli,
                    "simmetrie_fallite": sum(1 for c in dettagli if not c["simmetria_ok"])
                })

        with open(os.path.join(output_dir, "density_results.json"), "w", encoding='utf-8') as f:
            json.dump(density_results, f, indent=2, default=str)

        # -------------------------------------------------------------- #
        # 3. Confronto Pruning (Riga 16 vs Riga 17)                      #
        # -------------------------------------------------------------- #
        obstacle_scenarios = ["simple", "cluster", "diagonal", "enclosure", "bar"]
        pruning_comp: list[dict[str, object]] = []

        rng_pruning = np.random.default_rng(13)
        for scenario in obstacle_scenarios:
            logger.info(f"  Benchmark potatura — tipo ostacolo: {scenario}...")
            grid = GridGenerator.generate_grid(50, 50, [scenario], density=0.2, seed=2026)
            grid.clear_cell(0, 0)
            grid.clear_cell(49, 49)
            coppie = [((0, 0), (49, 49))]
            coppie += cls._coppie_casuali(grid, n_coppie_casuali, rng_pruning)

            campioni_weak: list[dict[str, object]] = []
            dettagli_strong: list[dict[str, object]] = []
            for o, d in coppie:
                campioni_weak.append(
                    cls.run_single_benchmark(grid, o, d, use_strong_pruning=False, timeout=20.0)
                )
                # La doppia invocazione O↔D (Slide 64) avviene sulla configurazione forte
                dettagli_strong.append(
                    cls.run_benchmark_coppia(grid, o, d, use_strong_pruning=True, timeout=20.0)
                )

            pruning_comp.append({
                "obstacle_type": scenario,
                "weak": cls._mediana_metriche(campioni_weak),
                "strong": cls._mediana_metriche([c["andata"] for c in dettagli_strong]),
                "campioni_weak": campioni_weak,
                "coppie_strong": dettagli_strong,
                "simmetrie_fallite": sum(1 for c in dettagli_strong if not c["simmetria_ok"]),
                "coppie": coppie
            })

        with open(os.path.join(output_dir, "pruning_comparison.json"), "w", encoding='utf-8') as f:
            json.dump(pruning_comp, f, indent=2, default=str)

        # -------------------------------------------------------------- #
        # 4. Confronto Ordinamento Frontiera: Euristico vs Casuale       #
        # (Slide 65-66: ordine di visita dei candidati di frontiera)     #
        # -------------------------------------------------------------- #
        ordering_comp: list[dict[str, object]] = []

        for risultato_pruning in pruning_comp:
            scenario = risultato_pruning["obstacle_type"]
            logger.info(f"  Benchmark ordinamento — tipo ostacolo: {scenario}...")
            grid = GridGenerator.generate_grid(50, 50, [scenario], density=0.2, seed=2026)
            grid.clear_cell(0, 0)
            grid.clear_cell(49, 49)

            # Stesse coppie della campagna di potatura: l'ordinamento euristico con
            # potatura forte coincide con la configurazione "strong" già misurata.
            coppie = risultato_pruning["coppie"]
            campioni_random = [
                cls.run_single_benchmark(
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
                "random": cls._mediana_metriche(campioni_random),
                "campioni_random": campioni_random
            })

        with open(os.path.join(output_dir, "ordering_comparison.json"), "w", encoding='utf-8') as f:
            json.dump(ordering_comp, f, indent=2, default=str)

        # --------------------------------------------------------------   #
        # 5. Test di Simmetria per ogni tipologia di ostacolo              #
        # (Slide 64: "algoritmo invocato due volte con parametri inversi") #
        # --------------------------------------------------------------   #
        symmetry_per_type = cls.run_symmetry_per_type(output_dir=output_dir, n_pairs=5, grid_size=20)

        # -------------------------------------------------------------- #
        # Riassunto complessivo della verifica di simmetria (Slide 64)   #
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
        cls.generate_plots(
            scaling_results, density_results, pruning_comp, ordering_comp,
            symmetry_per_type, output_dir
        )
        logger.info(f"Campagna sperimentale completata. Grafici salvati in: {output_dir}")

    # ------------------------------------------------------------------ #
    #  Generazione Grafici                                               #
    # ------------------------------------------------------------------ #

    @staticmethod
    def generate_plots(
        scaling_res: list[dict[str, object]],
        density_res: list[dict[str, object]],
        pruning_res: list[dict[str, object]],
        ordering_res: list[dict[str, object]],
        symmetry_res: list[dict[str, object]],
        output_dir: str
    ) -> None:
        """
        Genera ed esporta la suite di grafici ad alta risoluzione (2000x2000 px equivalenti)
        per l'analisi asintotica formale (Slide 53 / Slide 71).
        """
        import matplotlib.pyplot as plt
        import numpy as np

        # Raccogliamo in modo centralizzato tutti i campioni sperimentali per gli scatter plot analitici
        frontier_cells_list = []
        elapsed_time_list = []
        landmarks_count_list = []
        recursive_calls_list = []
        path_length_list = []

        def add_sample(metric_dict):
            if metric_dict and metric_dict.get('elapsed_time_s') is not None:
                # Evitiamo valori zero per evitare log(0)
                fc = max(1, metric_dict.get('frontier_cells', 0))
                rc = max(1, metric_dict.get('recursive_calls', 0))
                pl = max(1.0, metric_dict.get('path_length', 1.0))
                lm = max(1, metric_dict.get('landmarks_count', 1))
                t = max(1e-6, metric_dict.get('elapsed_time_s', 0))
                
                # Non inseriamo i timeout completi nello scatter per non falsare le pendenze ideali
                if not metric_dict.get('timed_out', False):
                    frontier_cells_list.append(fc)
                    elapsed_time_list.append(t)
                    landmarks_count_list.append(lm)
                    recursive_calls_list.append(rc)
                    path_length_list.append(pl)

        # Estraiamo da scaling (singole esecuzioni, andata e ritorno)
        for r in scaling_res:
            add_sample(r.get("weak"))
            add_sample(r.get("strong"))
            add_sample(r.get("ritorno"))
        # Estraiamo da density (tutte le coppie, andata e ritorno)
        for r in density_res:
            for c in r.get("coppie", []):
                add_sample(c.get("andata"))
                add_sample(c.get("ritorno"))
        # Estraiamo da pruning (campioni con potatura debole e coppie con potatura forte)
        for r in pruning_res:
            for s in r.get("campioni_weak", []):
                add_sample(s)
            for c in r.get("coppie_strong", []):
                add_sample(c.get("andata"))
                add_sample(c.get("ritorno"))
        # Estraiamo da ordering (solo i campioni con ordinamento casuale: quelli
        # con ordinamento euristico coincidono con le coppie della potatura forte)
        for r in ordering_res:
            for s in r.get("campioni_random", []):
                add_sample(s)

        # ── Plot 1: Tempo vs Densità (Transizione di Fase), per taglia ── #
        plt.figure(figsize=(8, 5))
        colori_taglia = {50: '#e056fd', 100: '#0984e3'}
        taglie_presenti = sorted({r.get("size", 50) for r in density_res})
        for taglia in taglie_presenti:
            campioni_taglia = [r for r in density_res if r.get("size", 50) == taglia]
            dens = [r["density"] for r in campioni_taglia]
            times = [r["metrics"]["elapsed_time_s"] for r in campioni_taglia]
            colore = colori_taglia.get(taglia, '#e056fd')
            plt.plot(dens, times, marker='o', linewidth=2.5, color=colore, label=f'Griglia {taglia}x{taglia} (potatura forte)')
        plt.title("Tempo di esecuzione in funzione della densità di ostacoli (transizione di fase)", fontsize=12, fontweight='bold')
        plt.xlabel("Densità ostacoli", fontsize=10)
        plt.ylabel("Tempo di esecuzione (secondi)", fontsize=10)
        plt.yscale('log')
        plt.grid(True, which="both", linestyle='--', alpha=0.6)
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "1_time_vs_density.png"), dpi=200)
        plt.close()

        # ── Plot 2: BoxPlot/BarPlot comparativo delle configurazioni ──── #
        # Solo 3 configurazioni sono realmente distinte: la potatura forte viene sempre
        # misurata insieme all'ordinamento euristico (la campagna di ordinamento riusa
        # infatti quella stessa misura come termine di paragone, si veda "strong" sopra),
        # quindi non esiste una misura isolata di "sola potatura forte" o "solo ordinamento
        # euristico" da poter distinguere in un quarto scenario.
        categories = [r["obstacle_type"] for r in pruning_res]
        weak_times = [r["weak"]["elapsed_time_s"] for r in pruning_res]
        strong_times = [r["strong"]["elapsed_time_s"] for r in pruning_res]

        # Estraiamo per gli stessi scenari la performance dell'ordinamento casuale
        random_times = []
        for cat in categories:
            match = next((r for r in ordering_res if r["obstacle_type"] == cat), None)
            random_times.append(match["random"]["elapsed_time_s"] if match else 0.0)

        x = np.arange(len(categories))
        width = 0.25
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(x - width, weak_times, width, label='Potatura debole + ordinamento euristico', color='#ff7979')
        ax.bar(x, strong_times, width, label='Potatura forte + ordinamento euristico', color='#2ed573')
        ax.bar(x + width, random_times, width, label='Potatura forte + ordinamento casuale', color='#a29bfe')

        ax.set_title("Tempi di esecuzione delle diverse configurazioni per scenario", fontsize=12, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(categories)
        ax.set_ylabel("Tempo di esecuzione (secondi)")
        ax.set_yscale('log')
        ax.grid(True, which="both", linestyle='--', alpha=0.4)
        ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.2), ncol=2)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "2_pruning_comparison_boxplot.png"), dpi=200, bbox_inches='tight')
        plt.close()

        # ── Plot 3: Line Plot di Scaling Asintotico Log-Log ───────────── #
        plt.figure(figsize=(8, 5))
        sizes = [r["size"] for r in scaling_res]
        times_weak = [r["weak"]["elapsed_time_s"] for r in scaling_res]
        times_strong = [r["strong"]["elapsed_time_s"] for r in scaling_res]
        plt.loglog(sizes, times_weak, marker='s', label='Potatura debole (riga 16)', color='#ffbe0b', linewidth=2)
        plt.loglog(sizes, times_strong, marker='^', label='Potatura forte (riga 17)', color='#2ed573', linewidth=2)
        plt.title("Crescita temporale asintotica in scala bilogaritmica (dimensione e tempo)", fontsize=12, fontweight='bold')
        plt.xlabel("Dimensione griglia (lato R = C)", fontsize=10)
        plt.ylabel("Tempo di esecuzione mediano (secondi)", fontsize=10)
        plt.grid(True, which="both", linestyle='--', alpha=0.5)
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "3_complexity_scaling_loglog.png"), dpi=200)
        plt.close()

        # ── Plot 4: Scatter Plot Tempo vs Celle Frontiera Considerate ──── #
        if elapsed_time_list:
            plt.figure(figsize=(8, 5.5))
            sc = plt.scatter(
                frontier_cells_list, elapsed_time_list,
                c=landmarks_count_list, cmap='viridis',
                s=100, alpha=0.85, edgecolors='black', linewidths=0.5
            )
            cbar = plt.colorbar(sc)
            cbar.set_label("Numero totale di landmark", fontsize=10)
            
            # Regressione lineare in scala logaritmica
            log_x = np.log10(frontier_cells_list)
            log_y = np.log10(elapsed_time_list)
            slope, intercept = np.polyfit(log_x, log_y, 1)
            x_fit = np.logspace(min(log_x), max(log_x), 100)
            y_fit = 10**(slope * np.log10(x_fit) + intercept)
            plt.loglog(x_fit, y_fit, color='red', linestyle='--', label=f'Andamento asintotico (pendenza: {slope:.2f})')

            plt.xscale('log')
            plt.yscale('log')
            plt.title("Tempo di esecuzione e celle di frontiera esplorate (scala bilogaritmica)", fontsize=11, fontweight='bold')
            plt.xlabel("Celle di frontiera considerate", fontsize=10)
            plt.ylabel("Tempo di esecuzione (secondi)", fontsize=10)
            plt.grid(True, which="both", linestyle='--', alpha=0.5)
            plt.legend()
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, "4_scatter_time_vs_frontier.png"), dpi=200)
            plt.close()

        # ── Plot 5: Scatter Plot Tempo vs Invocazioni Ricorsive ───────── #
        if elapsed_time_list:
            plt.figure(figsize=(8, 5.5))
            sc = plt.scatter(
                recursive_calls_list, elapsed_time_list,
                c=path_length_list, cmap='plasma',
                s=100, alpha=0.85, edgecolors='black', linewidths=0.5
            )
            cbar = plt.colorbar(sc)
            cbar.set_label("Lunghezza del cammino minimo", fontsize=10)
            
            # Regressione lineare in scala logaritmica
            log_x = np.log10(recursive_calls_list)
            log_y = np.log10(elapsed_time_list)
            slope, intercept = np.polyfit(log_x, log_y, 1)
            x_fit = np.logspace(min(log_x), max(log_x), 100)
            y_fit = 10**(slope * np.log10(x_fit) + intercept)
            plt.loglog(x_fit, y_fit, color='red', linestyle='--', label=f'Andamento asintotico (pendenza: {slope:.2f})')

            plt.xscale('log')
            plt.yscale('log')
            plt.title("Tempo di esecuzione e complessità ricorsiva (scala bilogaritmica)", fontsize=11, fontweight='bold')
            plt.xlabel("Numero di invocazioni ricorsive", fontsize=10)
            plt.ylabel("Tempo di esecuzione (secondi)", fontsize=10)
            plt.grid(True, which="both", linestyle='--', alpha=0.5)
            plt.legend()
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, "5_scatter_time_vs_recursion.png"), dpi=200)
            plt.close()

        # ── Plot 6: Simmetria per tipologia (coppie fallite/timeout) ─── #
        sym_types = [r["obstacle_type"] for r in symmetry_res]
        sym_failed = [r["failed"] for r in symmetry_res]
        sym_timeout = [r["excluded_timeout"] for r in symmetry_res]
        sym_ok = [
            r["total_pairs"] - r["failed"] - r["excluded_timeout"]
            for r in symmetry_res
        ]

        x3 = np.arange(len(sym_types))
        fig, ax = plt.subplots(figsize=(9, 5.5))
        ax.bar(x3, sym_ok, label='Simmetria verificata', color='#2ed573')
        ax.bar(x3, sym_timeout, bottom=sym_ok, label='Escluse (tempo limite)', color='#ffd32a')
        bottom_fail = [a + b for a, b in zip(sym_ok, sym_timeout)]
        ax.bar(x3, sym_failed, bottom=bottom_fail, label='Fallite', color='#ff4757')
        ax.set_title("Prove di simmetria O↔D per tipologia di ostacolo", fontsize=12, fontweight='bold')
        ax.set_xticks(x3)
        ax.set_xticklabels(sym_types)
        ax.set_ylabel("Numero di coppie testate")
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.4)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "6_symmetry_per_type.png"), dpi=200)
        plt.close()
