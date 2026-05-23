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
    #  Benchmark singolo                                                 #
    # ------------------------------------------------------------------ #

    @staticmethod
    def run_single_benchmark(
        grid: Grid,
        origin: Coordinate,
        destination: Coordinate,
        use_strong_pruning: bool = False,
        randomize_frontier: bool = False,
        timeout: float = 30.0,
        disable_seed: bool = False
    ) -> dict[str, object]:
        """
        Esegue un singolo benchmark di cammino minimo con raccolta di metriche.

        Args:
            grid: L'oggetto Griglia.
            origin: Coordinata di partenza.
            destination: Coordinata di arrivo.
            use_strong_pruning: Se True, abilita la potatura forte (Riga 17).
            randomize_frontier: Se True, ordina la frontiera casualmente anziché euristicamente.
            timeout: Tempo limite di esecuzione in secondi.
            disable_seed: Se True, disabilita il seed del minimo globale (Greedy Seeding).

        Returns:
            Dizionario con metriche di percorso, tempo, memoria e nodi esplorati.
        """
        state_copy = grid.state.copy()

        tracemalloc.start()
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
                randomize_frontier=randomize_frontier,
                disable_seed=disable_seed
            )
        except Exception as e:
            logger.error(f"Errore critico durante benchmark: {e}", exc_info=True)
            l_min, landmarks, timed_out = float('inf'), [], False

        elapsed = time.time() - start_time
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
        # 1. Scaling dimensione griglia: 10 → 200                        #
        # -------------------------------------------------------------- #
        # Include 200x200 come richiesto dalla specifica (Slide 72).
        # Timeout generoso (60s) per dare una chance anche alla griglia più grande.
        sizes = [10, 20, 50, 100, 150, 200]
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

            res_weak = cls.run_single_benchmark(grid, o, d, use_strong_pruning=False, timeout=60.0, disable_seed=True)
            res_strong_no_seed = cls.run_single_benchmark(grid, o, d, use_strong_pruning=True, timeout=60.0, disable_seed=True)
            res_strong = cls.run_single_benchmark(grid, o, d, use_strong_pruning=True, timeout=60.0, disable_seed=False)

            scaling_results.append({
                "size": size,
                "weak": res_weak,
                "strong_no_seed": res_strong_no_seed,
                "strong": res_strong
            })

        with open(os.path.join(output_dir, "scaling_results.json"), "w", encoding='utf-8') as f:
            json.dump(scaling_results, f, indent=2, default=str)

        # -------------------------------------------------------------- #
        # 2. Prestazioni vs Densità ostacoli                             #
        # -------------------------------------------------------------- #
        densities = [0.05, 0.15, 0.25, 0.35, 0.45]
        density_results: list[dict[str, object]] = []
        size = 50

        for dens in densities:
            logger.info(f"  Benchmark densità: {dens:.2f}...")
            grid = GridGenerator.generate_grid(
                size, size, ["simple", "cluster"], density=dens, seed=100
            )
            o = (0, 0)
            d = (size - 1, size - 1)
            grid.clear_cell(o[0], o[1])
            grid.clear_cell(d[0], d[1])

            res = cls.run_single_benchmark(grid, o, d, use_strong_pruning=True, timeout=30.0)
            density_results.append({"density": dens, "metrics": res})

        with open(os.path.join(output_dir, "density_results.json"), "w", encoding='utf-8') as f:
            json.dump(density_results, f, indent=2, default=str)

        # -------------------------------------------------------------- #
        # 3. Confronto Pruning (Riga 16 vs Riga 17)                      #
        # -------------------------------------------------------------- #
        obstacle_scenarios = ["simple", "cluster", "diagonal", "enclosure", "bar"]
        pruning_comp: list[dict[str, object]] = []

        for scenario in obstacle_scenarios:
            logger.info(f"  Benchmark pruning — tipo ostacolo: {scenario}...")
            grid = GridGenerator.generate_grid(50, 50, [scenario], density=0.2, seed=2026)
            o = (0, 0)
            d = (49, 49)
            grid.clear_cell(o[0], o[1])
            grid.clear_cell(d[0], d[1])

            res_weak = cls.run_single_benchmark(grid, o, d, use_strong_pruning=False, timeout=30.0)
            res_strong = cls.run_single_benchmark(grid, o, d, use_strong_pruning=True, timeout=30.0)

            pruning_comp.append({
                "obstacle_type": scenario,
                "weak": res_weak,
                "strong": res_strong
            })

        with open(os.path.join(output_dir, "pruning_comparison.json"), "w", encoding='utf-8') as f:
            json.dump(pruning_comp, f, indent=2, default=str)

        # -------------------------------------------------------------- #
        # 4. Confronto Ordinamento Frontiera: Euristico vs Casuale       #
        # (Slide 65-66: ordine di visita dei candidati di frontiera)     #
        # -------------------------------------------------------------- #
        ordering_comp: list[dict[str, object]] = []

        for scenario in obstacle_scenarios:
            logger.info(f"  Benchmark ordinamento — tipo ostacolo: {scenario}...")
            grid = GridGenerator.generate_grid(50, 50, [scenario], density=0.2, seed=2026)
            o = (0, 0)
            d = (49, 49)
            grid.clear_cell(o[0], o[1])
            grid.clear_cell(d[0], d[1])

            # Ordinamento euristico: dlib(f, D) crescente
            res_heuristic = cls.run_single_benchmark(
                grid, o, d,
                use_strong_pruning=True,
                randomize_frontier=False,
                timeout=30.0
            )
            # Ordinamento casuale (seed fisso per riproducibilità)
            res_random = cls.run_single_benchmark(
                grid, o, d,
                use_strong_pruning=True,
                randomize_frontier=True,
                timeout=30.0
            )

            ordering_comp.append({
                "obstacle_type": scenario,
                "heuristic": res_heuristic,
                "random": res_random
            })

        with open(os.path.join(output_dir, "ordering_comparison.json"), "w", encoding='utf-8') as f:
            json.dump(ordering_comp, f, indent=2, default=str)

        # --------------------------------------------------------------   #
        # 5. Test di Simmetria per ogni tipologia di ostacolo              #
        # (Slide 64: "algoritmo invocato due volte con parametri inversi") #
        # --------------------------------------------------------------   #
        symmetry_per_type = cls.run_symmetry_per_type(output_dir=output_dir, n_pairs=5, grid_size=20)

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

        # Estraiamo da scaling
        for r in scaling_res:
            add_sample(r.get("weak"))
            add_sample(r.get("strong_no_seed"))
            add_sample(r.get("strong"))
        # Estraiamo da density
        for r in density_res:
            add_sample(r.get("metrics"))
        # Estraiamo da pruning
        for r in pruning_res:
            add_sample(r.get("weak"))
            add_sample(r.get("strong"))
        # Estraiamo da ordering
        for r in ordering_res:
            add_sample(r.get("heuristic"))
            add_sample(r.get("random"))

        # ── Plot 1: Tempo vs Densità (Transizione di Fase) ────────────── #
        plt.figure(figsize=(8, 5))
        dens = [r["density"] for r in density_res]
        times = [r["metrics"]["elapsed_time_s"] for r in density_res]
        plt.plot(dens, times, marker='o', linewidth=2.5, color='#e056fd', label='CAMMINOMIN (Pruning Forte)')
        plt.title("Tempo di Esecuzione vs Densità Ostacoli (Transizione di Fase)", fontsize=12, fontweight='bold')
        plt.xlabel("Densità Ostacoli", fontsize=10)
        plt.ylabel("Tempo di Esecuzione (secondi)", fontsize=10)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "1_time_vs_density.png"), dpi=200)
        plt.close()

        # ── Plot 2: BoxPlot/BarPlot comparativo delle configurazioni ──── #
        categories = [r["obstacle_type"] for r in pruning_res]
        weak_times = [r["weak"]["elapsed_time_s"] for r in pruning_res]
        strong_times = [r["strong"]["elapsed_time_s"] for r in pruning_res]
        
        # Estraiamo per gli stessi scenari le performance dell'ordinamento
        heuristic_times = []
        random_times = []
        for cat in categories:
            match = next((r for r in ordering_res if r["obstacle_type"] == cat), None)
            if match:
                heuristic_times.append(match["heuristic"]["elapsed_time_s"])
                random_times.append(match["random"]["elapsed_time_s"])
            else:
                heuristic_times.append(0.0)
                random_times.append(0.0)

        x = np.arange(len(categories))
        width = 0.2
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(x - 1.5*width, weak_times, width, label='Pruning Debole (Riga 16)', color='#ff7979')
        ax.bar(x - 0.5*width, strong_times, width, label='Pruning Forte (Riga 17)', color='#2ed573')
        ax.bar(x + 0.5*width, heuristic_times, width, label='Ordinamento Euristico', color='#3a86ff')
        ax.bar(x + 1.5*width, random_times, width, label='Ordinamento Casuale', color='#ff6b6b')
        
        ax.set_title("Tempi di Esecuzione delle Differenti Configurazioni per Scenario", fontsize=12, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(categories)
        ax.set_ylabel("Tempo di Esecuzione (secondi)")
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
        times_strong_no_seed = [r["strong_no_seed"]["elapsed_time_s"] for r in scaling_res]
        times_strong = [r["strong"]["elapsed_time_s"] for r in scaling_res]
        plt.loglog(sizes, times_weak, marker='s', label='Pruning Debole (Base)', color='#ffbe0b', linewidth=2)
        plt.loglog(sizes, times_strong_no_seed, marker='o', label='Pruning Forte + Cache', color='#3a86c8', linewidth=2)
        plt.loglog(sizes, times_strong, marker='^', label='Pruning Forte + Cache + Seeding', color='#2ed573', linewidth=2)
        plt.title("Scaling Asintotico Temporale: Log-Log (Dimensione vs Tempo)", fontsize=12, fontweight='bold')
        plt.xlabel("Dimensione Griglia (Lato R = C)", fontsize=10)
        plt.ylabel("Tempo di Esecuzione Mediano (secondi)", fontsize=10)
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
            cbar.set_label("Numero Totale Landmark", fontsize=10)
            
            # Regressione lineare in scala logaritmica
            log_x = np.log10(frontier_cells_list)
            log_y = np.log10(elapsed_time_list)
            slope, intercept = np.polyfit(log_x, log_y, 1)
            x_fit = np.logspace(min(log_x), max(log_x), 100)
            y_fit = 10**(slope * np.log10(x_fit) + intercept)
            plt.loglog(x_fit, y_fit, color='red', linestyle='--', label=f'Trend Asintotico (pendenza: {slope:.2f})')

            plt.xscale('log')
            plt.yscale('log')
            plt.title("Tempo di Esecuzione vs Celle di Frontiera Esplorate (Scala Log-Log)", fontsize=11, fontweight='bold')
            plt.xlabel("Celle di Frontiera Considerate", fontsize=10)
            plt.ylabel("Tempo di Esecuzione (secondi)", fontsize=10)
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
            cbar.set_label("Lunghezza Cammino Minimo", fontsize=10)
            
            # Regressione lineare in scala logaritmica
            log_x = np.log10(recursive_calls_list)
            log_y = np.log10(elapsed_time_list)
            slope, intercept = np.polyfit(log_x, log_y, 1)
            x_fit = np.logspace(min(log_x), max(log_x), 100)
            y_fit = 10**(slope * np.log10(x_fit) + intercept)
            plt.loglog(x_fit, y_fit, color='red', linestyle='--', label=f'Trend Asintotico (pendenza: {slope:.2f})')

            plt.xscale('log')
            plt.yscale('log')
            plt.title("Tempo di Esecuzione vs Complessità Ricorsiva (Invocazioni) (Scala Log-Log)", fontsize=11, fontweight='bold')
            plt.xlabel("Numero di Invocazioni Ricorsive", fontsize=10)
            plt.ylabel("Tempo di Esecuzione (secondi)", fontsize=10)
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
        ax.bar(x3, sym_ok, label='Simmetria OK', color='#2ed573')
        ax.bar(x3, sym_timeout, bottom=sym_ok, label='Escluse (timeout)', color='#ffd32a')
        bottom_fail = [a + b for a, b in zip(sym_ok, sym_timeout)]
        ax.bar(x3, sym_failed, bottom=bottom_fail, label='FALLITE', color='#ff4757')
        ax.set_title("Test di Simmetria O↔D per Tipologia di Ostacolo", fontsize=12, fontweight='bold')
        ax.set_xticks(x3)
        ax.set_xticklabels(sym_types)
        ax.set_ylabel("Numero di coppie testate")
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.4)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "6_symmetry_per_type.png"), dpi=200)
        plt.close()
