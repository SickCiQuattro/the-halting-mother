#!/usr/bin/env python3
"""
Punto di ingresso principale della CLI per il sistema di pathfinding su griglia (Elaborato 2024/25).

Fornisce un'interfaccia a riga di comando per generare griglie, calcolare contesti/complementi
di raggiungibilità, misurare distanze ideali, trovare cammini minimi con l'algoritmo ricorsivo
ed eseguire benchmark comparativi.
"""

import sys
import os
import argparse
import json
import time
import logging
import numpy as np

# Aumenta il limite di ricorsione per consentire griglie di grandi dimensioni (es. 200x200)
sys.setrecursionlimit(15000)

from src.grid import Grid, Coordinate
from src.generator import GridGenerator
from src.free_paths import dlib, compute_context_rays, compute_complement_rays, compute_frontier
from src.camminomin import camminomin, reconstruct_path
from src.utils import parse_coords, format_landmarks, print_grid_visual
from src.experiment import ExperimentRunner
from src.exceptions import PathfindingError

# Configura il logger radice per l'applicazione CLI
logger = logging.getLogger("pathfinding_cli")

def _carica_griglia_o_esci(path: str) -> Grid:
    """Carica la griglia da file, terminando con un messaggio d'errore se il file non esiste."""
    if not os.path.exists(path):
        logger.error(f"File griglia '{path}' non trovato.")
        sys.exit(1)
    return Grid.load(path)

def _interpreta_coordinate_o_esci(coord_str: str, etichetta: str = "coordinate") -> Coordinate:
    """Interpreta una stringa di coordinate, terminando con un messaggio d'errore se non valida."""
    try:
        return parse_coords(coord_str)
    except PathfindingError as e:
        logger.error(f"Errore parsing {etichetta}: {e}")
        sys.exit(1)

def cmd_generate(args: argparse.Namespace) -> None:
    """
    Sotto-comando per la generazione procedurale di ostacoli sulla griglia.

    Args:
        args: Argomenti parsati dalla CLI.
    """
    types: list[str] = args.types
    if "mix" in types:
        types = ["simple", "cluster", "diagonal", "enclosure", "bar"]
        
    logger.info(f"Generazione griglia {args.rows}x{args.cols} in corso...")
    grid = GridGenerator.generate_grid(args.rows, args.cols, types, args.density, args.seed)
    
    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    grid.save(args.output)
    logger.info(f"Griglia salvata con successo in: {args.output}")
    
    if args.save_img:
        from src.visualization import save_grid_image
        save_grid_image(grid, args.save_img, title=f"Griglia generata ({grid.rows}x{grid.cols})")
        
    # Visualizzazione della griglia sul terminale se le dimensioni sono limitate
    if args.rows <= 30 and args.cols <= 30:
        print("\nRappresentazione visiva della griglia:")
        print(grid)

def cmd_context(args: argparse.Namespace) -> None:
    """
    Sotto-comando per analizzare il contesto (tipo 1), complemento (tipo 2) e frontiera di un nodo.

    Args:
        args: Argomenti parsati dalla CLI.
    """
    grid = _carica_griglia_o_esci(args.grid)
    origin = _interpreta_coordinate_o_esci(args.origin, "coordinate origine")

    if not grid.is_valid(origin[0], origin[1]):
        logger.error(f"L'origine {origin} è posizionata fuori dalla griglia.")
        sys.exit(1)
        
    logger.info(f"Calcolo dei cammini liberi a raggi da O={origin}...")
    
    context = compute_context_rays(origin, grid.state)
    complement = compute_complement_rays(origin, grid.state, context)
    frontier = compute_frontier(context, complement, grid.state)
    
    if args.type in ('1', 'both'):
        print("\n--- CONTESTO (Tipo 1: Diagonale prima) ---")
        print(f"Celle raggiungibili: {len(context)}")
        if len(context) <= 100:
            print(sorted(list(context)))
            
    if args.type in ('2', 'both'):
        print("\n--- COMPLEMENTO (Tipo 2: Cardinale prima) ---")
        print(f"Celle raggiungibili: {len(complement)}")
        if len(complement) <= 100:
            print(sorted(list(complement)))
            
    print("\n--- FRONTIERA DELLA CHIUSURA ---")
    print(f"Celle di frontiera: {len(frontier)}")
    if len(frontier) <= 100:
        formatted_frontier = [(cell, f"Tipo {tipo}") for cell, tipo in sorted(frontier)]
        print(formatted_frontier)

    if args.save_img:
        from src.visualization import save_context_image
        save_context_image(
            grid, origin, context, complement, frontier, args.save_img,
            title=f"Contesto, complemento e frontiera da O={origin}"
        )

