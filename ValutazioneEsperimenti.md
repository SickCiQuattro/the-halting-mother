# Valutazione della campagna sperimentale — Compito 4

**Ambito:** elaborato ASD 2024/25, gruppo di 3 persone, obiettivo lode.
**Oggetto:** la campagna sperimentale esistente (`results/`, `scripts/`, `src/experiment*.py`) e la
sua esposizione in `Relazione/5-CompitoQuattro/CompitoQuattro.tex`.
**Asticella di riferimento:** requisiti pieni del gruppo da 3 (diapositive 37–38, 67, 71
dell'elaborato — ricostruzione del cammino, confronto riga 16/17, interruzione con risultato
parziale), più le indicazioni generali di sperimentazione delle diapositive 63–68.

---

## 1. Sintesi e verdetto

La campagna copre **tutti** i requisiti obbligatori del gruppo da 3 e aggiunge materiale che va
oltre lo spec (oracolo A* indipendente, divario di ottimalità anytime, confronto di strutture dati
byte/bit-plane). Su questa base è già **sopra la sufficienza per la lode**.

Tuttavia un esame incrociato dei JSON in `results/` rivela un problema metodologico non
cosmetico: **la curva che il grafico principale (densità/transizione di fase) racconta è
contraddetta di 2–3 ordini di grandezza dalla stessa campagna multi-seme presente nella
relazione**. Questo non è un dettaglio — è la figura che apre la sezione sperimentale e la
metafora concettuale (transizione di fase) che la relazione costruisce sopra. A questo si
aggiungono un'analisi spaziale sotto-sviluppata rispetto a quanto lo spec richiede esplicitamente
e due ottimizzazioni implementate ma non misurate in modo sistematico.

**Verdetto: campagna promossa, materiale da lode presente, ma non ancora pronta così com'è.** Le
criticità sono risolvibili senza ripartire da zero (si veda `PianoMiglioramentoEsperimenti.md`).

---

## 2. Metodo di valutazione

La valutazione confronta tre fonti indipendenti per ogni affermazione:
1. il testo della consegna (`doc/AlgoritmiElaborato.md`),
2. il codice che produce i dati (`src/camminomin.py`, `src/experiment_runner.py`,
   `src/generator.py`, `main.py`),
3. i dati stessi (`results/*.json`) e il testo che li descrive (`CompitoQuattro.tex`).

Un punto di forza è tale solo se il codice fa davvero quello che il testo dichiara. Una criticità è
segnalata solo se ha un riscontro numerico verificabile in un file specifico — non impressioni
qualitative.

---

## 3. Conformità ai requisiti (mappa)

| Requisito spec | Diapositiva | Stato | Evidenza |
|---|---|---|---|
| Verifica di simmetria O↔D | 64 | ✅ | `simmetria_campagna.json`: 64/81 coppie verificabili, 0 fallite |
| Confronto potatura riga 16 vs riga 17 | 67 (gruppi da 3) | ✅ | `pruning_comparison.json` |
| Confronto ordinamento euristico vs casuale frontiera | 65–66 | ✅ | `ordering_comparison.json` |
| Crescita asintotica in scala log-log | 65 | ✅ | `scaling_results.json`, fino a lato 150, timeout 600s |
| Prestazioni **temporali** | 65, 71 | ✅ | tutti i benchmark |
| Prestazioni **spaziali** | 65, 71 | ⚠️ parziale | `peak_memory_kb` raccolto ma non graficato a livello di algoritmo (§5.4, criticità C4) |
| Riassunto strutturato dell'esecuzione | 71 | ✅ | `main.py cmd_camminomin --summary`, campi conformi |
| Interruzione con risultato parziale (gruppi 3) | 71 | ✅ | `timed_out` + miglior cammino parziale sempre restituito |
| Ricostruzione del cammino da landmark (gruppi 3) | 38 | ✅ | `reconstruct_path` in `src/camminomin.py` |
| Tutte le tipologie del Compito 1, incluse combinazioni | 8–9, 207 | ✅ | tabella di conformità in `CompitoQuattro.tex` §5.4, `mix_comparison.json`, `maze_results.json` |
| Doppia invocazione O↔D per ogni coppia distinta usata | 64 | ✅ | verificato su scaling, densità, potatura |
| Confronto fra strutture dati diverse | 63, 72 | ✅ | `BitPackedGrid`, `verifica_griglia_bit.py` |

