import time
import numpy as np
from src.grid import Coordinate
from src.exceptions import PathReconstructionError
from src.free_paths import (
    dlib,
    compute_context_rays,
    compute_complement_rays,
    compute_frontier,
    free_path_type1,
    free_path_type2
)

def camminomin(
    origin: Coordinate,
    destination: Coordinate,
    grid_state: np.ndarray,
    depth: int = 0,
    stats: dict[str, int] | None = None,
    start_time: float | None = None,
    timeout: float | None = None,
    use_strong_pruning: bool = False,
    randomize_frontier: bool = False,
    shared_state: dict[str, any] | None = None,
    accumulated_len: float = 0.0,
    frozen_cells: frozenset[Coordinate] = frozenset(),
    path_cache: dict[tuple, tuple] | None = None,
    greedy_seed: bool = False,  # Flag per la corsa avida preliminare (limite superiore)
    disable_seed: bool = False  # Flag per disabilitare il seed (per analisi di benchmark)
) -> tuple[float, list[tuple[Coordinate, int]], bool]:
    """
    Trova il cammino minimo tra origine e destinazione utilizzando l'algoritmo ricorsivo basato su landmark.

    Risolve il Compito 3 dell'elaborato accademico, implementando un algoritmo di backtracking
    con due condizioni di potatura (Pruning condizionale) ed espansione a raggi (Ray-Casting).

    Args:
        origin: Coordinata di partenza (row, col).
        destination: Coordinata di arrivo (row, col).
        grid_state: Array numpy che memorizza gli ostacoli e le marcature temporanee.
        depth: Profondità corrente della ricorsione.
        stats: Dizionario per accumulare le metriche prestazionali dell'esecuzione.
        start_time: Timestamp dell'inizio dell'algoritmo principale per gestire il timeout.
        timeout: Tempo massimo in secondi concesso per l'intera ricerca.
        use_strong_pruning: Se True, utilizza il pruning forte (Riga 17) invece di quello debole (Riga 16).
        randomize_frontier: Se True, randomizza l'esplorazione delle celle di frontiera.
        shared_state: Stato condiviso mutable contenente il minimo globale trovato finora.
        accumulated_len: Lunghezza accumulata del percorso finora dall'origine root.
        frozen_cells: Insieme delle celle attualmente temporaneamente bloccate nei livelli superiori.
        path_cache: Cache per memoizzazione dei sotto-problemi.
        greedy_seed: Se True, disabilita il backtracking scendendo solo sul primo candidato (euristico migliore).
        disable_seed: Se True, esclude l'inizializzazione del seed Greedy root.

    Returns:
        Una tupla `(lunghezza_min, sequenza_landmark, timed_out)` dove:
          - lunghezza_min: float (distanza minima, 'inf' se irraggiungibile).
          - sequenza_landmark: lista di tuple `(cella, tipo_cammino)` dove tipo_cammino indica il tipo di
                               passo per raggiungere cella (0: origine, 1: tipo 1, 2: tipo 2).
          - timed_out: boolean che segnala se l'algoritmo si è arrestato per superamento del timeout.
    """
    # Se siamo in modalità greedy, isoliamo e disattiviamo la cache
    if greedy_seed:
        path_cache = None

    # 1. Inizializzazione dello stato condiviso e della cache se siamo a livello root
    if shared_state is None:
        shared_state = {
            'global_min_length': float('inf'),
            'has_real_path': False
        }
        
        # Corsa Greedy preliminare sul grafo dei landmark per trovare un limite superiore concreto
        if not greedy_seed and not disable_seed and origin != destination:
            import logging
            temp_logger = logging.getLogger("pathfinding_cli")
            greedy_state = grid_state.copy()
            l_greedy, _, _ = camminomin(
                origin, destination, greedy_state,
                depth=0, stats=None, start_time=None, timeout=None,
                use_strong_pruning=use_strong_pruning,
                randomize_frontier=False,
                shared_state={'global_min_length': float('inf'), 'has_real_path': False}, # isolato per il seed
                accumulated_len=0.0,
                frozen_cells=frozenset(),
                path_cache=None,
                greedy_seed=True,
                disable_seed=False
            )
            if l_greedy < float('inf'):
                shared_state['global_min_length'] = l_greedy
                temp_logger.info(f"Seed del minimo globale trovato via Greedy: {l_greedy:.4f}")

    if path_cache is None and not greedy_seed:
        path_cache = {}

    # 2. Aggiornamento delle statistiche di esecuzione
    if stats is not None:
        stats['recursive_calls'] = stats.get('recursive_calls', 0) + 1
        stats['max_depth'] = max(stats.get('max_depth', 0), depth)

    # 3. Controllo del limite di tempo (Timeout)
    if timeout is not None and start_time is not None:
        if time.time() - start_time > timeout:
            return float('inf'), [], True

    # 4. Lookup in Cache (solo se la cache è abilitata e attiva)
    cache_key = (origin, destination, frozen_cells)
    if path_cache is not None:
        if cache_key in path_cache:
            if stats is not None:
                stats['cache_hit'] = stats.get('cache_hit', 0) + 1
            return path_cache[cache_key]

    # 5. Global Pruning Check (attivo solo se siamo scesi sotto il livello radice)
    if depth > 0:
        limit = shared_state['global_min_length']
        if shared_state.get('has_real_path', False):
            if accumulated_len + dlib(origin, destination) >= limit:
                return float('inf'), [], False
        else:
            if accumulated_len + dlib(origin, destination) > limit:
                return float('inf'), [], False

    # 6. Caso Base 1: La destinazione è direttamente raggiungibile tramite tipo 1
    context = compute_context_rays(origin, grid_state)
    if destination in context:
        path_len = dlib(origin, destination)
        full_path_len = accumulated_len + path_len
        
        # Aggiornamento del minimo globale
        if not greedy_seed:
            if full_path_len < shared_state['global_min_length'] or (full_path_len == shared_state['global_min_length'] and not shared_state.get('has_real_path', False)):
                shared_state['global_min_length'] = full_path_len
                shared_state['has_real_path'] = True
                
        res = (path_len, [(origin, 0), (destination, 1)], False)
        if path_cache is not None:
            path_cache[cache_key] = res
        return res

    # 7. Caso Base 2: La destinazione è direttamente raggiungibile tramite tipo 2
    complement = compute_complement_rays(origin, grid_state, context)
    if destination in complement:
        path_len = dlib(origin, destination)
        full_path_len = accumulated_len + path_len
        
        # Aggiornamento del minimo globale
        if not greedy_seed:
            if full_path_len < shared_state['global_min_length'] or (full_path_len == shared_state['global_min_length'] and not shared_state.get('has_real_path', False)):
                shared_state['global_min_length'] = full_path_len
                shared_state['has_real_path'] = True
                
        res = (path_len, [(origin, 0), (destination, 2)], False)
        if path_cache is not None:
            path_cache[cache_key] = res
        return res

    # 8. Calcolo della frontiera della chiusura corrente
    frontier = compute_frontier(context, complement, grid_state)
    if stats is not None:
        stats['frontier_cells'] = stats.get('frontier_cells', 0) + len(frontier)

    if not frontier:
        return float('inf'), [], False

    # 9. Ordinamento Euristico dei candidati di frontiera (Slide 72)
    if randomize_frontier:
        import random
        random.shuffle(frontier)
    else:
        # Ordina per dlib(f, destination) crescente (promozione delle celle fisicamente più vicine al target)
        frontier.sort(key=lambda ft: dlib(ft[0], destination))

    min_length = float('inf')
    min_seq: list[tuple[Coordinate, int]] = []
    closure = context | complement
    
    # 10. BACKTRACKING: Marca la chiusura corrente come ostacolo temporaneo
    depth_id = depth + 2
    for cell in closure:
        grid_state[cell] = depth_id

    timed_out = False
    new_frozen_cells = frozen_cells | closure
    
    # 11. Esplorazione ricorsiva dei candidati di frontiera
    for f_cell, f_type in frontier:
        lf = dlib(origin, f_cell)
        
        # Pruning condizionale (Riga 16 vs Riga 17 della specifica)
        if use_strong_pruning:
            should_explore = (lf + dlib(f_cell, destination)) < min_length
        else:
            should_explore = lf < min_length

        # Global Pruning Check
        if should_explore:
            limit = shared_state['global_min_length']
            if shared_state.get('has_real_path', False):
                if accumulated_len + lf + dlib(f_cell, destination) >= limit:
                    should_explore = False
            else:
                if accumulated_len + lf + dlib(f_cell, destination) > limit:
                    should_explore = False

        if not should_explore:
            if stats is not None:
                stats['pruning_false'] = stats.get('pruning_false', 0) + 1
            if greedy_seed:
                # Se siamo in modalità seed e il primo nodo (migliore) fallisce il potatissimo check, ci fermiamo
                break
            continue

        # UNLOCK F: Rendi F temporaneamente libera per consentire la ricorsione da essa
        grid_state[f_cell] = 0

        # Chiamata ricorsiva da F
        lfd, seq_fd, child_timed_out = camminomin(
            f_cell,
            destination,
            grid_state,
            depth + 1,
            stats,
            start_time,
            timeout,
            use_strong_pruning,
            randomize_frontier,
            shared_state=shared_state,
            accumulated_len=accumulated_len + lf,
            frozen_cells=new_frozen_cells,
            path_cache=path_cache,
            greedy_seed=greedy_seed,
            disable_seed=disable_seed
        )
        
        if child_timed_out:
            timed_out = True

        # LOCK F: Ripristina la marcatura temporanea di F
        grid_state[f_cell] = depth_id

        # Se abbiamo trovato un cammino valido passante per F
        if lfd < float('inf'):
            l_tot = lf + lfd
            if l_tot < min_length:
                min_length = l_tot
                min_seq = compact([(origin, 0), (f_cell, f_type)], seq_fd)
                
                # Aggiornamento del minimo globale
                full_path_len = accumulated_len + l_tot
                if not greedy_seed:
                    if full_path_len < shared_state['global_min_length'] or (full_path_len == shared_state['global_min_length'] and not shared_state.get('has_real_path', False)):
                        shared_state['global_min_length'] = full_path_len
                        shared_state['has_real_path'] = True

        # Se si è verificato un timeout globale o siamo in modalità Greedy Seed, interrompi
        if timed_out or greedy_seed:
            break

    # 12. BACKTRACKING: Ripristina lo stato originale della griglia per tutta la chiusura
    for cell in closure:
        grid_state[cell] = 0

    res = (min_length, min_seq, timed_out)
    if not timed_out and path_cache is not None:
        path_cache[cache_key] = res
    return res