def cmd_dlib(args: argparse.Namespace) -> None:
    """
    Sotto-comando per misurare la distanza di cammino libero ideale dlib tra due punti.

    Args:
        args: Argomenti parsati dalla CLI.
    """
    o = _interpreta_coordinate_o_esci(args.origin, "coordinate origine")
    d = _interpreta_coordinate_o_esci(args.dest, "coordinate destinazione")

    dist = dlib(o, d)
    print(f"Distanza ideale dlib tra {o} e {d}: {dist:.6f}")

def cmd_camminomin(args: argparse.Namespace) -> None:
    """
    Sotto-comando per calcolare il cammino minimo tramite backtracking ricorsivo basato su landmark.

    Args:
        args: Argomenti parsati dalla CLI.
    """
    grid = _carica_griglia_o_esci(args.grid)
    origin = _interpreta_coordinate_o_esci(args.origin, "coordinate origine")
    dest = _interpreta_coordinate_o_esci(args.dest, "coordinate destinazione")

    if not grid.is_valid(origin[0], origin[1]) or not grid.is_valid(dest[0], dest[1]):
        logger.error(f"Origine {origin} o destinazione {dest} fuori dai limiti della griglia.")
        sys.exit(1)
        
    logger.info(f"Ricerca del cammino minimo da O={origin} a D={dest}...")
    
    stats = {
        'frontier_cells': 0,
        'pruning_false': 0,
        'recursive_calls': 0,
        'max_depth': 0
    }
    
    start_time = time.time()
    
    min_len, landmarks, timed_out = camminomin(
        origin, dest, grid.state, depth=0, stats=stats,
        start_time=start_time, timeout=args.timeout,
        use_strong_pruning=args.strong_pruning,
        randomize_frontier=args.randomize_frontier,
        use_component_check=not args.no_component_check,
        greedy_seed=args.greedy_seed
    )
    
    elapsed = time.time() - start_time
    
    path: list[Coordinate] = []
    if min_len < float('inf'):
        try:
            path = reconstruct_path(landmarks, grid.state)
        except PathfindingError as e:
            logger.error(f"Errore durante la ricostruzione del cammino: {e}")
            sys.exit(1)
            
    if args.save_img and min_len < float('inf'):
        from src.visualization import save_grid_image
        save_grid_image(
            grid, args.save_img,
            origin=origin, dest=dest,
            path=path, landmarks=landmarks,
            title=f"Cammino minimo ricostruito (lunghezza: {min_len:.4f})"
        )
        
    if args.summary:
        # Riassunto strutturato dell'esecuzione come richiesto dalla specifica
        if timed_out:
            calculation_status = "INTERROTTO PER SUPERAMENTO DEL TEMPO LIMITE"
        elif min_len < float('inf'):
            calculation_status = "COMPLETO"
        else:
            calculation_status = "IRRAGGIUNGIBILE"

        summary = {
            "dimensioni_griglia": f"{grid.rows}x{grid.cols}",
            "tipologia_griglia": ", ".join(grid.types) if grid.types else "non specificata",
            "file_griglia": args.grid,
            "origine": origin,
            "destinazione": dest,
            "stato_calcolo": calculation_status,
            "lunghezza_cammino_minimo": min_len if min_len < float('inf') else "infinita",
            "numero_landmark": len(landmarks),
            "sequenza_landmark": landmarks,
            "celle_frontiera_totali": stats['frontier_cells'],
            "condizione_potatura_falsa": stats['pruning_false'],
            "regola_potatura": "Riga 17 (forte)" if args.strong_pruning else "Riga 16 (debole)",
            "invocazioni_ricorsive": stats['recursive_calls'],
            "profondita_massima": stats['max_depth'],
            "memoria_rappresentazione_byte": grid.rows * grid.cols,
            "tempo_trascorso_s": elapsed,
            "calcolo_completato": not timed_out
        }
        print("\n=== RIASSUNTO STRUTTURATO DELL'ESECUZIONE ===")
        print(json.dumps(summary, indent=2, default=str, ensure_ascii=False))
    else:
        print("\n=== Risultato della Ricerca ===")
        status = 'TEMPO LIMITE SUPERATO' if timed_out else 'SUCCESSO' if min_len < float('inf') else 'NON RAGGIUNGIBILE'
        print(f"Stato: {status}")
        print(f"Lunghezza cammino minimo: {min_len:.6f}" if min_len < float('inf') else "Lunghezza cammino minimo: Inf")
        print(f"Tempo impiegato: {elapsed:.6f} secondi")
        print("\nSequenza ordinata dei Landmark:")
        print(format_landmarks(landmarks))
        
        if grid.rows <= 40 and grid.cols <= 40 and len(path) > 0:
            print("\nMappa visuale del cammino ottimale (*):")
            print_grid_visual(grid, origin, dest, path)

