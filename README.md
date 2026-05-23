# Algoritmi e Strutture Dati — Elaborato Accademico 2024/25

Progetto accademico per il corso di *Algoritmi e Strutture Dati* (a.a. 2024/25, Prof.ssa Zanella).  
Sviluppato in **Python 3.13** rispettando i requisiti completi per **gruppi di 3 persone**.

L'architettura risolve in modo definitivo la scalabilità asintotica su griglie di grandi dimensioni ($100 \times 100$, $150 \times 150$ e $200 \times 200$) grazie all'introduzione della tecnica **Global Min Length Seeding (v4)** e presenta una suite di rendering premium allineata alla **Slide 53** delle specifiche.

---

## Caratteristiche Architetturali ed Ottimizzazioni

1. **Global Min Length Seeding (Breccia nel Paradosso della Cache)**:
   - *Il Problema*: Su grandi griglie, l'insieme dinamico `frozen_cells` (necessario per l'esattezza matematica in cache) cambia continuamente ad ogni livello di ricorsione, portando l'efficacia della memoizzazione a zero e causando timeout sistematici.
   - *La Soluzione*: Esecuzione di una corsa preliminare **Greedy pura** (senza backtracking) con cache isolata (`path_cache=None`) per identificare in millisecondi un limite superiore reale ($L_{\text{ottimo}} \le L_{\text{greedy}}$).
   - Inserendo questo valore nel pruning globale, le chiamate ricorsive non ottimali vengono potate all'istante nei piani alti dell'albero, prevenendo l'esplosione dei nodi profondi.

2. **Backtracking in-place su Matrice numpy `uint8`**:
   - Evita l'overhead del Garbage Collector dovuto alla duplicazione degli stati. Le celle occupate dalla chiusura ricorsiva corrente sono marcate in-place tramite `depth_id = depth + 2` e ripristinate a `0` (libere) durante la risalita (pop).

3. **Ottimizzazione Ray-Casting per Chiusure ($O(\max(R, C)^2)$)**:
   - Evita la scansione naive $O(R^2 \cdot C^2)$ proiettando raggi cardinali e diagonali dall'origine con espansione a gomito, garantendo performance eccellenti.

4. **Visualizzazione Premium Ibrida (Slide 53)**:
   - Rendering ad alta risoluzione (DPI 200, pixel cristallini via `interpolation='nearest'`).
   - Evidenziazione semitrasparente in azzurro del percorso completo.
   - Spezzata blu tra i landmark con grandi marker romboidali dorati a bordo rosso ed etichettatura numerica centrata ($O \rightarrow 1 \rightarrow 2 \rightarrow D$).

---

## Installazione

1. Crea l'ambiente virtuale con Python 3.13:
   ```bash
   python3.13 -m venv .venv
   ```
2. Attiva l'ambiente virtuale:
   ```bash
   source .venv/bin/activate
   ```
3. Installa le dipendenze:
   ```bash
   pip install -r requirements.txt
   ```

---

## Utilizzo CLI (`main.py`)

Tutti i comandi CLI devono essere eseguiti con il prefisso `PYTHONPATH=.` ed utilizzando l'interprete dell'ambiente virtuale `.venv/bin/python`.

### 1. Generazione di Griglie (Compito 1)
Genera ostacoli misti (`simple`, `cluster`, `diagonal`, `enclosure`, `bar` o `mix`) e salva la griglia strutturata ed un'immagine PNG ad alta risoluzione:
```bash
PYTHONPATH=. .venv/bin/python main.py generate --rows 50 --cols 50 --types mix --density 0.2 --seed 42 -o grids/grid.json --save-img results/test_grid_generated.png
```

### 2. Calcolo del Contesto e Complemento (Compito 2)
Espande i raggi per calcolare Contesto (Tipo 1), Complemento (Tipo 2) e Frontiera di una coordinata origine:
```bash
PYTHONPATH=. .venv/bin/python main.py context --grid grids/grid.json --origin 10,10 --type both
```

### 3. Calcolo della Distanza Ideale ($d_{\text{lib}}$)
Calcola la distanza minima teorica priva di ostacoli su una griglia 8-connected:
```bash
PYTHONPATH=. .venv/bin/python main.py dlib --origin 10,10 --dest 40,40
```

### 4. Calcolo del Cammino Minimo (`CAMMINOMIN` - Compito 3)
Esegue l'algoritmo di pathfinding ricorsivo con la v4 attiva. Esporta la sequenza dei landmark e produce l'immagine premium del cammino ibrido (Slide 53):
```bash
PYTHONPATH=. .venv/bin/python main.py camminomin --grid grids/grid.json --origin 0,0 --dest 49,49 --strong-pruning --summary --save-img results/test_path_resolved.png
```
*Il flag `--summary` stampa il riassunto strutturato in formato JSON (Slide 71).*

### 5. Campagna Sperimentale e Grafici (Compito 4)
Esegue l'intera suite di benchmark temporali e spaziali (memoria) e genera i 6 grafici di report nella cartella `results/` (incluso lo scaling Log-Log con **3 curve distinte**):
```bash
PYTHONPATH=. .venv/bin/python main.py experiment --output-dir results
```

Per lanciare la verifica formale di simmetria ($O \leftrightarrow D$ vs $D \leftrightarrow O$) su $N$ coppie casuali di nodi:
```bash
PYTHONPATH=. .venv/bin/python main.py experiment --verify-symmetry-count 10 --symmetry-grid-size 20
```

---

## Esecuzione dei Test Unitari
Tutti i componenti logici e matematici del progetto sono coperti da test automatici:
```bash
PYTHONPATH=. .venv/bin/python -m unittest discover -s tests -p "test_*.py"
```
