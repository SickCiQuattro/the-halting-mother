"""Helper condivisi fra gli script di riproducibilità in scripts/.

Va importato per primo (prima di `matplotlib.pyplot`) perché imposta il backend
headless "Agg", necessario per generare figure senza un display disponibile.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402 (import intenzionalmente dopo la scelta del backend)

from src.generator import GridGenerator
from src.grid import Grid, Coordinate

__all__ = ["plt", "griglia_campagna_scaling"]


def griglia_campagna_scaling(size: int) -> tuple[Grid, Coordinate, Coordinate]:
    """Griglia e coppia d'angolo della campagna di scaling (seed 42, densità 0.2,
    tipologie simple+cluster+bar), riprodotta identica da più script di verifica."""
    grid = GridGenerator.generate_grid(size, size, ["simple", "cluster", "bar"], density=0.2, seed=42)
    origin, dest = (0, 0), (size - 1, size - 1)
    grid.clear_cell(*origin)
    grid.clear_cell(*dest)
    return grid, origin, dest
