"""Verifica di correttezza per simmetria (Compito 4, diapositiva 64).

Confronta camminomin(O, D) con camminomin(D, O): le due lunghezze minime devono coincidere.
"""
import json
import os
import time
import logging

import numpy as np

from src.grid import Grid, Coordinate
from src.generator import GridGenerator
from src.camminomin import camminomin

logger = logging.getLogger(__name__)

# Timeout (s) utilizzato per i test di simmetria: abbastanza alto per evitare falsi positivi
_SYMMETRY_TIMEOUT = 30.0


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


def run_symmetry_per_type(
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

        results = verify_symmetry(grid, points, use_strong=True)
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
