# Giustificazione delle scelte implementative

Elaborato di Algoritmi e Strutture Dati, a.a. 2024/25, Prof.ssa Marina Zanella.

Questo documento motiva ogni scelta implementativa del progetto, distinguendo tra
requisiti esplicitamente richiesti dalla traccia (`doc/AlgoritmiElaborato.md`) e
ottimizzazioni aggiunte di iniziativa. Per ciascuna scelta si indica il riferimento
alla diapositiva della traccia (quando pertinente) e il file sorgente coinvolto.

## Compito 1 — Generatore di griglie (`src/generator.py`)

La traccia (pag. 9) richiede un generatore capace di produrre ostacoli con
disposizione casuale e, per gruppi di tre persone, almeno quattro tipologie
distinte (semplici, agglomerati, diagonali, delimitatori di aree chiuse, a barre).
`GridGenerator` ne implementa cinque: `simple`, `cluster`, `diagonal`, `enclosure`,
`bar`, combinabili nella stessa griglia tramite il parametro `types` di
`generate_grid`, come richiesto dalla traccia ("una griglia può contenere una o
più tipologie di ostacoli contemporaneamente").

- **`generate_cluster`**: gli agglomerati sono costruiti con un cammino casuale a
  partire da un seme (`seme`), aggiungendo ai vicini liberi finché non si
  raggiunge la dimensione target. Questo produce forme organiche e connesse,
  coerenti con l'esempio di pag. 4 ("agglomerati di 2, 3 o 4 celle"), invece di
  un blocco rettangolare fisso che sarebbe meno vario.
- **`generate_diagonal`**: genera esplicitamente coppie o triple allineate solo
  sulla diagonale, per garantire che nella sperimentazione compaiano casi di
  attraversamento dello spigolo (pag. 3: "se due celle ostacolo si toccano solo
  su uno spigolo... è possibile attraversare tale spigolo"), un caso limite che
  un generatore puramente casuale difficilmente produrrebbe con frequenza
  sufficiente.
- **`generate_enclosure`**: costruisce recinti rettangolari con bordo di ostacoli
  e interno libero, per riprodurre il caso di pag. 7 (aree chiuse irraggiungibili
  dall'esterno) e verificare che l'algoritmo riconosca correttamente distanza
  infinita fra celle interne ed esterne al recinto.
- **`generate_bar`**: crea barriere continue con un varco obbligatorio, secondo
  lo schema di pag. 8. Il varco garantisce che la griglia resti sempre transitabile
  almeno in parte, evitando di generare per costruzione istanze totalmente
  disconnesse quando non richiesto.
- **Parametro `density` e `seed`**: la traccia richiede che l'utente possa
  configurare dimensioni e "altri parametri ritenuti significativi" (pag. 9).
  `density` controlla la frazione di celle occupate, `seed` garantisce la
  riproducibilità delle prove sperimentali (fondamentale per confrontare
  configurazioni diverse sulla stessa istanza, vedi Compito 4). Ogni sottotipo
  riceve un seme derivato ma distinto (`rng.randint` per ogni chiamata locale) in
  modo che comporre più tipologie non produca correlazioni indesiderate tra le
  loro disposizioni.
- **Generazione in due fasi (macro poi `simple`)**: gli ostacoli strutturati
  (cluster, diagonali, recinti, barre) vengono generati prima; la densità residua
  rispetto al target viene poi colmata con ostacoli sparsi. Questo permette di
  rispettare la densità complessiva richiesta anche quando l'utente combina più
  tipologie, senza dover risolvere un sistema di equazioni sulle proporzioni.

## Compito 2 — Distanza libera, contesto e complemento (`src/free_paths.py`)

### `dlib`

Implementa direttamente la formula di pag. 17:
`dlib(O,D) = sqrt(2) * Δmin + (Δmax - Δmin)`. Nessuna scelta implementativa
oltre alla traduzione diretta della formula.

### `free_path_type1` / `free_path_type2`

Seguono la definizione di cammino libero di pag. 12: una sequenza di mosse
oblique in un solo verso seguita da una sequenza di mosse cardinali in un solo
verso (tipo 1), o l'ordine inverso (tipo 2). Entrambe le funzioni verificano
cella per cella l'attraversabilità (stato pari a 0) e restituiscono l'intero
percorso fisico, usato poi dalla ricostruzione del cammino nel Compito 3.

### Contesto e complemento: proiezione di raggi (`compute_context_rays`, `compute_complement_rays`)

Il calcolo diretto di contesto e complemento, come suggerito implicitamente
dallo pseudocodice (CALCOLACONTESTO/CALCOLACOMPLEMENTO), consisterebbe nel
verificare l'esistenza di un cammino libero fra l'origine e ciascuna cella della
griglia: un test per cella, quindi O(R·C) chiamate a `free_path_type1`/`2`, ciascuna
di costo O(R+C) nel caso peggiore, per un totale O(R·C·(R+C)), che sulle griglie
richieste dal Compito 4 (fino a 200×200, pag. 72) diventa proibitivo.

L'implementazione traccia invece raggi cardinali e diagonali a partire
dall'origine e, da ogni cella diagonale raggiunta, espande cardinalmente finché
non incontra un ostacolo. Poiché ogni raggio si allunga di una cella alla volta
fino al bordo della griglia, il costo complessivo si riduce a O(max(R,C)²): è
esattamente l'insieme di celle che il test diretto avrebbe dovuto verificare una
per una, ma visitato in un solo attraversamento invece che ricalcolato da zero
per ogni destinazione. Questa è la principale ottimizzazione richiesta
esplicitamente dalla traccia in termini generali ("particolare attenzione deve
essere dedicata alla scelta di strutture dati... nonché di altri accorgimenti"
volti a estendere le dimensioni delle griglie elaborabili, pag. 72).

Il complemento esclude per costruzione le celle già presenti nel contesto
(controllo `cell not in context`), coerentemente con la definizione di pag. 20
("celle raggiungibili da O solo attraverso un cammino libero di tipo 2").

### `compute_frontier`

Determina la frontiera controllando, per ogni cella della chiusura, la presenza
di almeno un vicino libero esterno alla chiusura stessa, secondo la definizione
di pag. 25. Il tipo (1 o 2) è assegnato in base all'appartenenza a contesto o
complemento, come richiesto a pag. 33 ("l'assegnamento del tipo avverrà a opera
di CALCOLAFRONTIERA").

## Compito 3 — Algoritmo CAMMINOMIN (`src/camminomin.py`)

### Fedeltà allo pseudocodice

La funzione `camminomin` segue la struttura delle righe 3-23 dello pseudocodice
di pag. 30: calcolo del contesto (riga 3), caso base di tipo 1 (righe 4-5),
calcolo del complemento (riga 6), caso base di tipo 2 (righe 7-8), calcolo della
frontiera e gestione del vicolo cieco (righe 9-11), ciclo sulla frontiera con
condizione di potatura, chiamata ricorsiva e compattazione della sequenza
(righe 12-22). La traccia consente esplicitamente di non seguire fedelmente lo
pseudocodice purché si producano gli stessi effetti operativi (pag. 34); qui la
fedeltà è mantenuta perché non introduce complessità aggiuntiva e rende più
diretto il confronto con la specifica durante la revisione.

### Potatura di riga 16 e riga 17

Entrambe le condizioni della traccia sono implementate e selezionabili da riga
di comando (`--strong-pruning`): la potatura debole confronta la sola distanza
già percorsa (`lf`), quella forte vi somma la stima ammissibile `dlib(F, D)`
della distanza residua (pag. 37, commento di riga 17). La disponibilità di
entrambe è richiesta dal confronto sperimentale opzionale del Compito 4
(pag. 67, "confrontare l'efficacia delle due condizioni alternative").

### Estensione a limite superiore globale (branch-and-bound)

Lo pseudocodice valuta la condizione di riga 16/17 contro `lunghezzaMin`,
variabile locale alla singola invocazione. L'implementazione la sostituisce con
un limite superiore condiviso fra tutte le invocazioni ricorsive
(`shared_state['global_min_length']`), aggiornato ogni volta che si trova un
cammino completo più breve. Un candidato di frontiera viene esplorato solo se
la somma fra la lunghezza già accumulata dall'origine principale, il costo
parziale e (nella variante forte) la stima residua non supera tale limite.

Questa non è una richiesta esplicita della traccia, ma una potatura
aggiuntiva legittima: poiché `dlib` non sovrastima mai la distanza reale, la
stima resta ammissibile e nessun cammino ottimo viene mai scartato. È motivata
dal punto della traccia che invita a ridurre il costo temporale della
computazione, documentando lo sforzo (pag. 72). Non richiede alcuna passata
preliminare: finché non si è trovato il primo cammino completo il limite vale
infinito e non si pota nulla; il limite emerge dalla ricerca stessa.

### Ritracciamento sul posto con marcatura costante

Anziché clonare la matrice della griglia a ogni invocazione ricorsiva (che
esaurirebbe rapidamente la memoria sulle griglie 150×150 e 200×200 richieste
dal Compito 4), le celle della chiusura corrente vengono marcate con un valore
costante (`TEMP_MARK = 2`) direttamente sulla matrice condivisa, e ripristinate
a 0 durante la risalita. Questo risponde al punto della traccia sulla
"scelta di strutture dati volte a estendere le dimensioni delle griglie che
possono essere elaborate" (pag. 72), e affronta direttamente la critica che la
traccia stessa muove all'approccio a oggetti ("associa a ogni cella un'istanza
dedicata e grava sul gestore della memoria", pag. 9-11 dell'introduzione della
relazione).

La marcatura è costante e non dipendente dalla profondità di ricorsione: le
chiusure annidate sono per costruzione disgiunte (ciascuna esclude le chiusure
dei livelli precedenti, come richiesto a pag. 28) e il ripristino avviene per
insieme esplicito di celle, non per confronto di valore. Una marcatura
dipendente dalla profondità (`profondità + 2`) era stata usata in una prima
versione ma è stata scartata: con tipo `uint8` (0-255) supera il limite massimo
già a profondità 254, causando un overflow su catene di landmark lunghe. La
marcatura costante rimuove sia il problema di correttezza sia il limite
artificiale sulla profondità.

### Assenza di memoizzazione

Un tentativo di introdurre la memoizzazione dei sotto-problemi (con chiave
data da origine, destinazione e insieme delle celle temporaneamente escluse)
è stato scartato per un difetto logico: il risultato di ogni sotto-problema
dipende, tramite la potatura globale, dalla lunghezza già accumulata nelle
chiamate esterne, che non fa parte della chiave. Un risultato calcolato con una
lunghezza accumulata elevata (e quindi con rami ottimali già potati) sarebbe
stato riusato in una chiamata con lunghezza accumulata minore, producendo una
risposta subottimale. Questo avrebbe violato la verifica di simmetria richiesta
dalla traccia (pag. 64): `camminomin(O,D)` e `camminomin(D,O)` devono avere la
stessa lunghezza. Le prestazioni restano affidate alla potatura branch-and-bound
e all'ordinamento euristico della frontiera.

### Ordinamento euristico della frontiera

Prima di scorrere il ciclo sulla frontiera, le celle vengono ordinate per
distanza libera crescente dalla destinazione (a meno che l'utente non richieda
`--randomize-frontier`). Questa è esattamente l'osservazione di pag. 66 della
traccia ("criterio euristico goloso di ordinare le celle di frontiera per
valori non decrescenti della distanza libera dalla cella destinazione"),
esplicitamente indicata come osservazione facoltativa, non come richiesta. È
stata implementata perché, esplorando per prime le celle più vicine alla
destinazione, il limite superiore globale si abbassa prima, rendendo la
potatura branch-and-bound efficace già nelle prime iterazioni. Il flag
`--randomize-frontier` permette il confronto sperimentale fra le due strategie,
richiesto opzionalmente dal Compito 4 per i gruppi di tre persone.

### Ricostruzione del cammino fisico (`reconstruct_path`)

Requisito per i soli gruppi di tre persone (pag. 38). A partire dalla sequenza
di landmark, ogni tratto consecutivo viene tradotto in celle fisiche tramite
`free_path_type1`/`free_path_type2` (in base al tipo memorizzato nel landmark
di arrivo) e i segmenti vengono concatenati evitando la duplicazione della
cella di giunzione.

### Interruzione per tempo limite

Requisito per i soli gruppi di tre persone (pag. 71). Il tempo trascorso viene
controllato all'ingresso di ogni chiamata ricorsiva; al superamento del limite
la ricerca si arresta restituendo il miglior cammino trovato fino a quel
momento, la sua lunghezza e un indicatore `timed_out`. Il controllo avviene
all'inizio della funzione (non durante il calcolo di contesto/complemento/
frontiera all'interno di una singola chiamata) per mantenere l'overhead di
verifica trascurabile; il costo in termini di reattività è al più il tempo di
una singola espansione di chiusura, accettabile rispetto ai tempi di
esecuzione osservati nella sperimentazione.

## Struttura dati fisica della griglia (`src/grid.py`)

La griglia è rappresentata da un array NumPy bidimensionale di tipo `uint8`
(1 byte per cella): 0 libera, 1 ostacolo fisso, 2 ostacolo temporaneo. La
scelta di un array di interi contigui in memoria, invece di una matrice di
oggetti Python, riduce l'occupazione di un fattore proporzionale al
sovraccarico per istanza di un oggetto Python (dell'ordine di alcune decine di
byte a cella anche per un oggetto minimale), risultando decisiva per le griglie
di grandi dimensioni richieste dal Compito 4.

## Compito 4 — Sperimentazione (`src/experiment.py`)

### Verifica di simmetria

Richiesta esplicita e non opzionale (pag. 64): ogni coppia di celle deve essere
testata invocando l'algoritmo in entrambi gli ordini, confrontando le due
lunghezze minime. `verify_symmetry` e `run_benchmark_coppia` eseguono sempre la
doppia invocazione O→D e D→O, sia nel comando dedicato
(`experiment --verify-symmetry-count`) sia all'interno di ogni campagna della
sperimentazione completa. Le coppie in cui almeno una direzione va in tempo
limite sono escluse dal conteggio dei fallimenti (non essendo comparabili) ma
tracciate separatamente, per non falsare la percentuale di successo con un
esito che non è un errore logico.

### Misura separata di tempo e memoria

`tracemalloc`, se attivo durante la misura del tempo, introduce un sovraccarico
di circa cinque volte sull'esecuzione, alterando sensibilmente i tempi
rilevati. La misura temporale viene quindi eseguita su un'esecuzione pulita, e
solo in una seconda passata, separata, si attiva `tracemalloc` per misurare il
picco di memoria. Questo rispetta il requisito di documentare le prestazioni
sia spaziali sia temporali (pag. 65) senza che l'una comprometta la precisione
dell'altra.

### Aggregazione per mediana

Ogni configurazione viene misurata su più coppie casuali di celle (oltre al
caso d'angolo O=(0,0), D=(righe-1,colonne-1), il più oneroso); le metriche
vengono aggregate con la mediana anziché con la media, per ridurre l'influenza
di singole coppie anomale (ad esempio celle isolate con chiusura minima) sulla
tendenza generale, che è l'obiettivo della sperimentazione (pag. 65: "registrare
e valutare criticamente le prestazioni spaziali e temporali").

### Riassunto strutturato (`--summary`, Slide 71)

Il comando `camminomin --summary` produce un riassunto JSON con tutti i campi
richiesti dal requisito funzionale di pag. 71: dimensioni e tipo della griglia,
numero totale di celle di frontiera individuate, numero di volte in cui la
condizione di potatura è risultata falsa, prestazioni (tempo trascorso,
profondità massima, numero di invocazioni ricorsive) e stato del calcolo,
incluso il caso di interruzione per tempo limite con relativa indicazione
esplicita, come richiesto dal secondo requisito funzionale (pag. 71).

### Grafici prodotti

La campagna genera sei grafici per coprire le dimensioni richieste dalla
sperimentazione (correttezza, prestazioni, confronto tra scelte
implementative):

1. Tempo in funzione della densità di ostacoli, per osservare l'eventuale
   transizione di fase nella difficoltà di ricerca.
2. Confronto a barre fra potatura debole, potatura forte, ordinamento
   euristico e ordinamento casuale, sugli stessi cinque scenari di ostacolo
   del Compito 1 (risponde ai due confronti opzionali di pag. 66-67 per i
   gruppi di tre persone).
3. Crescita del tempo in scala bilogaritmica al crescere della dimensione
   della griglia, fino a 200×200 (pag. 72), per stimare l'andamento asintotico
   effettivo.
4. Dispersione tempo/celle di frontiera esplorate, con regressione lineare in
   scala logaritmica per stimare la pendenza empirica.
5. Dispersione tempo/numero di invocazioni ricorsive, con la stessa
   regressione, per correlare il costo osservato al numero di sotto-problemi
   effettivamente esplorati.
6. Esito della verifica di simmetria per ciascuna tipologia di ostacolo
   (verificata, esclusa per tempo limite, fallita).

I campioni che vanno in tempo limite sono esclusi dagli scatter plot di
regressione (punti 4 e 5), perché rappresenterebbero un tempo troncato e non
il tempo reale di completamento, distorcendo la pendenza stimata.

## Visualizzazione (`src/visualization.py`)

I requisiti non funzionali escludono la necessità di una interfaccia grafica e
richiedono elaborazione batch con I/O solo da/per file (pag. 73). Le immagini
PNG prodotte da `save_grid_image` rispettano questo vincolo: sono file di
output, non un'interfaccia interattiva. La rappresentazione ibrida (evidenzia
in azzurro il cammino fisico completo e sovrappone la spezzata dei soli
landmark con etichette numeriche) rende leggibile a colpo d'occhio sia il
percorso realmente attraversato sia la sequenza sintetica su cui si basa
l'algoritmo, corrispondente all'esempio di pag. 53 della traccia.

## Gestione degli errori (`src/exceptions.py`)

Le eccezioni applicative (`InvalidCoordinateError`, `PathReconstructionError`)
derivano da una base comune `PathfindingError` e sono sollevate solo ai confini
del sistema: coordinate fornite dall'utente da riga di comando, file griglia
non trovati, segmenti di cammino non ricostruibili. Il codice interno (celle
generate dall'algoritmo, coordinate calcolate dalla chiusura) non viene
validato di nuovo, perché la sua correttezza è garantita per costruzione dalle
funzioni che lo producono.

## Limiti noti

- Il limite di ricorsione di Python è stato innalzato a 15000
  (`sys.setrecursionlimit`) per non troncare la ricerca su griglie di grandi
  dimensioni, dato che ogni landmark della sequenza corrisponde a un livello di
  ricorsione. Resta comunque un limite fisico allo stack di chiamate, non
  eliminabile senza riscrivere l'algoritmo in forma iterativa.
- Il controllo del tempo limite avviene solo all'ingresso di ogni chiamata
  ricorsiva: durante il calcolo di una singola chiusura molto estesa (proiezione
  di raggi su una griglia enorme) l'interruzione può quindi ritardare fino al
  completamento di quel calcolo.
- La misura di memoria con `tracemalloc` cattura l'occupazione degli oggetti
  Python tracciati dall'interprete, non l'occupazione nativa dell'array NumPy
  sottostante (dimensionata a parte in byte in `memoria_rappresentazione_byte`
  del riassunto strutturato); le due misure sono complementari, non
  sovrapponibili.
