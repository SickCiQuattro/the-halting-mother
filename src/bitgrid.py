"""
Rappresentazione alternativa della griglia a bit impacchettati (pag. 63 e 72 dell'elaborato:
confronto di implementazioni relativamente alle strutture dati; strutture che estendono le
taglie elaborabili).

La matrice `uint8` standard usa 1 byte per cella, ma gli stati logici necessari sono tre
(0 libera, 1 ostacolo fisso, 2 ostacolo temporaneo): bastano due piani di bit, uno per gli
ostacoli fissi e uno per le marcature temporanee, cioè 2 bit per cella, con un'occupazione
di memoria pari a circa 1/4. Il prezzo è l'accesso per singola cella tramite operazioni sui
bit in Python puro, atteso più lento di svariate volte rispetto all'indicizzazione numpy
diretta: il compromesso spazio/tempo è quantificato in `scripts/verifica_griglia_bit.py`.

La classe espone la stessa interfaccia duck-typed usata dagli algoritmi esistenti
(`.shape`, accesso e assegnazione con tupla `(riga, colonna)`, `.copy()`), quindi
`compute_context_rays`, `compute_complement_rays`, `compute_frontier`, `camminomin` e
`compute_components` operano sull'oggetto impacchettato senza alcuna modifica.
"""
import numpy as np

from src.grid import Coordinate


class BitPackedGrid:
    """Griglia a due piani di bit impacchettati (8 celle per byte, per riga)."""

    def __init__(self, rows: int, cols: int) -> None:
        if rows <= 0 or cols <= 0:
            raise ValueError(f"Le dimensioni della griglia devono essere positive. Ricevute: ({rows}x{cols})")
        self.rows = rows
        self.cols = cols
        packed_cols = (cols + 7) // 8
        # Piano degli ostacoli fissi e piano delle marcature temporanee
        self._fixed = np.zeros((rows, packed_cols), dtype=np.uint8)
        self._temp = np.zeros((rows, packed_cols), dtype=np.uint8)

    @classmethod
    def from_array(cls, state: np.ndarray) -> 'BitPackedGrid':
        """Costruisce la griglia impacchettata da una matrice di stati 0/1/2 esistente."""
        rows, cols = state.shape
        grid = cls(rows, cols)
        for r in range(rows):
            for c in range(cols):
                val = int(state[r, c])
                if val:
                    grid[r, c] = val
        return grid

    @property
    def shape(self) -> tuple[int, int]:
        return (self.rows, self.cols)

    @property
    def nbytes(self) -> int:
        """Byte effettivi dei due piani (per il confronto di memoria con la matrice uint8)."""
        return self._fixed.nbytes + self._temp.nbytes

    def __getitem__(self, cell: Coordinate) -> int:
        r, c = cell
        byte, bit = c >> 3, 1 << (c & 7)
        if self._fixed[r, byte] & bit:
            return 1
        if self._temp[r, byte] & bit:
            return 2
        return 0

    def __setitem__(self, cell: Coordinate, value: int) -> None:
        r, c = cell
        byte, bit = c >> 3, 1 << (c & 7)
        if value == 0:
            self._fixed[r, byte] &= ~bit & 0xFF
            self._temp[r, byte] &= ~bit & 0xFF
        elif value == 1:
            self._fixed[r, byte] |= bit
            self._temp[r, byte] &= ~bit & 0xFF
        elif value == 2:
            self._temp[r, byte] |= bit
            self._fixed[r, byte] &= ~bit & 0xFF
        else:
            raise ValueError(f"Stato di cella non valido: {value} (ammessi 0, 1, 2)")

    def copy(self) -> 'BitPackedGrid':
        nuovo = BitPackedGrid(self.rows, self.cols)
        nuovo._fixed = self._fixed.copy()
        nuovo._temp = self._temp.copy()
        return nuovo

    def to_array(self) -> np.ndarray:
        """Espande i piani di bit nella matrice uint8 equivalente (per test e visualizzazione)."""
        state = np.zeros((self.rows, self.cols), dtype=np.uint8)
        for r in range(self.rows):
            for c in range(self.cols):
                state[r, c] = self[r, c]
        return state
