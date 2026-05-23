import math
import numpy as np
from src.grid import Coordinate

def dlib(origin: Coordinate, destination: Coordinate) -> float:
    """
    Calcola la distanza di cammino libero ideale (dlib) tra due coordinate in una griglia 8-connected.

    La formula calcola il costo del cammino minimo teorico assumendo l'assenza di ostacoli:
    dlib = sqrt(2) * min(dy, dx) + (max(dy, dx) - min(dy, dx))

    Args:
        origin: Coordinata di partenza (row, col).
        destination: Coordinata di arrivo (row, col).

    Returns:
        Il valore float della distanza ideale di cammino.
    """
    dy = abs(origin[0] - destination[0])
    dx = abs(origin[1] - destination[1])
    d_min = min(dx, dy)
    d_max = max(dx, dy)
    return math.sqrt(2) * d_min + (d_max - d_min)

def get_diag_direction(origin: Coordinate, destination: Coordinate) -> Coordinate:
    """
    Determina la direzione diagonale (dr, dc) per muoversi da un'origine a una destinazione.

    Args:
        origin: Coordinata di partenza.
        destination: Coordinata di arrivo.

    Returns:
        Una tupla (dr, dc) dove ogni elemento è in {-1, 0, 1}.
    """
    dr = 1 if destination[0] > origin[0] else (-1 if destination[0] < origin[0] else 0)
    dc = 1 if destination[1] > origin[1] else (-1 if destination[1] < origin[1] else 0)
    return dr, dc

def free_path_type1(
    origin: Coordinate,
    destination: Coordinate,
    grid_state: np.ndarray
) -> list[Coordinate] | None:
    """
    Verifica la presenza di un cammino libero di tipo 1 (diagonale prima, cardinale dopo).

    Il cammino è libero se tutte le celle intermedie e di destinazione hanno stato pari a 0
    (libere da ostacoli sia fissi che temporanei).

    Args:
        origin: Coordinata di partenza.
        destination: Coordinata di arrivo.
        grid_state: Array bidimensionale numpy che rappresenta lo stato della griglia.

    Returns:
        La lista dei punti del cammino (compresi origine e destinazione) se esiste,
        altrimenti None se il cammino è ostruito o fuori dai limiti.
    """
    dy = abs(origin[0] - destination[0])
    dx = abs(origin[1] - destination[1])
    d_min = min(dx, dy)
    d_max = max(dx, dy)
    
    diag_dr, diag_dc = get_diag_direction(origin, destination)
    
    if dx > dy:
        card_dr, card_dc = 0, diag_dc  # Movimento orizzontale residuo
    elif dy > dx:
        card_dr, card_dc = diag_dr, 0  # Movimento verticale residuo
    else:
        card_dr, card_dc = 0, 0        # Diagonale pura o coincidenti
        
    path: list[Coordinate] = [origin]
    r, c = origin
    
    # Fase 1: Movimenti diagonali
    for _ in range(d_min):
        r += diag_dr
        c += diag_dc
        if not (0 <= r < grid_state.shape[0] and 0 <= c < grid_state.shape[1]):
            return None
        if grid_state[r, c] > 0:
            return None
        path.append((r, c))
        
    # Fase 2: Movimenti cardinali
    for _ in range(d_max - d_min):
        r += card_dr
        c += card_dc
        if not (0 <= r < grid_state.shape[0] and 0 <= c < grid_state.shape[1]):
            return None
        if grid_state[r, c] > 0:
            return None
        path.append((r, c))
        
    return path

