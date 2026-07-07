# Script di supporto alla campagna sperimentale

Guida rapida a cosa eseguire e in che ordine. Razionale completo di ogni intervento in
`PianoMiglioramentoEsperimenti.md` (radice del repository).

## Pipeline principale (già eseguita in precedenza)

```
python main.py experiment                        # ~2h, produce scaling/density/pruning/ordering
                                                   # + symmetry_per_type + figure 1-6
python scripts/campagna_multiseme.py              # multi-seme leggero (per tipo + densità, N=5)
python scripts/esperimento_mix.py                 # tipologia combinata "mix"
python scripts/esperimento_maze.py                # labirinto serpentino (caso peggiore topologico)
python scripts/rianalisi_metriche.py              # R^2 e rapporti debole/forte (costo zero)
python scripts/verifica_oracolo_astar.py          # oracolo A* sui risultati di scaling
python scripts/verifica_griglia_bit.py            # confronto strutture dati byte/bit-plane
```

## Nuovi script (Piano di miglioramento) — ordine consigliato per stasera

Eseguire 1-3 sulla stessa macchina (il PC fisso): sono pensati per essere confrontabili fra
loro (stesse tipologie, stessa taglia, stesso timeout) e mescolare hardware diverso
introdurrebbe una variabile in più oltre a quella di interesse. 4-6 sono a costo quasi nullo
(solo plotting o esecuzioni leggere) e vanno bene ovunque, ma conviene lanciarli di seguito
sulla stessa macchina per semplicità.

| # | Script | Tipo | Stima tempo | Dipendenze |
|---|---|---|---|---|
| 1 | `campagna_densita_multiseme.py` | Esecuzione — **priorità massima, chiude C1** | 10-25 min | nessuna |
| 2 | `campagna_potatura_ordinamento_multiseme.py` | Esecuzione | 15-35 min | nessuna |
| 3 | `ablation_ottimizzazioni.py` | Esecuzione leggera | 3-8 min | `results/component_check_results.json` già presente |
| 4 | `consolida_scatter.py` | Solo plotting, nessuna esecuzione | <1 min | `results/scaling_results.json`, `density_results.json`, `pruning_comparison.json`, `ordering_comparison.json` già presenti |
| 5 | `genera_grafico_memoria.py` | Solo plotting, nessuna esecuzione | <1 min | `results/scaling_results.json` già presente |
| 6 | `esperimento_mix.py` (rilancio) | Esecuzione leggera, aggiunge la densità effettiva a `mix_comparison.json` | 1-2 min | nessuna |

Comando unico per lanciare tutto in sequenza (dalla radice del repository):

```
python scripts/campagna_densita_multiseme.py && \
python scripts/campagna_potatura_ordinamento_multiseme.py && \
python scripts/ablation_ottimizzazioni.py && \
python scripts/consolida_scatter.py && \
python scripts/genera_grafico_memoria.py && \
python scripts/esperimento_mix.py
```

Se il tempo stringe, gli script 1 e 2 sono gli unici davvero necessari (chiudono C1/C2, le
criticità più gravi). 3-6 sono rapidi e possono essere lanciati anche a campagna 1-2 in corso
(non condividono file di output), ma per evitare di far girare due benchmark insieme sulla
stessa macchina conviene comunque rispettare l'ordine sopra.

## Politica dei tempi limite (timeout)

| Tipo di campagna | Timeout | Motivo |
|---|---|---|
| Scaling (curva di crescita, lato 10-150) | 600 s | Distingue un limite strutturale da un budget insufficiente |
| Densità / potatura / ordinamento multi-seme (script 1-2) | 20 s | Sufficiente a separare i regimi osservati senza esplodere il tempo totale |
| Ablation greedy_seed (script 3) | 20 s | Stesso protocollo delle campagne multi-seme |
| Labirinto serpentino (istanza singola) | 60 s | Coerente con la taglia contenuta (30x30) |
| Verifica component_check (istanza irraggiungibile) | 600 s | Già eseguita una volta, dato riusato da `ablation_ottimizzazioni.py`, non ripetuta |

`timed_out` ha lo stesso significato in ogni script: la ricerca è stata interrotta senza
garanzia di ottimalità, il miglior cammino trovato fino a quel momento viene comunque
restituito (requisito diapositiva 71).

## Script ad-hoc/storici (non fanno più parte della pipeline standard)

Questi script hanno prodotto risultati già citati in relazione o già assorbiti negli script
nuovi sopra. Restano nel repository come documentazione di come sono stati ottenuti i dati
esistenti, ma non vanno rilanciati come parte della campagna corrente:

- `aggiorna_scaling_30.py` — migrazione una tantum già applicata a `scaling_results.json`
  (aggiunta taglia 30, rimozione 200).
- `verifica_potatura_100.py` — approfondimento puntuale a taglia 100x100, citato in
  `CompitoQuattro.tex` §5.4.2 con i suoi numeri, non parte del flusso riproducibile principale.
- `verifica_componenti.py` — superato da `ablation_ottimizzazioni.py`, che riusa il suo
  risultato invece di ricalcolarlo.
- `verifica_innesco_goloso.py` — superato da `ablation_ottimizzazioni.py`, che misura lo stesso
  effetto su un campione di semi invece che su 3 istanze isolate.
