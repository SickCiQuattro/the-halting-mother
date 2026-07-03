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

# Valore con cui le celle della chiusura corrente vengono marcate come ostacolo temporaneo
# durante il ritracciamento sul posto. È una costante (non dipende dalla profondità): le
# chiusure annidate sono disgiunte (il ray-casting si arresta a stato>0) e il ripristino
# avviene per insieme esplicito, quindi non serve un identificativo distinto per livello.
# Usare una costante evita l'overflow del tipo uint8 (depth+2 superava 255 oltre profondità 253).
TEMP_MARK = 2


def _aggiorna_minimo_globale(shared_state: dict[str, float], full_path_len: float) -> None:
    """Aggiorna il limite superiore globale se il cammino appena trovato è più breve.

    Il limite alimenta la potatura branch-and-bound condivisa tra tutte le invocazioni
    ricorsive: ogni ramo il cui costo ottimistico non può batterlo viene scartato.
    """
    if full_path_len < shared_state['global_min_length']:
        shared_state['global_min_length'] = full_path_len


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
    shared_state: dict[str, float] | None = None,
    accumulated_len: float = 0.0,
    visited_closures: set[Coordinate] | None = None
) -> tuple[float, list[tuple[Coordinate, int]], bool]:
    """
    Trova il cammino minimo tra origine e destinazione con l'algoritmo ricorsivo basato su landmark.

    Risolve il Compito 3 dell'elaborato tramite ritracciamento con le due condizioni di potatura
    alternative (riga 16 e riga 17) ed espansione della chiusura a proiezione di raggi.

    La condizione di riga 16/17 è valutata contro un limite superiore globale aggiornato durante la
    ricerca (potatura branch-and-bound): la riga 16 confronta la sola distanza già percorsa, la riga
    17 vi aggiunge la stima ammissibile della distanza libera residua dalla cella di frontiera alla
    destinazione. La memoizzazione dei sotto-problemi è stata rimossa perché il risultato di ogni
    sotto-problema dipende, attraverso la potatura globale, dalla lunghezza accumulata delle chiamate
    esterne, che non faceva parte della chiave; risultati subottimali venivano quindi riusati in
    contesti errati, violando la simmetria O-D / D-O.

    Args:
        origin: Coordinata di partenza (riga, colonna).
        destination: Coordinata di arrivo (riga, colonna).
        grid_state: Matrice numpy che memorizza gli ostacoli e le marcature temporanee.
        depth: Profondità corrente della ricorsione.
        stats: Dizionario per accumulare le metriche prestazionali dell'esecuzione.
        start_time: Istante d'inizio dell'algoritmo principale per gestire il tempo limite.
        timeout: Tempo massimo in secondi concesso per l'intera ricerca.
        use_strong_pruning: Se True, utilizza la potatura forte (riga 17) invece di quella debole (riga 16).
        randomize_frontier: Se True, esplora le celle di frontiera in ordine casuale.
        shared_state: Stato condiviso mutabile contenente il minimo globale trovato finora.
        accumulated_len: Lunghezza accumulata del percorso dall'origine della chiamata principale.
        visited_closures: Se fornito, accumula tutte le celle incluse in una chiusura esplorata durante
            l'intera ricerca (usato solo per analisi/visualizzazione, non influenza la logica).

    Returns:
        Una tupla `(lunghezza_min, sequenza_landmark, timed_out)` dove:
          - lunghezza_min: float (distanza minima, 'inf' se irraggiungibile).
          - sequenza_landmark: lista di tuple `(cella, tipo_cammino)` dove tipo_cammino indica il tipo di
                               passo per raggiungere cella (0: origine, 1: tipo 1, 2: tipo 2).
          - timed_out: True se l'algoritmo si è arrestato per superamento del tempo limite.
    """
    # 1. Inizializzazione dello stato condiviso al livello radice
    if shared_state is None:
        shared_state = {'global_min_length': float('inf')}

    # 2. Aggiornamento delle statistiche di esecuzione
    if stats is not None:
        stats['recursive_calls'] = stats.get('recursive_calls', 0) + 1
        stats['max_depth'] = max(stats.get('max_depth', 0), depth)

    # 3. Controllo del tempo limite
    if timeout is not None and start_time is not None:
        if time.time() - start_time > timeout:
            return float('inf'), [], True

    # 4. Caso base 1: la destinazione è raggiungibile con un cammino libero di tipo 1
    context = compute_context_rays(origin, grid_state)
    if destination in context:
        path_len = dlib(origin, destination)
        _aggiorna_minimo_globale(shared_state, accumulated_len + path_len)
        return path_len, [(origin, 0), (destination, 1)], False

    # 5. Caso base 2: la destinazione è raggiungibile solo con un cammino libero di tipo 2
    complement = compute_complement_rays(origin, grid_state, context)
    if destination in complement:
        path_len = dlib(origin, destination)
        _aggiorna_minimo_globale(shared_state, accumulated_len + path_len)
        return path_len, [(origin, 0), (destination, 2)], False

    # 6. Frontiera della chiusura corrente
    frontier = compute_frontier(context, complement, grid_state)
    if stats is not None:
        stats['frontier_cells'] = stats.get('frontier_cells', 0) + len(frontier)

    if not frontier:
        return float('inf'), [], False

    # 7. Ordinamento euristico della frontiera (osservazione della diapositiva 66):
    #    si esplorano per prime le celle più vicine alla destinazione.
    if randomize_frontier:
        import random
        random.shuffle(frontier)
    else:
        frontier.sort(key=lambda ft: dlib(ft[0], destination))

    min_length = float('inf')
    min_seq: list[tuple[Coordinate, int]] = []
    closure = context | complement

    if visited_closures is not None:
        visited_closures.update(closure)

    # 8. Ritracciamento sul posto: marca la chiusura corrente come ostacolo temporaneo
    for cell in closure:
        grid_state[cell] = TEMP_MARK

    timed_out = False

    # 9. Esplorazione ricorsiva dei candidati di frontiera
    for f_cell, f_type in frontier:
        lf = dlib(origin, f_cell)

        # Condizione di potatura di riga 16 / riga 17 valutata contro il limite superiore globale:
        # la riga 16 usa la sola distanza percorsa, la riga 17 vi somma la stima ammissibile
        # dlib(F, D) della distanza residua. Quando il limite è ancora infinito non si pota nulla.
        if use_strong_pruning:
            stima = accumulated_len + lf + dlib(f_cell, destination)
        else:
            stima = accumulated_len + lf

        if stima >= shared_state['global_min_length']:
            # La condizione di riga 16/17 è falsa: il candidato viene scartato.
            if stats is not None:
                stats['pruning_false'] = stats.get('pruning_false', 0) + 1
            continue

        # Sblocca F per consentire la ricorsione da essa, poi ne ripristina la marcatura
        grid_state[f_cell] = 0
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
            visited_closures=visited_closures
        )
        grid_state[f_cell] = TEMP_MARK

        if child_timed_out:
            timed_out = True

        # Se è stato trovato un cammino valido passante per F, aggiorna il minimo locale e globale
        if lfd < float('inf'):
            l_tot = lf + lfd
            if l_tot < min_length:
                min_length = l_tot
                min_seq = compact([(origin, 0), (f_cell, f_type)], seq_fd)
                _aggiorna_minimo_globale(shared_state, accumulated_len + l_tot)

        if timed_out:
            break

    # 10. Ripristina lo stato originale della griglia per tutta la chiusura
    for cell in closure:
        grid_state[cell] = 0

    return min_length, min_seq, timed_out

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