def free_path_type2(
    origin: Coordinate,
    destination: Coordinate,
    grid_state: np.ndarray
) -> list[Coordinate] | None:
    """
    Verifica la presenza di un cammino libero di tipo 2 (cardinale prima, diagonale dopo).

    Il cammino è libero se tutte le celle intermedie e di destinazione hanno stato pari a 0
    (libere da ostacoli sia fissi che temporanei).

    Args:
        origin: Coordinata di partenza.
        destination: Coordinata di arrivo.
        grid_state: Array bidimensionale numpy che rappresenta lo stato della griglia.

    Returns:
        La lista dei punti del cammino (compresi origine e destinazione) se esiste,
        altrimenti None se il cammino è ostruito o fuori dai limiti.
    """
    dy = abs(origin[0] - destination[0])
    dx = abs(origin[1] - destination[1])
    d_min = min(dx, dy)
    d_max = max(dx, dy)
    
    diag_dr, diag_dc = get_diag_direction(origin, destination)
    
    if dx > dy:
        card_dr, card_dc = 0, diag_dc  # Movimento orizzontale iniziale
    elif dy > dx:
        card_dr, card_dc = diag_dr, 0  # Movimento verticale iniziale
    else:
        card_dr, card_dc = 0, 0        # Diagonale pura o coincidenti
        
    path: list[Coordinate] = [origin]
    r, c = origin
    
    # Fase 1: Movimenti cardinali prima
    for _ in range(d_max - d_min):
        r += card_dr
        c += card_dc
        if not (0 <= r < grid_state.shape[0] and 0 <= c < grid_state.shape[1]):
            return None
        if grid_state[r, c] > 0:
            return None
        path.append((r, c))
        
    # Fase 2: Movimenti diagonali dopo
    for _ in range(d_min):
        r += diag_dr
        c += diag_dc
        if not (0 <= r < grid_state.shape[0] and 0 <= c < grid_state.shape[1]):
            return None
        if grid_state[r, c] > 0:
            return None
        path.append((r, c))
        
    return path

def compute_context_rays(origin: Coordinate, grid_state: np.ndarray) -> set[Coordinate]:
    """
    Ritorna l'insieme di celle raggiungibili da un'origine tramite un cammino libero di tipo 1.

    Ottimizzazione Ray-Casting:
    Invece di invocare `free_path_type1` per ciascuna cella della griglia (costo totale O(R^2 * C^2)),
    questo algoritmo traccia i raggi partendo dall'origine ed espandendo verso l'esterno.
    La complessità temporale è ridotta a O(max(R, C)^2).

    Algoritmo:
    1. Traccia i 4 raggi cardinali puri (N, S, E, W) a partire dall'origine finché non incontra un ostacolo.
    2. Per ciascuno dei 4 quadranti:
       - Traccia il raggio diagonale puro.
       - Da ogni cella raggiunta sul raggio diagonale, espande cardinalmente
         (in direzione orizzontale e verticale) finché non trova ostacoli.

    Args:
        origin: Coordinata sorgente di espansione.
        grid_state: Array bidimensionale dello stato della griglia.

    Returns:
        Un set di coordinate raggiungibili tramite cammino di tipo 1.
    """
    context: set[Coordinate] = {origin}
    rows, cols = grid_state.shape
    
    # 1. Celle sugli assi puri dell'origine (solo movimenti cardinali)
    for card_dr, card_dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        r, c = origin
        while True:
            r += card_dr
            c += card_dc
            if not (0 <= r < rows and 0 <= c < cols):
                break
            if grid_state[r, c] > 0:
                break
            context.add((r, c))
            
    # 2. Celle nei 4 quadranti (diagonale prima, poi espansione cardinale)
    for diag_dr, diag_dc in [(-1, 1), (-1, -1), (1, -1), (1, 1)]:
        r, c = origin
        while True:
            r += diag_dr
            c += diag_dc
            if not (0 <= r < rows and 0 <= c < cols):
                break
            if grid_state[r, c] > 0:
                # Se la diagonale è bloccata, il raggio diagonale si interrompe
                break
                
            context.add((r, c))
            
            # Espansione cardinale orizzontale a partire dal punto diagonale corrente
            er, ec = r, c
            while True:
                ec += diag_dc
                if not (0 <= ec < cols):
                    break
                if grid_state[er, ec] > 0:
                    break
                context.add((er, ec))
                
            # Espansione cardinale verticale a partire dal punto diagonale corrente
            er, ec = r, c
            while True:
                er += diag_dr
                if not (0 <= er < rows):
                    break
                if grid_state[er, ec] > 0:
                    break
                context.add((er, ec))
                
    return context