Tutti i requisiti letterali risultano soddisfatti. Le criticità che seguono riguardano **la
qualità metodologica** dell'evidenza raccolta, non la sua presenza.

---

## 4. Punti di forza

### F1 — Doppia verifica di correttezza indipendente
La simmetria O↔D (condizione **necessaria** richiesta dalla diapositiva 64) è integrata da un
oracolo A* indipendente (condizione **sufficiente**). L'argomento è corretto: la distanza $d_{lib}$
già definita nel Compito 2 è esattamente la distanza octile, euristica ammissibile e consistente
sul grafo delle celle — quindi A* restituisce sempre l'ottimo esatto. `tests/test_astar.py`
confronta le due implementazioni su 20 griglie casuali con tolleranza $10^{-9}$;
`scripts/verifica_oracolo_astar.py` rivalida ex post tutte le esecuzioni completate dello scaling.
Nessun'altra verifica nella campagna raggiunge questo livello di rigore.

### F2 — Metodologia di misura curata
La separazione fra misura del tempo (senza profilazione) e misura della memoria (con
`tracemalloc`, in una passata separata) è motivata e quantificata: la profilazione introduce un
sovraccarico di circa 5× (da 1,7 s a 9,6 s su una prova a 50×50, documentato in `CompitoQuattro.tex`
§5.3). L'aggregazione a mediana e la marcatura esplicita dei timeout con un marcatore dedicato
(evitando di leggere un tempo di completamento dove non c'è) sono scelte corrette e non scontate.

### F3 — Copertura delle tipologie di ostacolo completa
Le cinque tipologie del Compito 1 sono tutte generate (`src/generator.py`) e tutte misurate
singolarmente (potatura, ordinamento, simmetria per tipo). La combinazione `mix` è misurata a
parte (`mix_comparison.json`) e il caso limite "barre disposte a formare un labirinto" citato
letteralmente dallo spec (diapositiva 8) ha un generatore dedicato (`generate_maze`) con
connessione garantita per costruzione, non affidata al caso.

### F4 — Onestà intellettuale e correttezza dell'interpretazione fisica
Il codice documenta esplicitamente una scelta implementativa abbandonata: la memoizzazione dei
sotto-problemi è stata rimossa perché il risultato dipendeva, tramite la potatura globale, da uno
stato non incluso nella chiave — violava la simmetria O–D/D–O (commento in `camminomin.py`, righe
130–136). Questo è il segno di un debug reale, non di codice mai stressato. L'interpretazione della
transizione di fase come fenomeno di percolazione (comparsa di corridoi critici non prevedibile
dalla sola densità media) è corretta e ben argomentata nel testo.

### F5 — Divario anytime come lettura quantitativa del "muro esponenziale"
Il confronto fra i cammini restituiti dalle esecuzioni interrotte e l'ottimo esatto di A*
(`divario_anytime.json`) dà una scala al risultato parziale richiesto dalla diapositiva 71: mostra
che l'algoritmo interrotto è un buon approssimato fino a lato 100 (potatura forte: 0,4% dall'ottimo)
e degrada solo a lato 150 (9–20% a seconda della configurazione). Senza questo confronto
"interrotto" sarebbe un dato qualitativo; con A* diventa una misura.

---

## 5. Criticità

### C1 — [ALTA] La figura headline sulla densità è a seme singolo ed è contraddetta dalla stessa campagna multi-seme

`CompitoQuattro.tex` §5.4.1 (`1_time_vs_density.png`, dati in `density_results.json`, seed=100)
afferma: su griglia 50×50 il tempo mediano resta **sotto i 10 ms fino a densità 0,35**.

