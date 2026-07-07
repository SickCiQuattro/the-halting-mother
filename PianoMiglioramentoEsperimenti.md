# Piano di miglioramento della campagna sperimentale — Compito 4

Segue da `ValutazioneEsperimenti.md`. Obiettivo: chiudere le criticità C1–C6 con una campagna
**pulita e precisa**, non una campagna più grande. Ogni intervento ha un costo dichiarato e un
criterio di accettazione; il piano è vincolato alla consegna del **9/07/2026**.

Principio guida: **selezionare, non accumulare**. Dove un test esiste già e basta correggerne il
protocollo, si corregge senza rieseguire tutto; dove un dato è già calcolato e solo mancante in
relazione, si integra a costo zero; solo dove la variabilità non è misurata (C1, C2) si rieseguono
campagne mirate.

---

## 1. Selezione dei test: keep / cut / redo

| Esperimento | Azione | File coinvolti | Motivo |
|---|---|---|---|
| Scaling log-log (lato 10→150) | **KEEP** invariato | `scaling_results.json` | È una curva di crescita al variare della taglia: seme singolo è corretto per questo tipo di analisi, non serve variabilità qui |
| Densità / transizione di fase | **REDO** come esperimento headline | `density_results.json` → sostituito | Risolve C1: unica correzione obbligatoria |
| Potatura riga 16 vs riga 17 | **REDO** con multi-seme | `pruning_comparison.json` → esteso | Requisito esplicito gruppo 3 (diapositiva 67); risolve C2 |
| Ordinamento euristico vs casuale | **REDO** con multi-seme, stesse coppie della potatura | `ordering_comparison.json` → esteso | Stesso protocollo di rigore di C2 |
| Simmetria O↔D (globale + per tipo) | **KEEP** | `simmetria_campagna.json`, `symmetry_per_type.json` | Già corretto, 0 fallimenti |
| Oracolo A* | **KEEP** | `divario_anytime.json`, `test_astar.py` | Già rigoroso, materiale da lode |
| Divario anytime | **KEEP** | `divario_anytime.json` | Idem |
| Campagna multi-seme (per tipo + densità) | **PROMUOVI**: diventa il metodo standard per densità/potatura/ordinamento, non un extra separato | `multiseme_results.json` → assorbito nei redo sopra | Coerenza metodologica |
| Labirinto serpentino | **KEEP**, ridotto a 1 sola taglia (già così) | `maze_results.json` | Caso peggiore topologico citato dallo spec, già efficiente |
| Mix (5 tipologie combinate) | **KEEP**, aggiungere densità effettiva misurata | `mix_comparison.json` | Risolve C6 a costo quasi nullo |
| Ablation `component_check` / `greedy_seed` | **NUOVO**, unificato in una tabella | nuovo file `results/ablation_ottimizzazioni.json` | Risolve C3 |
| Bit-plane vs byte | **KEEP** | `verifica_griglia_bit.py` | Già solido |
| Scatter tempo-vs-frontiera + tempo-vs-ricorsione | **CONSOLIDA** in un'unica figura a due pannelli, testo ridotto | `4_scatter_time_vs_frontier.png`, `5_scatter_time_vs_recursion.png` | Risolve C5 (ridondanza), a costo zero (dati già presenti) |
| Memoria vs taglia | **NUOVO** grafico, dati già raccolti | nuovo `results/10_memory_vs_size.png` | Risolve C4, costo minimo (nessuna nuova esecuzione) |
| `scripts/aggiorna_scaling_30.py`, `scripts/verifica_potatura_100.py` | **CUT**: risultati assorbiti come nota testuale, script rimossi dal flusso principale | — | Risolve C5 (riproducibilità) |
| Rianalisi metriche (R², rapporti debole/forte) | **KEEP** | `rianalisi_metriche.json` | Costo zero, già utile |

---

## 2. Interventi trasversali

### A — Protocollo statistico unico per densità, potatura, ordinamento
Regola unica: **N=8 semi indipendenti** per configurazione (taglia, tipologia, densità), potatura
forte, riportando sempre:
- mediana e IQR (Q1–Q3) del tempo e delle chiamate ricorsive,
- numero di semi in timeout su N,
- la coppia d'angolo **separata** dalle coppie casuali (mai mediate insieme come in
  `density_results.json` attuale — questo è esattamente l'errore che ha causato C1).

N=8 invece di N=5: piccolo aumento di costo, riduce il rischio che 1-2 semi anomali dominino la
mediana come già osservato nella campagna a N=5 esistente.

