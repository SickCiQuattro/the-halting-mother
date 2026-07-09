import os
import logging
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from src.grid import Grid, Coordinate

logger = logging.getLogger(__name__)

def save_grid_image(
    grid: Grid,
    output_path: str,
    origin: Coordinate | None = None,
    dest: Coordinate | None = None,
    path: list[Coordinate] | None = None,
    landmarks: list[tuple[Coordinate, int]] | None = None,
    title: str | None = None
) -> None:
    """
    Genera e salva un'immagine PNG ad alta definizione (2000x2000 px) della griglia
    con visualizzazione ibrida del percorso.

    Args:
        grid: L'oggetto Grid da renderizzare.
        output_path: Percorso del file PNG di output.
        origin: Coordinata di origine (row, col).
        dest: Coordinata di destinazione (row, col).
        path: Lista ordinata di celle fisiche del cammino completo ricostruito.
        landmarks: Sequenza ordinata di landmark (cella, tipo_cammino) per la spezzata.
        title: Titolo opzionale del grafico.
    """
    rows, cols = grid.rows, grid.cols
    
    # 1. Definizione della ListedColormap discreta
    # 0: bianco (libero)
    # 1: blu navy (ostacolo fisso)
    # da 2 in poi: giallo spento (ostacolo temporaneo)
    colors = ['#ffffff', '#002060'] + ['#ffeaa7'] * 254
    custom_cmap = ListedColormap(colors)

    # 2. Inizializzazione della figura ad alta risoluzione (headless)
    # Utilizziamo dimensioni proporzionali ma ampie, con DPI elevato per output 2000x2000 px nominale
    fig, ax = plt.subplots(figsize=(12, 12), dpi=200)

    # 3. Disegno dello stato delle celle della griglia con interpolation='nearest'
    # vmin/vmax fissi a 0/255 forzano la mappatura letteraria valore->indice della colormap,
    # altrimenti imshow normalizza sul min/max effettivo dei dati (es. 0/1 per una griglia
    # senza ostacoli temporanei) facendo cadere il valore 1 quasi alla fine della LUT a 256 colori.
    ax.imshow(
        grid.state,
        cmap=custom_cmap,
        vmin=0,
        vmax=255,
        interpolation='nearest',
        origin='upper',
        extent=[-0.5, cols - 0.5, rows - 0.5, -0.5]  # Imposta i limiti precisi degli assi
    )

    # 4. Disegno dinamico del reticolo della scacchiera
    if rows <= 100:
        # Disegna linee orizzontali e verticali di divisione per griglie medio-piccole
        for r in range(rows + 1):
            ax.axhline(r - 0.5, color='#dfe6e9', linewidth=0.5, zorder=1)
        for c in range(cols + 1):
            ax.axvline(c - 0.5, color='#dfe6e9', linewidth=0.5, zorder=1)

    # 5. Evidenziazione semitrasparente (azzurro) delle celle fisiche del percorso completo
    if path:
        for r, c in path:
            # Per matplotlib X=col, Y=row. Matrice origin='upper' inverte direzione asse Y
            rect = plt.Rectangle(
                (c - 0.5, r - 0.5), 1, 1,
                facecolor='#0984e3',
                alpha=0.35,
                edgecolor='none',
                zorder=2
            )
            ax.add_patch(rect)

    # 6. Disegno della spezzata dei landmark e dei marcatori geometrici
    if landmarks:
        # Estrae le coordinate cartesiane X, Y (col, row) per allineamento sub-pixel perfetto
        lm_cols = [coord[1] for coord, _ in landmarks]
        lm_rows = [coord[0] for coord, _ in landmarks]

        # Disegna la linea segmentata spessa che connette i landmark
        ax.plot(
            lm_cols,
            lm_rows,
            color='#0984e3',
            linewidth=3.5,
            linestyle='-',
            zorder=3
        )

        # Disegna i marcatori romboidali dorati sui landmark
        ax.scatter(
            lm_cols,
            lm_rows,
            color='#fdcb6e',
            edgecolor='#d63031',
            s=220,
            marker='D',
            zorder=4
        )

        # Aggiunge le etichette testuali geometriche (O -> 1 -> 2 -> ... -> D) centrate sui marcatori
        for idx, (coord, _) in enumerate(landmarks):
            r, c = coord
            if idx == 0:
                label = 'O'
            elif idx == len(landmarks) - 1:
                label = 'D'
            else:
                label = str(idx)

            ax.text(
                c,
                r,
                label,
                color='#2d3436',
                fontsize=10,
                fontweight='bold',
                ha='center',
                va='center',
                zorder=5
            )
    else:
        # Fallback se non ci sono i landmark ma abbiamo origine e destinazione
        if origin is not None:
            ax.scatter(origin[1], origin[0], color='#2ed573', edgecolor='#2d3436', s=250, marker='o', zorder=4)
            ax.text(origin[1], origin[0], 'O', color='#ffffff', fontsize=11, fontweight='bold', ha='center', va='center', zorder=5)
        if dest is not None:
            ax.scatter(dest[1], dest[0], color='#ff4757', edgecolor='#2d3436', s=250, marker='o', zorder=4)
            ax.text(dest[1], dest[0], 'D', color='#ffffff', fontsize=11, fontweight='bold', ha='center', va='center', zorder=5)

    # 7. Formattazione e decorazione del grafico
    if title:
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)

    ax.set_xlabel("Colonne", fontsize=10)
    ax.set_ylabel("Righe", fontsize=10)
    
    # Visualizza i tick a intervalli regolari
    ax.set_xticks(np.arange(0, cols, max(1, cols // 10)))
    ax.set_yticks(np.arange(0, rows, max(1, rows // 10)))
    
    ax.set_xlim(-0.5, cols - 0.5)
    ax.set_ylim(rows - 0.5, -0.5)  # Invertito per mantenere Y decrescente (0 in alto)
    ax.grid(False)

    # 8. Salvataggio ed esportazione del PNG ad alta definizione
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight')
    plt.close()
    logger.info(f"Immagine della griglia salvata con successo in: {output_path}")