def cmd_experiment(args: argparse.Namespace) -> None:
    """
    Sotto-comando per lanciare la campagna di benchmark sperimentale o il test di simmetria.

    Args:
        args: Argomenti parsati dalla CLI.
    """
    if args.verify_symmetry_count > 0:
        grid_size = args.symmetry_grid_size
        logger.info(
            f"Avvio test di simmetria su {args.verify_symmetry_count} coppie "
            f"(griglia {grid_size}x{grid_size})..."
        )
        grid = GridGenerator.generate_grid(
            grid_size, grid_size, ["simple", "cluster"], density=0.15, seed=999
        )

        rng = np.random.default_rng(12345)
        points: list[tuple[Coordinate, Coordinate]] = []
        for _ in range(args.verify_symmetry_count):
            while True:
                o: Coordinate = (int(rng.integers(0, grid_size)), int(rng.integers(0, grid_size)))
                d: Coordinate = (int(rng.integers(0, grid_size)), int(rng.integers(0, grid_size)))
                if o != d and grid.is_traversable(o[0], o[1]) and grid.is_traversable(d[0], d[1]):
                    points.append((o, d))
                    break

        results = ExperimentRunner.verify_symmetry(grid, points, use_strong=True)
        symmetry_failed = [r for r in results if not r["symmetry_ok"]]

        print("\n--- Analisi Simmetria Risultati ---")
        for r in results:
            status = 'OK' if r['symmetry_ok'] else 'FALLITA'
            to_note = ' [TEMPO LIMITE]' if r['timed_out_od'] or r['timed_out_do'] else ''
            print(
                f"Coppia {r['pair_index']}: O={r['origin']} -> D={r['dest']} "
                f"| Len(O->D)={r['len_od']:.4f}, Len(D->O)={r['len_do']:.4f} "
                f"| Simmetria: {status}{to_note}"
            )

        print(f"\nTotale test: {len(results)} | Fallimenti: {len(symmetry_failed)}")
        if symmetry_failed:
            logger.error("Test di simmetria fallito su uno o più campioni.")
            sys.exit(1)
    else:
        # Avvia l'intera campagna sperimentale
        ExperimentRunner.run_campaign(args.output_dir)