**Griglie/parametri:**
- Densità: taglia 50×50, tipologie `simple+cluster`, densità ∈ {0,05; 0,15; 0,25; 0,35}, coppia
  d'angolo su 8 semi + 3 coppie casuali su 1 seme di riferimento (per il solo confronto di forma
  della curva, non per la mediana headline).
- Potatura: 50×50, le 5 tipologie singole, 8 semi, coppia d'angolo, potatura debole vs forte.
- Ordinamento: stesse coppie/semi della potatura, potatura forte fissa, euristico vs casuale.

**Timeout:** 20 s per punto (invariato, sufficiente a separare i regimi osservati).

**Output atteso:** `results/density_results_multiseme.json`,
`results/pruning_comparison_multiseme.json`, `results/ordering_comparison_multiseme.json`,
sostituiscono le versioni a seme singolo come fonte delle figure 1 e 2.

**Stima costo:** la campagna a N=5 esistente su densità (5 punti × 5 semi) ha già mostrato tempi
fino a 15 s/campione in timeout; con N=8 e 4 densità la stima è ~15–25 minuti per la sola densità,
simile per potatura/ordinamento. Totale intervento A: **~45–60 minuti**.

### B — Timeout unificato e dichiarato
Politica esplicita, da riportare in una tabella nella relazione:

| Tipo di campagna | Timeout | Motivazione |
|---|---|---|
| Scaling (curva di crescita) | 600 s | Serve a distinguere limite strutturale da budget insufficiente (già giustificato in relazione) |
| Densità / potatura / ordinamento (multi-seme, N=8) | 20 s | Sufficiente a separare i regimi osservati senza esplodere il tempo totale di campagna |
| Labirinto (caso singolo, topologia difficile) | 60 s | Coerente con la taglia contenuta (30×30) |

Non serve un timeout identico ovunque: serve che **ogni figura dichiari il proprio** e che il
significato di "timed_out" sia sempre lo stesso (arresto senza garanzia di ottimalità, cammino
parziale comunque restituito). Costo: solo editoriale, nessuna nuova esecuzione.

