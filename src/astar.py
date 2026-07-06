"""
Implementazione di confronto: A* sul grafo delle celle (pag. 63, confronto di implementazioni).

Non sostituisce CAMMINOMIN (l'elaborato impone quello pseudocodice) ma funge da oracolo di
correttezza indipendente: su griglie 8-connesse con costi unitari sui passi cardinali e sqrt(2)
sui diagonali, la distanza `dlib` è esattamente l'euristica octile, ammissibile e consistente,
quindi A* restituisce sempre la lunghezza del cammino minimo esatto. Ogni lunghezza completata
da CAMMINOMIN deve coincidere con quella di A*.

Semantica di attraversamento identica a quella dei cammini liberi (pag. 3 dell'elaborato): il
passo diagonale fra due celle libere è sempre ammesso, anche quando i due ostacoli adiacenti si
toccano per lo spigolo (nessuna restrizione di taglio d'angolo).

Riferimento: P. E. Hart, N. J. Nilsson, B. Raphael, "A Formal Basis for the Heuristic
Determination of Minimum Cost Paths", IEEE Trans. SSC-4(2), 1968.
"""
import heapq
from math import sqrt

import numpy as np

from src.grid import Coordinate
from src.free_paths import dlib

SQRT2 = sqrt(2.0)

# Gli 8 spostamenti ammessi con il rispettivo costo
_MOSSE = [
    (-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0),
    (-1, -1, SQRT2), (-1, 1, SQRT2), (1, -1, SQRT2), (1, 1, SQRT2),
]


def astar(origin: Coordinate, dest: Coordinate, grid_state: np.ndarray) -> float:
    """
    Lunghezza del cammino minimo fra origine e destinazione con A* e euristica octile (`dlib`).

    Args:
        origin: Coordinata di partenza (riga, colonna).
        dest: Coordinata di arrivo (riga, colonna).
        grid_state: Matrice degli stati della griglia (0 libera, >0 ostacolo).

    Returns:
        La lunghezza del cammino minimo, oppure infinito se la destinazione è irraggiungibile
        (o una delle due celle è occupata da un ostacolo). Il percorso non viene ricostruito:
        all'oracolo serve solo la lunghezza.
    """
    if grid_state[origin] != 0 or grid_state[dest] != 0:
        return float('inf')
    if origin == dest:
        return 0.0

    rows, cols = grid_state.shape
    g_cost: dict[Coordinate, float] = {origin: 0.0}
    # Coda a priorità di tuple (f = g + h, cella)
    open_heap: list[tuple[float, Coordinate]] = [(dlib(origin, dest), origin)]
    closed: set[Coordinate] = set()

    while open_heap:
        f_val, cell = heapq.heappop(open_heap)
        if cell == dest:
            return g_cost[cell]
        if cell in closed:
            continue
        closed.add(cell)

        r, c = cell
        for dr, dc, step in _MOSSE:
            nr, nc = r + dr, c + dc
            if not (0 <= nr < rows and 0 <= nc < cols) or grid_state[nr, nc] != 0:
                continue
            neighbor = (nr, nc)
            tentative = g_cost[cell] + step
            if tentative < g_cost.get(neighbor, float('inf')):
                g_cost[neighbor] = tentative
                heapq.heappush(open_heap, (tentative + dlib(neighbor, dest), neighbor))

    return float('inf')
