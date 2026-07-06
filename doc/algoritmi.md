# Piano — estensioni algoritmiche per puntare alla lode (rivisto)

## Contesto
Il progetto soddisfa già tutti i requisiti della traccia. Obiettivo: aggiungere passi
algoritmici importanti agganciati a ciò che la traccia premia esplicitamente: confronto di
implementazioni diverse, anche sulle strutture dati (pag. 63), valutazione critica degli
esiti (pag. 70), strutture dati che estendono le taglie elaborabili e sforzi documentati per
ridurre il tempo di calcolo (pag. 72). Punto debole documentato: muro esponenziale a lato
≥100 (campagna con tempo limite 600 s) e costo potenzialmente esponenziale delle
interrogazioni irraggiungibili.

Il piano originale prevedeva quattro estensioni; dopo la verifica contro il codice reale ne
sono state implementate **tre**. La quarta (innesco goloso del limite superiore globale) è
stata **scartata**: la frontiera è già ordinata per `dlib` crescente, quindi la prima discesa
della ricerca completa è già quasi-golosa e produce l'incombente iniziale in un numero di
espansioni proporzionale alla profondità; il guadagno atteso dall'innesco era ~0, a fronte di
una collisione terminologica ("goloso" è già usato per l'ordinamento di frontiera, traccia
pag. 65-66) e del precedente storico nel repository (un seeding goloso accoppiato a una cache
buggata era già stato rimosso per violazione della simmetria O-D / D-O).

## Estensione 1 — Componenti connesse: irraggiungibilità in O(R·C) — FATTA
Riempimento a inondazione BFS (`compute_components` in `src/grid.py`) che etichetta ogni
cella libera con il proprio componente connesso (vicinato a 8). Correttezza: per la traccia
(pag. 3) l'attraversamento diagonale fra celle libere è sempre ammesso, quindi la
connettività a 8 coincide esattamente con la raggiungibilità. `camminomin` (solo alla
radice, parametro `use_component_check=True`) ritorna subito `(inf, [], False)` se O e D
hanno etichette diverse; flag CLI `--no-component-check` per il confronto.

**Esperimento** (`scripts/verifica_componenti.py`, griglia 50×50 con recinto, coppia
irraggiungibile): 0.014 s con controllo vs 600 s di timeout con 13.8 milioni di chiamate
ricorsive senza. Nota: il controllo aiuta solo le coppie realmente disconnesse (recinti);
il caso 200×200 della campagna è raggiungibile e non ne beneficia.

## Estensione 2 — A* sul grafo delle celle: oracolo e divario anytime — FATTA
La `dlib` esistente è esattamente l'euristica octile, ammissibile e consistente per griglie
8-connesse con costi 1/√2. `src/astar.py` (heapq, euristica `dlib` riusata, stessa semantica
di attraversamento dei cammini liberi: nessuna restrizione di taglio d'angolo, pag. 3) è
l'implementazione di confronto sancita da pag. 63 e abilita:
- **oracolo di correttezza**: ogni lunghezza completata da CAMMINOMIN coincide con l'ottimo
  di A* (verificato su tutta la campagna di scaling: tutte CONFERMATE);
- **divario di ottimalità anytime** sulle esecuzioni interrotte: 3.5% (50, debole),
  4.3%/0.4% (100, debole/forte), 19.6%/9.1%/11.2% (150), a 200 debole e forte non trovano
  alcun cammino mentre il ritorno D-O dista 7.8% dall'ottimo.

`scripts/verifica_oracolo_astar.py` rigenera le griglie della campagna (seed 42), riusa
`results/scaling_results.json` senza rieseguire la campagna e produce
`results/divario_anytime.json` + `Relazione/images/divario_anytime.png`.
Test (`tests/test_astar.py`): equivalenza A*/CAMMINOMIN su 20 griglie casuali miste, inclusi
casi irraggiungibili e taglio d'angolo. Bibliografia: Hart, Nilsson, Raphael 1968.

## Estensione 3 — Griglia impacchettata a bit (confronto strutture dati) — FATTA
Gli stati logici sono 3 (libera, ostacolo fisso, ostacolo temporaneo): bastano 2 piani di
bit, cioè 2 bit/cella. `src/bitgrid.py` (`BitPackedGrid`) espone l'interfaccia duck-typed
usata dagli algoritmi (`.shape`, accesso/assegnazione con tupla, `.copy()`): chiusure,
`camminomin` e `compute_components` girano senza alcuna modifica.

**Esperimento** (`scripts/verifica_griglia_bit.py`): memoria ~4× inferiore (es. 40 000 B →
10 000 B a 200×200), rallentamento ~2× sul calcolo di chiusura e su CAMMINOMIN (accesso per
singola cella via operazioni sui bit in Python puro). Compromesso spazio/tempo onesto da
discutere in relazione (pag. 63 e 72).
Test (`tests/test_bitgrid.py`): equivalenza chiusure e risultati, occupazione 1/4.

## Bonifica documentazione — FATTA
- `doc/tempiRisultati.md`: sostituito (era il log di una versione rimossa, in contraddizione
  con `results/scaling_results.json`).
- `doc/walkthrough.md`: avvertenza di documento storico + nota sulla sezione v4 (cache e
  greedy seeding rimossi).

## Aggiornamenti alla relazione
- `Relazione/4-CompitoTre/CompitoTre.tex`: sottosezione sul controllo dei componenti
  connessi (motivazione, correttezza, numeri dell'esperimento).
- `Relazione/5-CompitoQuattro/CompitoQuattro.tex`: sottosezioni su oracolo A* + divario
  anytime (figura `divario_anytime.png`) e confronto strutture dati uint8 vs bit.
- `Relazione/6-Conclusioni/Conclusioni.tex`: limitazioni aggiornate (irraggiungibilità ora
  O(R·C); divario anytime quantificato).
- `Relazione/7-UsoDelCodice/UsoDelCodice.tex`: flag `--no-component-check`, nuovi script.
- `Relazione/main.tex`: bibitem per A* (Hart, Nilsson, Raphael 1968).
- Passata humanizer sui nuovi paragrafi (niente trattini lunghi, grassetto decorativo, calchi).

## Verifica
1. Suite completa: 24 test preesistenti invariati + 14 nuovi (38 totali), tutti verdi
   (`python -m unittest discover tests`).
2. `tests/test_astar.py` convalida l'intera pila esistente, non solo il nuovo codice.
3. Ogni script `scripts/verifica_*.py` gira standalone e produce numeri/figure riproducibili.
4. Nessuna regressione del comportamento predefinito: senza flag nuovi `camminomin` produce
   gli stessi risultati (il controllo componenti cambia solo il percorso irraggiungibile,
   con esito identico ∞; la griglia a bit è opzionale).
5. `latexmk -pdf main.tex`: compila senza errori.