### C — Analisi spaziale (chiude C4)
Nessuna nuova esecuzione: `peak_memory_kb` è già presente in `scaling_results.json` e nei nuovi
JSON multi-seme del punto A. Produrre un grafico memoria-vs-taglia (scala log-log o lineare a
seconda dell'andamento) per la configurazione a potatura forte dello scaling, con lettura critica:
verificare se la crescita osservata è compatibile con $O(\text{profondità} + \text{chiusura
corrente})$ come sostenuto in §5.1 della relazione, o se emergono deviazioni.

**Output atteso:** `results/10_memory_vs_size.png` + un paragrafo di lettura in relazione.
**Costo:** ~15 minuti (solo plotting, nessuna esecuzione dell'algoritmo).

### D — Tabella di ablation per le ottimizzazioni (chiude C3)
Unificare `greedy_seed` e `component_check` in un unico esperimento controllato, invece di due
script usa-e-getta con 3 istanze ciascuno:
- Set comune: 5 semi, taglia 50×50, tipologia `cluster` (dove `greedy_seed` ha mostrato l'effetto
  più misurabile nei dati esistenti) + 1 istanza con recinto chiuso per isolare `component_check`
  su una coppia irraggiungibile (riusa lo scenario già presente in
  `component_check_results.json`).
- Configurazioni in sequenza: baseline (potatura forte, no component check, no greedy seed) →
  + component check → + greedy seed → (già presente) + ordinamento euristico.
- Metriche: chiamate ricorsive e tempo, per isolare il contributo marginale di ciascun
  accorgimento.

**Output atteso:** `results/ablation_ottimizzazioni.json` + tabella in relazione. Se, come nei dati
preliminari già raccolti, `greedy_seed` risulta marginale in combinazione con la potatura forte,
questo va riportato come risultato onesto (non nascosto), con l'ipotesi che il suo beneficio
principale sia nell'inizializzare rapidamente il limite quando la potatura debole è attiva, non
quando la potatura forte già stima bene il residuo.

**Costo:** ~10 minuti di esecuzione (istanze piccole/medie), 15 minuti di scrittura tabella.

### E — Riproducibilità e pulizia del flusso
- Assorbire `scripts/aggiorna_scaling_30.py` e `scripts/verifica_potatura_100.py`: i loro risultati
  (già citati in relazione come approfondimenti puntuali) restano come nota testuale con il comando
  esatto usato per riprodurli, ma vengono rimossi dal set di script "ufficiali" mantenuti — non sono
  parte della pipeline `ExperimentRunner.run_campaign` e non devono sembrarlo.
- Documentare in relazione (o in un breve `README` di `scripts/`, se si preferisce non toccare la
  relazione) l'elenco esatto e l'ordine dei comandi che rigenerano tutti i JSON e le figure da zero
  con semi fissi.

**Costo:** ~10 minuti, solo editoriale.

### F — Consolidamento degli scatter ridondanti (chiude C5)
Nessuna nuova esecuzione. Sostituire le due figure separate tempo-vs-frontiera e
tempo-vs-ricorsione con un'unica figura a due pannelli affiancati, mantenendo entrambe le
regressioni (frontiera resta la più esplicativa, $R^2=0,93$ contro $0,84$) ma riducendo lo spazio
e il testo dedicato, e rendendo esplicito nel testo che le due metriche sono correlate per
costruzione.

**Costo:** ~15 minuti.

### G — Densità effettiva della tipologia `mix` (chiude C6)
Calcolare e riportare la densità effettiva (`np.sum(grid.state == 1) / (rows*cols)`, già loggata da
`GridGenerator.generate_grid` ma non salvata nei risultati) per la griglia usata in
`mix_comparison.json`, e aggiungerla come colonna nella tabella di conformità già presente in
relazione.

**Costo:** ~5 minuti (rilettura del log o rigenerazione della singola griglia con lo stesso seed).

---

## 3. Ordine di esecuzione consigliato

| Ordine | Intervento | Tipo | Stima tempo |
|---|---|---|---|
| 1 | C — grafico memoria (dati esistenti) | Costo zero | 15 min |
| 2 | F — consolidamento scatter (dati esistenti) | Costo zero | 15 min |
| 3 | G — densità effettiva mix | Costo quasi zero | 5 min |
| 4 | A — redo multi-seme densità (**priorità massima**, chiude C1) | Esecuzione | 20–25 min |
| 5 | A — redo multi-seme potatura + ordinamento | Esecuzione | 25–35 min |
| 6 | D — ablation ottimizzazioni | Esecuzione + scrittura | 25 min |
| 7 | E — pulizia script e nota di riproducibilità | Editoriale | 10 min |
| 8 | B — tabella timeout unificata | Editoriale | 10 min |
| 9 | Aggiornamento `CompitoQuattro.tex`: Fig. 1 sostituita, Fig. 4/5 consolidate, nuova Fig. 10 memoria, nuova tabella ablation, colonna densità effettiva | Scrittura relazione | 45–60 min |

**Totale stimato: ~3–3,5 ore**, compatibile con la scadenza del 9/07/2026. Gli step 1–3 e 7–8 non
richiedono nuove esecuzioni e possono essere fatti per primi per garantire progresso visibile anche
se il tempo per gli step 4–6 si riducesse.

---

## 4. Criteri di accettazione (mappatura criticità → intervento)

| Criticità | Intervento che la chiude | Come si verifica la chiusura |
|---|---|---|
| C1 — densità headline a seme singolo contraddetta | A (redo densità multi-seme) | La nuova Fig. 1 mostra IQR e conteggio timeout su 8 semi; il valore mediano a densità 0,15–0,25 è coerente con `multiseme_results.json` esistente (ordine di grandezza dei secondi, non dei millisecondi) |
| C2 — rigore statistico non uniforme | A (protocollo N=8 esteso a densità/potatura/ordinamento) | Ogni figura headline riporta mediana + IQR + n° timeout su ≥8 semi |
| C3 — ottimizzazioni non misurate sistematicamente | D (tabella di ablation) | Tabella unica con le 4 configurazioni progressive, discussione esplicita anche se l'effetto di `greedy_seed` risulta marginale |
| C4 — analisi spaziale sotto-sviluppata | C (grafico memoria-vs-taglia) | Figura presente, letta contro la previsione teorica di §5.1 |
| C5 — ridondanza/disomogeneità | F (consolidamento scatter) + B (timeout dichiarato) + E (script assorbiti) | Una figura invece di due per frontiera/ricorsione; tabella timeout in relazione; nessuno script "orfano" fuori dal flusso documentato |
| C6 — densità `mix` non dichiarata | G | Colonna densità effettiva nella tabella di conformità |

Ogni riga è verificabile leggendo il file JSON o la figura corrispondente: nessuna chiusura è
lasciata a un giudizio qualitativo non riscontrabile nei dati.