`multiseme_results.json` (semi 301–305, stessa taglia 50×50, stesse tipologie `simple+cluster`,
stessa coppia d'angolo) dà, per la **stessa combinazione taglia/densità**:
- densità 0,15: mediana **3,66 s**, IQR fino a 14,9 s, 1 seme su 5 in timeout;
- densità 0,25: mediana **7,13 s**, IQR fino a 15,0 s, 2 semi su 5 in timeout.

Discrepanza di **2–3 ordini di grandezza** fra due misure che, sulla carta, descrivono la stessa
cosa. La causa non è un errore di implementazione (`simmetria_campagna.json` conferma 0 fallimenti
di simmetria su 64 coppie verificabili — l'algoritmo è corretto), ma una scelta metodologica: la
curva §5.4.1 fa mediana su **5 coppie diverse** (l'angolo + 4 casuali, spesso quasi banali, come
mostra `elapsed_time_s: 0.008` a densità 0,05 nel primo campione), mentre il seme è **unico**. La
campagna multi-seme isola invece la sola coppia d'angolo su **5 disposizioni diverse** di ostacoli
alla stessa densità nominale. Mediare su coppie eterogenee **diluisce sistematicamente** il caso
difficile: un risultato "fortunato" a bassa densità (coppia diretta, 1 chiamata ricorsiva) abbassa
la mediana anche quando la coppia d'angolo, nella stessa griglia, richiederebbe migliaia di
chiamate.

Impatto: la Fig. 1 della relazione, che è la prima figura sperimentale e introduce il concetto di
transizione di fase, riporta un fenomeno che è in parte un artefatto della scelta del seme e della
metrica aggregata, non solo della densità nominale. Il testo della relazione (§5.7, punto
multi-seme) descrive già questa tensione con onestà — ma la figura principale non viene corretta
di conseguenza.

### C2 — [ALTA] Rigore statistico non uniforme fra le campagne

Solo le campagne "veloci" (confronto per tipo a densità 0,2, densità fino a 0,35) sono state
ripetute su più semi, e con **N=5**, un campione che l'autore stesso definisce "modesto" nel testo.
Le tre campagne che generano le figure principali della relazione — scaling (`scaling_results.json`,
seed=42), densità (`density_results.json`, seed=100), potatura/ordinamento
(`pruning_comparison.json`, `ordering_comparison.json`, seed=2026) — restano a **istanza singola**.
Per un gruppo che punta alla lode, le conclusioni generali ("la potatura forte risolve in pochi
millisecondi", "l'ordinamento euristico è decisivo") sono estratte da una sola disposizione di
ostacoli per tipologia, senza stima di variabilità. C1 dimostra concretamente che questo non è un
rischio teorico: la variabilità fra istanze può essere più grande dell'effetto che si sta
misurando.

### C3 — [MEDIA] Le ottimizzazioni implementate non sono misurate in modo sistematico

`greedy_seed` (discesa golosa di innesco) e `use_component_check` (scarto immediato delle coppie
irraggiungibili) sono implementati, testati unitariamente (`tests/test_camminomin.py`) e verificati
da script usa-e-getta (`greedy_seed_results.json`, `component_check_results.json`), ma:
- `run_single_benchmark` in `src/experiment_runner.py` (righe 110–115) **non passa `greedy_seed`**
  ai benchmark: tutte le figure principali della campagna girano senza questa ottimizzazione;
- l'effetto isolato di `greedy_seed` risulta, sui soli 3 scenari testati, **marginale o nullo**
  quando combinato con la potatura forte (18×18: 2→1 chiamate; 40×40: 11303→11303 chiamate
  invariate; 100×100: 300998→299428, -0,5%) — un dato interessante che però nessun'analisi
  discute, e che si basa su una singola istanza per scenario, non su un campione;
- l'effetto di `use_component_check` è invece enorme e ben isolato (da 600 s/timeout e ~27,4
  milioni di chiamate a 0,006 s su una coppia irraggiungibile in un recinto), ma questo risultato
  vive solo in `component_check_results.json` e non è mai riportato né discusso in
  `CompitoQuattro.tex`, nonostante sia probabilmente il singolo numero più impressionante di tutta
  la campagna.

In sintesi: due accorgimenti implementati con effetti molto diversi (uno enorme, uno marginale) non
sono confluiti in una tabella di ablation comune né discussi in relazione — un'occasione persa per
materiale da lode già pronto nei dati.

### C4 — [MEDIA] Analisi spaziale sotto-sviluppata rispetto alla richiesta esplicita dello spec

La diapositiva 65 chiede esplicitamente prestazioni "spaziali e temporali"; il riassunto strutturato
della diapositiva 71 include la memoria. `peak_memory_kb` è raccolto in **ogni** singolo benchmark
(`run_single_benchmark`), ma nella relazione non esiste alcun grafico memoria-vs-taglia per
l'algoritmo principale: la sola analisi di memoria presente riguarda il confronto di strutture
dati (byte contro bit-plane, §5.7), che è un confronto statico di rappresentazione, non una verifica
sperimentale della crescita di memoria di `CAMMINOMIN` al crescere della griglia o della profondità
di ricorsione — l'analisi teorica di complessità spaziale (§5.1) resta quindi priva di un riscontro
empirico diretto, mentre il dato per farlo è già in `results/scaling_results.json` e
`results/density_results.json` sotto chiave `peak_memory_kb`.

### C5 — [BASSA] Ridondanza e disomogeneità del corredo sperimentale

- I due grafici a dispersione (tempo-vs-frontiera, $R^2=0,93$; tempo-vs-ricorsione, $R^2=0,84$)
  misurano essenzialmente lo stesso fenomeno: `frontier_cells` e `recursive_calls` crescono
  insieme per costruzione (ogni chiamata ricorsiva aggiunge la propria frontiera al totale). Il
  secondo grafico ha una correlazione inferiore, aggiunge un colore per la lunghezza del cammino,
  ma non un'informazione strutturalmente nuova.
- I tempi limite variano da campagna a campagna senza una politica dichiarata: 600 s per lo
  scaling, 20 s per densità/potatura/ordinamento, 15 s per multi-seme, 60 s per il labirinto e per
  la verifica di potatura a lato 100. Il significato di `timed_out` non è quindi comparabile fra
  figure diverse.
- Esistono script "toppa" fuori dal flusso principale (`scripts/aggiorna_scaling_30.py`,
  `scripts/verifica_potatura_100.py`) che ripetono singoli punti della campagna con parametri
  diversi: utili come approfondimento puntuale, ma non integrati nella pipeline riproducibile
  unica (`ExperimentRunner.run_campaign`).

### C6 — [BASSA] Densità nominale della tipologia `mix` non del tutto confrontabile

In `GridGenerator.generate_grid` (`src/generator.py`, righe 309–345), quando si combinano più
tipologie macro-strutturate (`cluster`, `diagonal`, `enclosure`, `bar`), ciascuna genera ostacoli
in aggiunta alle altre prima che venga eventualmente applicato `simple` per raggiungere la densità
target: la densità *effettiva* di `mix` può quindi superare il valore nominale 0,2 usato come
riferimento nel confronto con le tipologie singole. `CompitoQuattro.tex` §5.4 nota "coerentemente
con la maggiore densità effettiva di ostacoli generata dalla sovrapposizione" ma non riporta il
valore numerico effettivo, rendendo il confronto "a parità di densità" solo qualitativo.

---

## 6. Conclusione

La campagna soddisfa la lettera dello spec e contiene già gli elementi che distinguono un lavoro da
lode (oracolo indipendente, divario anytime, confronto di strutture dati, onestà nel documentare un
bug di correttezza risolto). Le criticità individuate non richiedono di ripartire da zero: sono
concentrate in (a) una figura headline da correggere con lo stesso rigore già applicato altrove
nella campagna, (b) un protocollo statistico da uniformare, (c) un paio di risultati già calcolati
ma non ancora integrati in relazione. Il piano di miglioramento allegato (`PianoMiglioramentoEsperimenti.md`)
affronta ciascun punto con interventi mirati, distinguendo cosa tenere, cosa tagliare e cosa
rieseguire, nel rispetto della scadenza del 9/07/2026.