def compute_complement_rays(
    origin: Coordinate,
    grid_state: np.ndarray,
    context: set[Coordinate]
) -> set[Coordinate]:
    """
    Ritorna l'insieme di celle raggiungibili da un'origine tramite cammino tipo 2 escludendo il contesto.

    Ottimizzazione Ray-Casting:
    La complessità temporale è O(max(R, C)^2).
    Questo metodo trova le celle che hanno un cammino libero di tipo 2 e NON di tipo 1.
    Nota: Per gli assi puri, tipo 1 e tipo 2 sono coincidenti, quindi sono già interamente coperti
    nel contesto.

    Algoritmo:
    Per ciascuno dei 4 quadranti:
    1. Traccia il raggio cardinale (orizzontale), e da ogni cella raggiunta, espande in diagonale.
    2. Traccia il raggio cardinale (verticale), e da ogni cella raggiunta, espande in diagonale.

    Args:
        origin: Coordinata sorgente di espansione.
        grid_state: Array bidimensionale dello stato della griglia.
        context: Insieme delle coordinate già appartenenti al contesto (tipo 1).

    Returns:
        Un set di coordinate appartenenti esclusivamente al complemento (tipo 2).
    """
    complement: set[Coordinate] = set()
    rows, cols = grid_state.shape
    
    for diag_dr, diag_dc in [(-1, 1), (-1, -1), (1, -1), (1, 1)]:
        
        # 1. Componente orizzontale prima: cammina orizzontalmente, poi espandi in diagonale
        r, c = origin
        while True:
            c += diag_dc
            if not (0 <= c < cols):
                break
            if grid_state[r, c] > 0:
                break
                
            dr2, dc2 = r, c
            while True:
                dr2 += diag_dr
                dc2 += diag_dc
                if not (0 <= dr2 < rows and 0 <= dc2 < cols):
                    break
                if grid_state[dr2, dc2] > 0:
                    break
                cell = (dr2, dc2)
                if cell not in context:
                    complement.add(cell)
                    
        # 2. Componente verticale prima: cammina verticalmente, poi espandi in diagonale
        r, c = origin
        while True:
            r += diag_dr
            if not (0 <= r < rows):
                break
            if grid_state[r, c] > 0:
                break
                
            dr2, dc2 = r, c
            while True:
                dr2 += diag_dr
                dc2 += diag_dc
                if not (0 <= dr2 < rows and 0 <= dc2 < cols):
                    break
                if grid_state[dr2, dc2] > 0:
                    break
                cell = (dr2, dc2)
                if cell not in context:
                    complement.add(cell)
                    
    return complement

def compute_frontier(
    context: set[Coordinate],
    complement: set[Coordinate],
    grid_state: np.ndarray
) -> list[tuple[Coordinate, int]]:
    """
    Individua le celle di frontiera della chiusura.

    Una cella appartiene alla frontiera se fa parte della chiusura (contesto U complemento)
    e possiede almeno una cella vicina libera (stato pari a 0) al di fuori della chiusura.

    Args:
        context: Insieme delle celle del contesto (tipo 1).
        complement: Insieme delle celle del complemento (tipo 2).
        grid_state: Array bidimensionale dello stato della griglia.

    Returns:
        Una lista di tuple `(coordinata, tipo_cammino)` dove tipo_cammino è:
          - 1 se la cella fa parte del contesto.
          - 2 se la cella fa parte del complemento.
    """
    closure = context | complement
    frontier: list[tuple[Coordinate, int]] = []
    rows, cols = grid_state.shape
    
    for cell in closure:
        r, c = cell
        is_frontier = False
        
        # Controlla tutti gli 8 vicini per verificare la presenza di uscite libere esterne alla chiusura
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    # Se il vicino è libero ed esterno alla chiusura corrente
                    if grid_state[nr, nc] == 0 and (nr, nc) not in closure:
                        is_frontier = True
                        break
            if is_frontier:
                break
                
        if is_frontier:
            tipo = 1 if cell in context else 2
            frontier.append((cell, tipo))
            
    return frontier
