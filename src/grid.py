import json
import numpy as np
from collections import deque
from typing import List
from src.exceptions import InvalidCoordinateError

# Definizione alias di tipo per una maggiore leggibilità e astrazione
Coordinate = tuple[int, int]

class Grid:
    """
    Rappresenta la griglia di transito 8-connected per l'algoritmo di pathfinding.

    La griglia è supportata internamente da un array numpy a due dimensioni di tipo `uint8`:
      - 0: Cella libera (traversabile)
      - 1: Ostacolo fisso (permanente)
      - 2: Ostacolo temporaneo, marcatura della chiusura corrente durante l'esplorazione
           ricorsiva (backtracking); ripristinato a 0 in fase di risalita.
    """

    def __init__(self, rows: int, cols: int) -> None:
        """
        Inizializza una griglia vuota di dimensioni specificate.

        Args:
            rows: Numero di righe della griglia.
            cols: Numero di colonne della griglia.

        Raises:
            ValueError: Se rows o cols sono inferiori o uguali a zero.
        """
        if rows <= 0 or cols <= 0:
            raise ValueError(f"Le dimensioni della griglia devono essere positive. Ricevute: ({rows}x{cols})")
            
        self.rows: int = rows
        self.cols: int = cols
        self.state: np.ndarray = np.zeros((rows, cols), dtype=np.uint8)
        # Tipologie di ostacoli con cui la griglia è stata generata (richiesto dal riassunto, Slide 71)
        self.types: List[str] = []

    def is_valid(self, row: int, col: int) -> bool:
        """
        Verifica se una coordinata (row, col) rientra nei limiti geografici della griglia.

        Args:
            row: Indice di riga da verificare.
            col: Indice di colonna da verificare.

        Returns:
            True se la coordinata è all'interno della griglia, False altrimenti.
        """
        return 0 <= row < self.rows and 0 <= col < self.cols

    def is_traversable(self, row: int, col: int) -> bool:
        """
        Verifica se una cella è valida ed è libera da ostacoli (sia fissi che temporanei).

        Args:
            row: Indice di riga della cella.
            col: Indice di colonna della cella.

        Returns:
            True se la cella è attraversabile, False altrimenti.
        """
        return self.is_valid(row, col) and self.state[row, col] == 0

    def set_obstacle(self, row: int, col: int) -> None:
        """
        Imposta un ostacolo fisso (permanente) nella cella specificata.

        Args:
            row: Indice di riga.
            col: Indice di colonna.

        Raises:
            InvalidCoordinateError: Se la coordinata è fuori dai limiti della griglia.
        """
        if not self.is_valid(row, col):
            raise InvalidCoordinateError(f"Impossibile posizionare ostacolo: coordinata ({row}, {col}) non valida.")
        self.state[row, col] = 1

    def clear_cell(self, row: int, col: int) -> None:
        """
        Libera la cella impostando il suo stato a 0 (traversabile).

        Args:
            row: Indice di riga.
            col: Indice di colonna.

        Raises:
            InvalidCoordinateError: Se la coordinata è fuori dai limiti della griglia.
        """
        if not self.is_valid(row, col):
            raise InvalidCoordinateError(f"Impossibile liberare la cella: coordinata ({row}, {col}) non valida.")
        self.state[row, col] = 0

    def save(self, path: str) -> None:
        """
        Salva lo stato strutturato della griglia (dimensioni e posizioni degli ostacoli fissi)
        in un file JSON leggibile.

        Args:
            path: Percorso del file JSON in cui scrivere la griglia.
        """
        obstacles: List[List[int]] = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.state[r, c] == 1:
                    obstacles.append([r, c])
        
        data = {
            "rows": self.rows,
            "cols": self.cols,
            "types": self.types,
            "obstacles": obstacles
        }
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, path: str) -> 'Grid':
        """
        Carica la configurazione di una griglia da un file JSON precedentemente salvato.

        Args:
            path: Percorso del file JSON da cui caricare la griglia.

        Returns:
            Un'istanza della classe Grid pre-popolata con gli ostacoli caricati.
        """
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        grid = cls(data["rows"], data["cols"])
        grid.types = data.get("types", [])
        for r, c in data["obstacles"]:
            grid.set_obstacle(r, c)
        return grid

    def __repr__(self) -> str:
        """
        Ritorna una rappresentazione ASCII compatta ed esteticamente pulita della griglia.
        Utile per il debug visuale rapido.
        """
        lines = []
        for r in range(self.rows):
            row_str = []
            for c in range(self.cols):
                val = self.state[r, c]
                if val == 1:
                    row_str.append("#")  # Ostacolo fisso
                elif val > 1:
                    row_str.append("T")  # Ostacolo temporaneo (Backtracking)
                else:
                    row_str.append(".")  # Cella libera
            lines.append(" ".join(row_str))
        return "\n".join(lines)


def compute_components(grid_state: np.ndarray) -> np.ndarray:
    """
    Etichetta ogni cella libera con l'identificativo del proprio componente connesso.

    Usa un riempimento a inondazione iterativo (BFS con coda) sul vicinato a 8: per la
    specifica dell'elaborato (pag. 3) l'attraversamento diagonale fra due celle libere è
    sempre ammesso, anche quando due ostacoli si toccano per lo spigolo, quindi la
    connettività a 8 coincide esattamente con la raggiungibilità. Due celle libere sono
    quindi mutuamente raggiungibili se e solo se hanno la stessa etichetta.

    Costo: O(R*C) in tempo e spazio.

    Args:
        grid_state: Matrice degli stati della griglia (0 libera, >0 ostacolo).

    Returns:
        Matrice int32 della stessa forma: etichetta di componente (0, 1, 2, ...) per le
        celle libere, -1 per le celle occupate da ostacoli.
    """
    rows, cols = grid_state.shape
    labels = np.full((rows, cols), -1, dtype=np.int32)
    current_label = 0

    for r in range(rows):
        for c in range(cols):
            if grid_state[r, c] != 0 or labels[r, c] != -1:
                continue
            # Nuova componente: inondazione BFS a partire da (r, c)
            labels[r, c] = current_label
            queue: deque[Coordinate] = deque([(r, c)])
            while queue:
                cr, cc = queue.popleft()
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = cr + dr, cc + dc
                        if (0 <= nr < rows and 0 <= nc < cols
                                and grid_state[nr, nc] == 0 and labels[nr, nc] == -1):
                            labels[nr, nc] = current_label
                            queue.append((nr, nc))
            current_label += 1

    return labels
