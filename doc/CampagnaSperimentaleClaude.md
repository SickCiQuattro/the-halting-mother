# Campagna sperimentale — piano di completamento (Claude Opus)

Redatto a supporto della campagna sperimentale del Compito 4, in vista della consegna del
9/07/2026. Contiene la valutazione critica del piano prodotto da NotebookLM
(`doc/CampagnaSperimentaleNotebookLM.md`) e il piano d'azione additivo effettivamente eseguito
per completare la campagna già presente in `results/` e già discussa in
`Relazione/5-CompitoQuattro/CompitoQuattro.tex`.

## Premessa: stato della campagna esistente

La campagna già eseguita (`python main.py experiment`, ~2h) copre in modo corretto tutti i
requisiti obbligatori dello spec (`doc/AlgoritmiElaborato.md`): verifica di simmetria O↔D
(diapositiva 64), confronto potatura riga 16 vs riga 17 (diapositiva 67, richiesto per gruppi
di 3), confronto ordinamento euristico vs casuale della frontiera (diapositive 65–66), analisi
di scaling in scala bilogaritmica fino al lato 150. A questo si aggiungono contenuti che
eccedono lo standard: un oracolo di correttezza indipendente basato su A* (§5.5 della relazione),
il divario di ottimalità delle esecuzioni interrotte rispetto all'ottimo esatto (§5.6, anytime
gap), il confronto fra rappresentazione a byte e a piani di bit (§5.7). La correttezza
dell'implementazione è confermata da **due oracoli indipendenti**: la simmetria (100% di successi
sulle coppie verificabili) e A* (coincidenza esatta su tutte le esecuzioni completate).

Questo lavoro non viene rifatto: viene **integrato**.

## Valutazione del piano NotebookLM

### Punti di forza

- Struttura in fasi allineata allo spec: correttezza → confronto potatura → ordinamento →
  crescita asintotica in scala bilogaritmica → stress test topologico. È l'ossatura corretta di
  una campagna per questo algoritmo.
- Enfasi giusta su alcuni concetti chiave: la verifica di simmetria come condizione di
  correttezza, il confronto riga 16/riga 17 come richiesta esplicita per i gruppi di tre persone,
  la scala log-log per l'analisi di complessità empirica, l'idea che topologie diverse (barre,
  labirinti) producano caso peggiore diverso da un caso medio con ostacoli sparsi.
- Intuizione corretta sul fatto che l'ordinamento euristico della frontiera comporti un
  *trade-off* fra costo di ordinamento e rami di ricerca risparmiati.

### Punti di debolezza

1. **Fondato su affermazioni non verificate e in parte ritrattate.** Il piano cita più volte,
   come fonte, la descrizione del repository GitHub («scala fino a 200×200 senza timeout»,
   «Greedy Seeding v4»). Queste affermazioni provengono dal README, non da un'esecuzione
   verificata, e il file `doc/tempiRisultati.md` le smentisce esplicitamente: erano il prodotto
   di una versione precedente con un bug di correttezza nella cache dei sotto-problemi (violava
   la simmetria O–D/D–O), poi rimossa. I dati reali in `results/scaling_results.json` mostrano
   invece un muro esponenziale a partire dal lato 100, anche con un tempo limite di 600 secondi.
   Un piano sperimentale che assume come vere premesse già ritrattate rischia di far scrivere in
   relazione conclusioni non riproducibili.
2. **Il "tocco in più per la lode" suggerito è tecnicamente impreciso.** L'affermazione che la
   rappresentazione `numpy uint8` prevenga «picchi di RAM che distruggerebbero il Garbage
   Collector di Python» non è la storia corretta: per le taglie trattate la memoria non è mai il
   collo di bottiglia (poche decine di kilobyte anche a lato 200), lo è sempre il tempo. La storia
   davvero interessante sulle strutture dati, già presente in relazione (§5.7), è l'opposto: una
   rappresentazione a piani di bit dimezza ulteriormente la memoria ma raddoppia il tempo di
   accesso, e per le taglie qui trattate la matrice di byte resta la scelta corretta.
3. **Ampiamente ridondante rispetto al lavoro già svolto.** Ognuna delle cinque fasi proposte è
   già stata eseguita, spesso con un rigore superiore a quanto richiesto dal piano (doppia
   invocazione per ogni coppia, non solo per una prova isolata; aggregazione a mediana su più
   campioni, non un singolo run). Il piano inoltre non menziona i contenuti già presenti che sono
   più vicini allo spirito della "lode" — l'oracolo A*, il divario anytime, l'analisi di
   correlazione tempo/frontiera e tempo/ricorsione con pendenza di regressione.
