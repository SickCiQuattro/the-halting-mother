#!/usr/bin/env python3
"""Tabella unica di ablation per le due ottimizzazioni di CAMMINOMIN (Piano di miglioramento,
sezione 2.D). Sostituisce, come fonte per la relazione, i due script usa-e-getta
scripts/verifica_componenti.py e scripts/verifica_innesco_goloso.py (mantenuti nel repository
solo come provenienza storica, si veda il Compito 3 della relazione) con un'unica campagna controllata.

Due parti:
  1. component_check: il suo beneficio si manifesta SOLO su coppie irraggiungibili (su coppie
     raggiungibili costa solo l'etichettatura O(R*C), sempre economica). Riusa il risultato già
     calcolato in results/component_check_results.json (recinto chiuso 50x50, coppia
     irraggiungibile) invece di ripetere l'esecuzione da 600s.
  2. greedy_seed: effetto marginale su coppie raggiungibili, misurato su 5 semi indipendenti
     (gli stessi di campagna_multiseme.py, per restare direttamente confrontabile con
     multiseme_results.json), con potatura debole e forte, con e senza innesco.

Costo atteso: solo la parte 2 esegue nuovi benchmark (5 semi x 4 configurazioni, cluster
50x50, timeout 20s), 3-8 minuti; la parte 1 è a costo zero (rilettura di un JSON già presente).

Produce results/ablation_ottimizzazioni.json.
"""
import json
import os
import time

from src.generator import GridGenerator
from src.camminomin import camminomin

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")
SEEDS = [301, 302, 303, 304, 305]  # stessi semi di campagna_multiseme.py
TAGLIA = 50
TIMEOUT = 20.0
ORIGIN, DEST = (0, 0), (TAGLIA - 1, TAGLIA - 1)


def _esegui(seed: int, forte: bool, innesco: bool) -> dict[str, object]:
    grid = GridGenerator.generate_grid(TAGLIA, TAGLIA, ["cluster"], density=0.2, seed=seed)
    grid.clear_cell(*ORIGIN)
    grid.clear_cell(*DEST)
    stats: dict[str, int] = {}
    start = time.time()
    min_len, _landmarks, timed_out = camminomin(
        ORIGIN, DEST, grid.state.copy(), stats=stats, start_time=start, timeout=TIMEOUT,
        use_strong_pruning=forte, greedy_seed=innesco, use_component_check=True
    )
    return {
        "seed": seed,
        "tempo_s": time.time() - start,
        "chiamate_ricorsive": stats.get("recursive_calls", 0),
        "lunghezza": min_len if min_len < float("inf") else None,
        "tempo_limite_raggiunto": timed_out
    }


def _ablation_greedy_seed() -> list[dict[str, object]]:
    configurazioni = [
        ("debole, senza innesco", False, False),
        ("debole, con innesco", False, True),
        ("forte, senza innesco", True, False),
        ("forte, con innesco", True, True),
    ]
    risultati = []
    for nome, forte, innesco in configurazioni:
        corse = [_esegui(seed, forte, innesco) for seed in SEEDS]
        tempi = sorted(c["tempo_s"] for c in corse)
        chiamate = sorted(c["chiamate_ricorsive"] for c in corse)
        risultati.append({
            "configurazione": nome,
            "potatura_forte": forte,
            "innesco_goloso": innesco,
            "tempo_mediano_s": tempi[len(tempi) // 2],
            "chiamate_mediane": chiamate[len(chiamate) // 2],
            "timeout_su_semi": sum(1 for c in corse if c["tempo_limite_raggiunto"]),
            "corse": corse
        })
    return risultati


def main() -> None:
    with open(os.path.join(RESULTS_DIR, "component_check_results.json"), encoding="utf-8") as f:
        component_check = json.load(f)

    greedy_seed = _ablation_greedy_seed()

    esito = {
        "component_check": {
            "nota": "Effetto su una coppia irraggiungibile in un recinto chiuso 50x50 "
                    "(risultato riusato da component_check_results.json, non ricalcolato)",
            "dati": component_check
        },
        "greedy_seed": {
            "nota": f"Effetto su {len(SEEDS)} semi indipendenti, cluster 50x50 densità 0.2, "
                    "coppia d'angolo sempre raggiungibile (component_check attivo in ogni "
                    "configurazione: qui costa solo l'etichettatura O(R*C), il suo beneficio "
                    "non è visibile su istanze raggiungibili)",
            "configurazioni": greedy_seed
        }
    }

    out_path = os.path.join(RESULTS_DIR, "ablation_ottimizzazioni.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(esito, f, indent=2, default=str, ensure_ascii=False)

    print("=== component_check (coppia irraggiungibile, dato riusato) ===")
    for c in component_check["corse"]:
        print(f"  {c['descrizione']:28s} tempo={c['tempo_s']:>10.4f}s "
              f"chiamate_ricorsive={c['chiamate_ricorsive']:>10} "
              f"tempo_limite_raggiunto={c['tempo_limite_raggiunto']}")

    print(f"\n=== greedy_seed ({len(SEEDS)} semi, cluster 50x50, mediana) ===")
    for r in greedy_seed:
        print(f"  {r['configurazione']:24s} tempo_mediano={r['tempo_mediano_s']:.4f}s "
              f"chiamate_mediane={r['chiamate_mediane']:.0f} "
              f"timeout_su_semi={r['timeout_su_semi']}/{len(SEEDS)}")

    print(f"\nSalvato in: {out_path}")


if __name__ == "__main__":
    main()
