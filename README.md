# Algoritmi e Strutture Dati: elaborato accademico 2024/25

Progetto accademico per il corso di *Algoritmi e Strutture Dati* (a.a. 2024/25, Prof.ssa Zanella).  
Sviluppato in **Python 3.13** rispettando i requisiti completi per **gruppi di 3 persone**.

L'architettura affronta la scalabilità su griglie di grandi dimensioni (fino a $150 \times 150$ nella campagna sperimentale) grazie alla potatura branch-and-bound con limite superiore globale, e produce visualizzazioni ad alta risoluzione allineate alla specifica.

---

## Caratteristiche architetturali e ottimizzazioni

1. **Potatura branch-and-bound con limite superiore globale**:
   - La condizione di riga 16/17 viene valutata rispetto a un limite superiore globale $L_{\text{glob}}$, condiviso da tutte le invocazioni ricorsive e aggiornato ogni volta che si trova un cammino completo più breve. Finché non se ne trova uno, $L_{\text{glob}}$ vale $+\infty$ e non si pota nulla.
   - Poiché $d_{\text{lib}}$ non sovrastima mai la distanza reale, la stima è ammissibile e la potatura non scarta mai il cammino ottimo. Il limite emerge dalla ricerca stessa: non è richiesta alcuna passata preliminare.

2. **Ritracciamento sul posto su matrice numpy `uint8`**:
   - Evita la duplicazione degli stati e il relativo onere sul raccoglitore di memoria. Le celle occupate dalla chiusura ricorsiva corrente sono marcate con il valore costante `2` (ostacolo temporaneo) e ripristinate a `0` (libere) durante la risalita.

3. **Proiezione di raggi per le chiusure ($O(\max(R, C)^2)$)**:
   - Evita la scansione diretta $O(R^2 \cdot C^2)$ proiettando raggi cardinali e diagonali dall'origine con espansione a gomito.

4. **Visualizzazione ibrida ad alta risoluzione**:
   - Resa grafica a 200 DPI con pixel nitidi (`interpolation='nearest'`).
   - Evidenziazione semitrasparente in azzurro del percorso completo.
   - Spezzata blu tra i landmark con marcatori romboidali dorati a bordo rosso ed etichettatura numerica centrata ($O \rightarrow 1 \rightarrow 2 \rightarrow D$).

---

## Installazione

Le istruzioni valgono in modo identico su macOS, Linux e Windows: cambia solo il comando di attivazione dell'ambiente virtuale.

1. Crea l'ambiente virtuale con Python 3.13:
   ```bash
   python3.13 -m venv .venv        # macOS / Linux
   py -3.13 -m venv .venv          # Windows (PowerShell o prompt dei comandi)
   ```
2. Attiva l'ambiente virtuale:
   ```bash
   source .venv/bin/activate       # macOS / Linux
   .venv\Scripts\Activate.ps1      # Windows PowerShell
   .venv\Scripts\activate.bat      # Windows prompt dei comandi
   ```
3. Installa il progetto in modalità modificabile (rende `src` importabile da qualunque cartella di lavoro, senza dover impostare `PYTHONPATH`):
   ```bash
   pip install -e .
   ```

---

## Utilizzo CLI (`main.py`)

Una volta attivato l'ambiente virtuale, tutti i comandi si lanciano con il semplice interprete `python`, identico sui due sistemi operativi.

### 1. Generazione di griglie (Compito 1)
Genera ostacoli misti (`simple`, `cluster`, `diagonal`, `enclosure`, `bar` o `mix`) e salva la griglia strutturata ed un'immagine PNG ad alta risoluzione:
```bash
python main.py generate --rows 50 --cols 50 --types mix --density 0.2 --seed 42 -o grids/grid.json --save-img results/test_grid_generated.png
```

### 2. Calcolo del contesto e complemento (Compito 2)
Espande i raggi per calcolare Contesto (Tipo 1), Complemento (Tipo 2) e Frontiera di una coordinata origine:
```bash
python main.py context --grid grids/grid.json --origin 10,10 --type both
```

### 3. Calcolo della distanza ideale ($d_{\text{lib}}$)
Calcola la distanza minima teorica priva di ostacoli su una griglia con adiacenza a otto direzioni:
```bash
python main.py dlib --origin 10,10 --dest 40,40
```

### 4. Calcolo del cammino minimo (`CAMMINOMIN`, Compito 3)
Esegue l'algoritmo ricorsivo di ricerca del cammino minimo con la potatura branch-and-bound a limite superiore globale. Esporta la sequenza dei landmark e produce l'immagine ad alta risoluzione del cammino:
```bash
python main.py camminomin --grid grids/grid.json --origin 0,0 --dest 49,49 --strong-pruning --summary --save-img results/test_path_resolved.png
```
*Il flag `--summary` stampa il riassunto strutturato in formato JSON.*

### 5. Campagna sperimentale e grafici (Compito 4)
Esegue l'intera batteria di prove temporali e spaziali (memoria) su più coppie origine-destinazione per configurazione, con doppia invocazione O→D e D→O su ogni coppia, e genera i 6 grafici nella cartella `results/`:
```bash
python main.py experiment --output-dir results
```

Per lanciare la verifica formale di simmetria ($O \leftrightarrow D$ contro $D \leftrightarrow O$) su $N$ coppie casuali di nodi:
```bash
python main.py experiment --verify-symmetry-count 10 --symmetry-grid-size 20
```

---

## Esecuzione dei test unitari
Tutti i componenti logici e matematici del progetto sono coperti da test automatici:
```bash
python -m unittest discover -s tests -p "test_*.py"
```