4. **Nessun protocollo di rigore statistico.** Le fasi 2, 3 e 5 propongono di «fissare una
   griglia» e misurare su di essa, senza ripetizioni su semi diversi né misura di variabilità.
   Questo è accettabile come primo passo (ed è quanto già fatto nella campagna esistente) ma non
   basta a sostenere affermazioni generali sul comportamento dell'algoritmo, come invece
   suggerisce implicitamente il linguaggio del piano.
5. **Ignora alcuni requisiti letterali dello spec.** Non menziona la copertura esplicita di
   *tutte* le tipologie di ostacolo previste dal Compito 1 (incluse le combinazioni, `mix`), né il
   riassunto strutturato richiesto dalla diapositiva 71, né la necessità che la doppia invocazione
   O↔D sia effettuata per ciascuna coppia distinta usata nella campagna (non solo genericamente
   "su un campione").
6. **Metriche descritte in modo vago.** «Misurare il tempo di esecuzione» senza specificare
   ripetizioni, aggregazione (media o mediana), gestione degli outlier o separazione fra misura
   del tempo e misura della memoria — separazione che nella campagna esistente si è rivelata
   necessaria, perché la profilazione di memoria introduce un sovraccarico di circa 5 volte sul
   tempo cronometrato.

**Verdetto:** il piano NotebookLM è utile come lista di temi da coprire — e su questo è per lo
più corretto — ma inutilizzabile come piano operativo, perché si basa su premesse fattuali errate
e ignora sia il lavoro già svolto sia alcuni requisiti letterali dello spec. Non è stato seguito
nella forma proposta.

## Piano d'azione eseguito

Principio guida: **additività**. La campagna pesante esistente non è stata ri-eseguita. Ogni
blocco produce nuovi file in `results/` e nuove figure numerate a partire da 7, lasciando intatti
gli script e i dati esistenti. Il lavoro nuovo è stato vincolato a un budget di esecuzione
complessivo di 90 minuti, per la scadenza di consegna del 9/07/2026.

- **Blocco 0 — Re-analisi a costo nullo.** Nessuna nuova esecuzione: dai JSON già presenti in
  `results/` sono stati calcolati l'R² delle due regressioni bilogaritmiche (tempo/celle di
  frontiera, tempo/invocazioni ricorsive), oggi riportate in relazione solo come pendenza, e il
  rapporto fra invocazioni ricorsive della potatura debole e della potatura forte in funzione del
  lato della griglia, per quantificare numericamente quanto la potatura forte sfoltisca l'albero
  di ricerca.
- **Blocco A — Ottimizzazioni documentate.** L'innesco goloso (`greedy_seed`) e il controllo dei
  componenti connessi (`use_component_check`) erano implementati e verificati solo da script
  usa-e-getta (`scripts/verifica_innesco_goloso.py`, `scripts/verifica_componenti.py`) che non
  salvavano risultati né producevano figure. Sono stati promossi a esperimenti documentati, con
  output in `results/greedy_seed_results.json` e `results/component_check_results.json` e una
  figura a confronto.
- **Blocco B — Copertura della tipologia `mix`.** Le cinque tipologie singole erano già coperte
  dalle campagne di potatura, ordinamento e simmetria per tipo. Mancava la tipologia combinata
  `mix` (più tipologie di ostacolo sulla stessa griglia) e una tabella esplicita che mappasse
  ciascuna tipologia del Compito 1 alla campagna che la copre, a dimostrazione diretta del
  requisito.
- **Blocco C — Multi-seme sulle campagne veloci.** Le configurazioni a basso costo temporale
  (confronto per tipo a 50×50 con potatura forte, densità fino alla soglia della transizione di
  fase) sono state ripetute su più semi, aggregando mediana e scarto interquartile, per sostenere
  con maggiore rigore statistico affermazioni altrimenti basate su una singola griglia. La
  campagna di scaling pesante, che descrive una curva di crescita e non una stima di variabilità,
  resta a seme singolo.
- **Blocco D — Worst-case a labirinto (facoltativo).** Un generatore di labirinto serpentino
  connesso, come caso peggiore topologico esplicitamente citato dallo spec, incluso solo se il
  tempo residuo nel budget di 90 minuti lo consentiva senza rischiare la scadenza di consegna.

Per il dettaglio completo di ciascun blocco (script, parametri, file prodotti, integrazioni
puntuali nella relazione) si veda il piano di implementazione tracciato durante la sessione di
lavoro; i risultati effettivi sono nei file JSON e PNG corrispondenti in `results/`.
