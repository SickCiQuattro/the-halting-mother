"""Stile e palette condivisi per le figure della relazione (Compito 4).

Palette Okabe-Ito (colorblind-safe), assegnata in modo fisso alle entità
categoriche ricorrenti nelle figure (potatura debole/forte, direzione di
percorrenza), mai ciclata automaticamente da matplotlib.
"""
import matplotlib

COLOR_DEBOLE = "#D55E00"    # potatura debole (riga 16) — vermiglio
COLOR_FORTE = "#0072B2"     # potatura forte (riga 17) — blu
COLOR_ANDATA = "#CC79A7"    # direzione O -> D — porpora
COLOR_RITORNO = "#009E73"   # direzione D -> O / ritorno — verde-blu
COLOR_TIMEOUT = "#404040"   # marcatore di stato "tempo limite raggiunto"
COLOR_GRID = "#B0B0B0"


def apply_style() -> None:
    """Applica font, griglia e spine condivise a tutte le figure della relazione."""
    matplotlib.rcParams.update({
        "font.size": 10,
        "axes.titlesize": 12,
        "axes.titleweight": "bold",
        "axes.labelsize": 10,
        "axes.edgecolor": "#4d4d4d",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "grid.color": COLOR_GRID,
        "grid.linewidth": 0.6,
        "grid.alpha": 0.5,
        "legend.fontsize": 9,
        "legend.frameon": False,
        "savefig.bbox": "tight",
    })