def compact(
    seq1: list[tuple[Coordinate, int]],
    seq2: list[tuple[Coordinate, int]]
) -> list[tuple[Coordinate, int]]:
    """
    Compatta due sequenze consecutive di landmark eliminando la duplicazione sul nodo di giunzione.

    Esempio:
      seq1 = [((0,0), 0), ((3,4), 1)]
      seq2 = [((3,4), 0), ((10,12), 2)]
      Ritorna: [((0,0), 0), ((3,4), 1), ((10,12), 2)]

    Args:
        seq1: Prima sequenza di landmark.
        seq2: Seconda sequenza di landmark.

    Returns:
        Lista dei landmark compattati.
    """
    if not seq2:
        return seq1
    return seq1 + seq2[1:]

def reconstruct_path(
    landmarks: list[tuple[Coordinate, int]],
    grid_state: np.ndarray
) -> list[Coordinate]:
    """
    Ricostruisce il cammino completo di celle (row, col) a partire dalla sequenza di landmark.

    Valida ciascun segmento di tipo 1 o di tipo 2 sulla griglia corrente.

    Args:
        landmarks: Sequenza dei landmark trovati dall'algoritmo camminomin.
        grid_state: Stato corrente della griglia per validare l'attraversabilità fisica.

    Returns:
        La lista ordinata di tutte le celle adiacenti che compongono il cammino.

    Raises:
        PathReconstructionError: Se uno dei tratti intermedi risulta ostruito o invalido.
    """
    if not landmarks:
        return []
        
    full_path: list[Coordinate] = []
    for i in range(len(landmarks) - 1):
        src, _ = landmarks[i]
        dst, tipo = landmarks[i + 1]
        
        if tipo == 1:
            segment = free_path_type1(src, dst, grid_state)
        elif tipo == 2:
            segment = free_path_type2(src, dst, grid_state)
        else:
            raise PathReconstructionError(f"Tipo di cammino {tipo} non supportato al segmento {i}.")
            
        if segment is None:
            raise PathReconstructionError(
                f"Impossibile ricostruire il segmento libero tra {src} e {dst} con tipo {tipo}."
            )
            
        if i == 0:
            full_path.extend(segment)
        else:
            # Evita la duplicazione della coordinata di giunzione tra segmenti consecutivi
            full_path.extend(segment[1:])
            
    return full_path