def main() -> None:
    """Configura il parser degli argomenti ed esegue il sotto-comando associato."""
    # Configura il logging standard dell'applicazione
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stderr
    )

    parser = argparse.ArgumentParser(description="Algoritmi e Strutture Dati: Elaborato 2024/25")
    subparsers = parser.add_subparsers(dest="command", help="Sotto-comandi disponibili")
    
    # 1. GENERATE
    parser_gen = subparsers.add_parser("generate", help="Genera ostacoli procedurali sulla griglia")
    parser_gen.add_argument("--rows", type=int, default=50, help="Righe della griglia")
    parser_gen.add_argument("--cols", type=int, default=50, help="Colonne della griglia")
    parser_gen.add_argument("--types", nargs="+", default=["simple"], choices=["simple", "cluster", "diagonal", "enclosure", "bar", "mix"], help="Tipologie ostacoli")
    parser_gen.add_argument("--density", type=float, default=0.2, help="Densità degli ostacoli (0..1)")
    parser_gen.add_argument("--seed", type=int, default=None, help="Seme pseudo-casuale per la riproducibilità")
    parser_gen.add_argument("-o", "--output", default="grids/grid.json", help="Percorso del file JSON per salvare lo stato")
    parser_gen.add_argument("--save-img", default=None, help="Percorso per salvare l'immagine PNG della griglia generata")
    parser_gen.set_defaults(func=cmd_generate)

    # 2. CONTEXT
    parser_ctx = subparsers.add_parser("context", help="Calcola contesto (tipo 1), complemento (tipo 2) e frontiera di un nodo")
    parser_ctx.add_argument("--grid", required=True, help="Percorso del file JSON della griglia")
    parser_ctx.add_argument("--origin", required=True, help="Coordinate cella di partenza (row,col)")
    parser_ctx.add_argument("--type", choices=['1', '2', 'both'], default='both', help="Visualizza contesto (1), complemento (2) o entrambi")
    parser_ctx.add_argument("--save-img", default=None, help="Percorso per salvare l'immagine PNG di contesto/complemento/frontiera")
    parser_ctx.set_defaults(func=cmd_context)

    # 3. DLIB
    parser_dlib = subparsers.add_parser("dlib", help="Calcola la distanza dlib tra due coordinate")
    parser_dlib.add_argument("--origin", required=True, help="Coordinate dell'origine (row,col)")
    parser_dlib.add_argument("--dest", required=True, help="Coordinate della destinazione (row,col)")
    parser_dlib.set_defaults(func=cmd_dlib)

    # 4. CAMMINOMIN
    parser_cm = subparsers.add_parser("camminomin", help="Risolve il cammino minimo tramite algoritmo CAMMINOMIN ricorsivo")
    parser_cm.add_argument("--grid", required=True, help="Percorso del file JSON della griglia")
    parser_cm.add_argument("--origin", required=True, help="Coordinate origine (row,col)")
    parser_cm.add_argument("--dest", required=True, help="Coordinate destinazione (row,col)")
    parser_cm.add_argument("--timeout", type=float, default=60.0, help="Tempo limite di elaborazione in secondi")
    parser_cm.add_argument("--strong-pruning", action="store_true", help="Abilita il pruning forte (Riga 17) anziché debole (Riga 16)")
    parser_cm.add_argument("--randomize-frontier", action="store_true", help="Mescola casualmente l'esplorazione dei nodi di frontiera")
    parser_cm.add_argument("--no-component-check", action="store_true", help="Disabilita il controllo preliminare dei componenti connessi per le coppie irraggiungibili")
    parser_cm.add_argument("--greedy-seed", action="store_true", help="Innesca il limite superiore globale con una discesa golosa preliminare")
    parser_cm.add_argument("--summary", action="store_true", help="Stampa il resoconto strutturato dell'esecuzione richiesto dalla specifica")
    parser_cm.add_argument("--save-img", default=None, help="Percorso per salvare l'immagine PNG del cammino minimo")
    parser_cm.set_defaults(func=cmd_camminomin)

    # 5. EXPERIMENT
    parser_exp = subparsers.add_parser("experiment", help="Lancia la campagna di sperimentazione analitica con report grafici")
    parser_exp.add_argument("--output-dir", default="results", help="Cartella per il salvataggio dei grafici e dei report")
    parser_exp.add_argument("--verify-symmetry-count", type=int, default=0, help="Esegue solo il test di simmetria con N coppie casuali")
    parser_exp.add_argument("--symmetry-grid-size", type=int, default=20, help="Dimensione lato griglia per il test di simmetria (default: 20)")
    parser_exp.set_defaults(func=cmd_experiment)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)

if __name__ == "__main__":
    main()
