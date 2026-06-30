# Algoritmi e Strutture Dati

Elaborato a.a. 2024-25

Prof.ssa Marina Zanella

### DOMINIO

<page_number>2</page_number>

# Griglia (8-connected gridmap)

* È uno spazio bidimensionale suddiviso in celle
* Due celle sono adiacenti se sono limitrofe secondo una delle 8 frecce in figura

![Diagramma di una griglia con 8 frecce rosse che partono da una cella centrale verso le celle adiacenti (cardinali e diagonali)](page_3_image_1_v2.jpg)

* Una cella può essere attraversabile oppure non attraversabile
* Ogni mossa cardinale (N,S,E,W) fra due celle attraversabili adiacenti ha distanza 1
* Ogni mossa diagonale (NE,NW,SE,SW) fra due celle attraversabili adiacenti ha distanza $\sqrt{2}$
* Una o più celle non attraversabili adiacenti formano un ostacolo
* Se due celle ostacolo si toccano solo su uno spigolo (cioè su un angolo) di ciascuna, è possibile attraversare tale spigolo (con le mosse diagonali)

3

# Griglia finita
# dotata di ostacoli

![Griglia con vari ostacoli formati da celle blu](page_4_image_1_v2.jpg)

La griglia in figura contiene un <mark>ostacolo semplice</mark>, costituito da una singola cella non attraversabile (in blu), e cinque ostacoli che sono <mark>agglomerati</mark> di 2, 3 o 4 celle non attraversabili. Un ulteriore ostacolo (quello più a destra), detto <mark>ostacolo diagonale</mark>, non è propriamente un agglomerato perché le celle non attraversabili si toccano solo sugli spigoli<sub>4</sub>

## Celle reciprocamente raggiungibili

- Cammino = sequenza finita di mosse che portano da una cella (attraversabile) origine O a una cella (attraversabile) destinazione D, visitando solo celle attraversabili; possono esistere zero, uno o più cammini da O a D
- Se esiste almeno un cammino da O a D si dice che O e D sono reciprocamente raggiungibili (cioè, a partire da una si può raggiungere l’altra e viceversa)
- Se non esiste alcun cammino da O a D si dice che la distanza da O e D (e viceversa) è infinita

<page_number>5</page_number>

# Ostacoli che partizionano lo spazio

![Griglia con ostacoli (celle blu) che dividono lo spazio in due parti separate](page_6_image_1_v2.jpg)

Lo spazio della griglia può essere suddiviso in due o più parti tali che le celle (attraversabili) appartenenti a una parte sono irraggiungibili dalle celle (attraversabili) delle altre parti

6

# Ostacoli che delimitano aree chiuse

![Griglia con ostacoli blu che formano un'area chiusa](page_7_image_1_v2.jpg)

La delimitazione di aree chiuse entro lo spazio rende le celle (attraversabili) che si trovano all’interno di un’area irraggiungibili dalle celle che si trovano all’esterno della stessa

7

# Ostacoli disposti secondo barre
# (orizzontali e/o verticali)


<table>
  <tbody>
    <tr>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td></td>
    </tr>
    <tr>
        <td> </td>
        <td rowspan="8">Obstacle</td>
        <td> </td>
        <td rowspan="8">Obstacle</td>
        <td> </td>
        <td colspan="2" rowspan="7">Obstacle</td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td colspan="8">Obstacle</td>
        <td></td>
    </tr>
    <tr>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td colspan="4"></td>
    </tr>
    <tr>
        <td> </td>
        <td> </td>
        <td> </td>
        <td colspan="10" rowspan="4">Obstacle</td>
        <td colspan="4"></td>
    </tr>
    <tr>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td colspan="3"></td>
    </tr>
    <tr>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td colspan="3"></td>
    </tr>
    <tr>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td colspan="3"></td>
    </tr>
    <tr>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td colspan="3"></td>
    </tr>
    <tr>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td colspan="10">Obstacle</td>
        <td> </td>
        <td> </td>
        <td colspan="3"></td>
    </tr>
    <tr>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td> </td>
        <td></td>
    </tr>
  </tbody>
</table>


Le barre possono avere diverso spessore e diversa lunghezza. Si noti che tali barre potrebbero essere disposte in modo da formare un «labirinto»

8

# Compito 1

* Dopo averne scritto lo pseudocodice, realizzare un generatore che sia in grado di produrre griglie finite contenenti
    - celle non attraversabili aventi disposizione totalmente casuale (questo generatore è quello da produrre nel caso il gruppo di lavoro sia eccezionalmente <u>composto da meno di tre persone</u>)
    - celle non attraversabili disposte secondo almeno quattro tipologie di ostacoli (semplici, agglomerati, diagonali, delimitatori di aree chiuse, a barre ed altre eventuali conformazioni ideate dal gruppo di lavoro); una griglia può contenere una o più tipologie di ostacoli contemporaneamente
* All’utente deve essere consentito di configurare le dimensioni della griglia desiderata e altri parametri, ritenuti significativi (anche ai fini della sperimentazione di cui si parlerà più avanti), che guidino il generatore (semi-)casuale

9

# CAMMINI LIBERI

10

# Quadranti

II quadrante

I quadrante

III quadrante

IV quadrante

![Cartesian plane quadrants diagram with origin O and highlighted axes](page_11_image_1_v2.jpg)

Ciascuna cella O può essere vista come l’origine di un piano cartesiano; le celle in giallo appartengono agli assi di tale piano

11

## Cammino libero

- È un cammino che contiene (a) una sequenza (anche nulla) di mosse oblique in un solo verso (NE nel quadrante I, NW nel quadrante II, SW nel quadrante III, SE nel quadrante IV) seguita da (b) una sequenza (anche nulla) di mosse orizzontali in un solo verso (E nei quadranti I e IV, W nei quadranti II e III) oppure verticali in un solo verso (N nei quadranti I e II, S nei quadranti III e IV), o viceversa
- Esistono al più due cammini liberi fra una cella origine O e una cella destinazione D (reciprocamente raggiungibili), uno di <u>tipo 1</u> (cioè che rispetta l’ordine (a)(b)), l’altro di <u>tipo 2</u> (cioè che rispetta l’ordine inverso (b)(a))
- Un cammino contenente solo celle orizzontali o solo celle verticali viene classificato di tipo 1, così come un cammino contenente solo celle oblique (in un unico verso)
- Fra due celle che sono allineate orizzontalmente o verticalmente od obliquamente esiste al più un cammino libero

<page_number>12</page_number>

# Cammini liberi

![Griglia con ostacoli e due percorsi (azzurro e marrone) che collegano i punti O e D.](page_13_image_1_v2.jpg)

La figura mostra i due cammini liberi relativi alla coppia ordinata (O,D): quello azzurro è di tipo 1, quello marrone è di tipo 2.

13

## Cammini minimi

- Lunghezza di un cammino (da una cella O a una cella D) = somma delle distanze delle mosse del cammino
- L’unico cammino da una cella O a se stessa è nullo, cioè privo di mosse (e quindi ha lunghezza nulla)
- Cammino minimo (da una cella O a una cella D) = è un cammino che porta da O a D di lunghezza minima; possono esistere più cammini minimi da O a D
- Ogni cammino libero è un cammino minimo (ma non viceversa)

<page_number>14</page_number>

# Cammini liberi e cammini minimi

![Diagram showing a grid with obstacles (dark blue squares) and three paths (brown, yellow, and blue) between points O and D. The yellow path passes through an obstacle.](page_15_image_1_v2.jpg)

Il camino giallo è un cammino minimo relativo alla coppia (O,D) ma non è un cammino libero.

15

# Distanza libera (dlib)

```mermaid
graph LR
    subgraph Grid
        O((O)) -- "√2Δy" --> M
        M -- "Δx - Δy" --> D((D))
    end
    style O stroke:#f00,stroke-width:2px
    style D stroke:#f00,stroke-width:2px
    style M width:0px,height:0px
```

<mark>Distanza libera</mark> fra una cella origine O e una destinazione D = lunghezza di un cammino libero fra O e D (se esiste), sia esso di tipo 1 o 2; nell’esempio in figura
dlib(O,D) = $\sqrt{2}\Delta y + \Delta x - \Delta y = 3\sqrt{2} + 8$

16

# Distanza libera

* Siano $\Delta x$ e $\Delta y$ le differenze (in valore assoluto ed eventualmente nulle) fra le coordinate di O e D
* Siano $\Delta_{min} = \min\{\Delta x, \Delta y\}$ e $\Delta_{max} = \max\{\Delta x, \Delta y\}$
* Per qualsiasi coppia (O,D),
$$dlib(O,D) = \sqrt{2}\Delta_{min} + \Delta_{max} - \Delta_{min}$$

17

# Contesto di O = insieme delle celle raggiungibili da O con cammini liberi di tipo 1

![Grid showing reachable cells from point O using type 1 free paths. The grid contains various colored cells (blue, magenta, white, yellow, green, purple, dark blue, red) with 'O' marked in a central yellow cell.](page_18_image_1_v2.jpg)

Tutte le celle attraversabili colorate in figura sono raggiungili da O attraverso un cammino libero di tipo 1 $\rightarrow$ per ciascuna di tali celle è noto un cammino minimo (il cammino libero di tipo 1) e la lunghezza di tale cammino (la distanza libera)

18

## Contesto di O

- Alcune celle che appartengono al contesto di O, oltre a essere raggiungibili da O con un cammino di tipo 1, possono essere raggiungibili con un cammino di tipo 2

<page_number>19</page_number>

# Complemento di O = insieme delle celle raggiungibili da O <u>solo</u> con cammini liberi di tipo 2

![Grid diagram showing a central cell 'O' and various colored paths, with orange shaded cells representing reachable areas via type 2 free paths.](page_20_image_1_v2.jpg)

Tutte le celle in arancione con sfumatura in figura sono raggiungili da O solo attraverso un cammino libero di tipo 2 $\rightarrow$ per ciascuna di tali celle è noto un cammino minimo (il cammino libero di tipo 2) e la lunghezza di tale cammino (la distanza libera)

20

## Compito 2

- Scrivere lo pseudocodice di un algoritmo che, data una griglia finita e una cella O della stessa, calcoli (non necessariamente separatamente) il contesto e il complemento di O. Costruire un’applicazione software che implementi tale algoritmo, acquisendo in ingresso una griglia prodotta dal generatore di cui al Compito 1
- La medesima applicazione deve essere in grado di calcolare la distanza libera fra due celle O e D

<page_number>21</page_number>

# ALTRI CAMMINI

22

## Quesito

- Per sinteticità, chiamiamo chiusura di O l’unione del contesto e del complemento di O; entro tale chiusura, chiamiamo celle di tipo 1 e celle di tipo 2 quelle che appartengono rispettivamente al contesto e al complemento di O
- Per le celle D che appartengono alla chiusura di O conosciamo un cammino minimo da O a D e la lunghezza dello stesso; come possiamo calcolare un cammino minimo e la sua lunghezza quando la cella destinazione D non appartiene alla chiusura di O?
- Prima di fornire una risposta, introduciamo alcuni concetti

<page_number>23</page_number>

# Chiusura di O

![Grid diagram showing the closure of set O with green cells, some with internal shading, and dark blue/white cells.](page_24_image_1_v2.jpg)

È la stessa immagine di pag. 20, dove tutte le celle appartenenti alla chiusura di O sono però in verde. Le celle verdi prive di sfumatura interna sono quelle appartenenti al contesto di O, quelle con sfumatura interna sono quelle appartenenti al complemento di O

24

# Frontiera di O

![Grid map showing an obstacle O in green and blue, with circles marking the boundary cells.](page_25_image_1_v2.jpg)

<mark>Frontiera</mark> di una cella O = insieme di tutte le celle della chiusura di O che sono adiacenti a una cella attraversabile che non appartiene a tale chiusura. In figura, le celle che costituiscono la frontiera di O sono quelle contenenti un cerchio.

25

# Idea

* Per raggiungere una cella D non appartenente alla chiusura di O è necessario passare per una cella della frontiera di O

* Un cammino minimo che raggiunge una cella D esterna alla chiusura di O è dato dalla composizione di più cammini minimi $\rightarrow$ proviamo a comporre più cammini liberi (il primo avente origine in O, il secondo avente origine in una cella della frontiera di O, ecc.) finché non troviamo una cella (di frontiera) la cui chiusura comprenda D

26

# Sequenza dei landmark

* È la sequenza O → F1 → F2 → F3 ..., ovvero l'origine O seguita dalle celle di frontiera lungo un cammino che stiamo esplorando per raggiungere la cella destinazione D. Se effettivamente D è raggiungibile da O, la sequenza dei landmark termina con D, cioè è O → F1 → F2 → F3 ... → D, altrimenti la sequenza dei landmark si arresta in corrispondenza di una cella di frontiera la cui chiusura ha una frontiera vuota

* Se, entro la sequenza dei landmark, <u>ogni cella di frontiera è accompagnata dal suo tipo</u> (come sempre assunto di seguito), a ogni cammino che stiamo esplorando corrisponde una (sola) sequenza dei landmark e viceversa, quindi la sequenza dei landmark può essere vista come una rappresentazione sintetica del cammino corrispondente

27

# Sequenza dei landmark

* A ogni tratto Fi →F(i+1) della sequenza dei landmark corrisponde un tratto del cammino che stiamo esplorando che non deve passare per nessuna cella (attraversabile) che appartenga alla chiusura delle celle (origine o di frontiera) che nella sequenza dei landmark compaiono prima di Fi
* Pertanto, durante l’esplorazione, il calcolo della chiusura di F1 (che è una cella di frontiera di O) deve escludere le celle della chiusura di O; il calcolo della chiusura di F2 (che è una cella di frontiera di F1) deve escludere sia le celle della chiusura di O sia quelle della chiusura di F1 come precedentemente calcolata, e così via. A tal fine, nel calcolo della chiusura di una cella di frontiera Fi, <u>tutte le celle delle chiusure relative alle celle che precedono Fi entro la sequenza dei landmark devono essere trattate come se fossero celle non attraversabili (ostacoli)</u>

28

# Definizione ricorsivadi un cammino minimo

* Un cammino minimo fra O e D, camminoMinimo(O,D), può essere definito ricorsivamente come

Min(camminoLibero(O,F).camminoMinimo(F,D))al variare di F entro la frontiera della chiusura di O

dove camminoLibero(O,F) è un cammino libero da O a F, . è l’operatore di composizione (in sequenza) fra cammini e Min è un operatore che seleziona un cammino di lunghezza minima fra tutti i cammini camminoLibero(O,F).camminoMinimo(F,D) ottenibili al variare di F entro la frontiera di O

* Lo pseudocodice della pagina seguente sfrutta la definizione di cui sopra per determinare un cammino minimo fra O e D e la lunghezza di tale cammino

29

1: **procedure** CAMMINOMIN($O, D, dim, osta$) $\quad \triangleright$ ritorna la lunghezza del cammino minimo ($lunghezzaMin$) da $O$ a $D$ (che è infinita se $D$ non è raggiungibile da $O$) e la sequenza dei landmark ($seqMin$) lungo un cammino minimo (sequenza in base al quale è possibile ricostruire l'intero percorso)

2: $\quad \triangleright$ $dim$ rappresenta le (due) dimensioni della griglia e $osta$ l'insieme delle celle non attraversabili della stessa

3: $\quad contesto \leftarrow \text{CALCOLACONTESTO}(O, dim, osta)$
4: $\quad$ **if** $D \in contesto$ **then**
5: $\quad \quad$ **return** $\text{DLIB}(O,D), \langle(O,0), (D,1)\rangle \quad \quad \quad \quad \quad \quad \triangleright$ sequenza di due elementi
6: $\quad complemento \leftarrow \text{CALCOLACOMPLEMENTO}(O, dim, osta)$
7: $\quad$ **if** $D \in complemento$ **then**
8: $\quad \quad$ **return** $\text{DLIB}(O,D), \langle(O,0), (D,2)\rangle$
9: $\quad frontiera \leftarrow \text{CALCOLAFRONTIERA}(contesto, complemento, dim, osta)$
10: $\quad$ **if** $frontiera = \emptyset$ **then** $\quad \quad \quad \quad \quad \quad \quad \quad \quad \quad \quad \quad \quad \quad \quad \quad \triangleright$ vicolo cieco
11: $\quad \quad$ **return** $\infty, \langle \rangle$
12: $\quad lunghezzaMin \leftarrow \infty$
13: $\quad seqMin \leftarrow \langle \rangle \quad \quad \quad \quad \quad \quad \quad \quad \quad \quad \quad \quad \quad \quad \quad \quad \quad \quad \quad \quad \quad \triangleright$ sequenza di vuota
14: $\quad$ **for each** $(F, t) \in frontiera$ **do**
15: $\quad \quad lF \leftarrow \text{DLIB}(O,F)$
16: $\quad \quad$ **if** $lF < lunghezzaMin$ **then**
17: $\quad \quad \quad \quad \quad \quad \quad \triangleright$ una condizione più forte è $lF + \text{DLIB}(F,D) < lunghezzaMin$
18: $\quad \quad \quad \quad lFD, seqFD \leftarrow \text{CAMMINOMIN}(F, D, dim, osta \cup contesto \cup complemento)$
19: $\quad \quad \quad \quad lTot \leftarrow lF + lFD$
20: $\quad \quad \quad \quad$ **if** $lTot < lunghezzaMin$ **then**
21: $\quad \quad \quad \quad \quad lunghezzaMin \leftarrow lTot$
22: $\quad \quad \quad \quad \quad seqMin \leftarrow \text{COMPATTA}(\langle(O,0), (F,t)\rangle, seqFD)$
23: $\quad$ **return** $lunghezzaMin, seqMin$

30

## Intestazione

- I parametri d’ingresso dim e osta di

CAMMINOMIN rappresentano cumulativamente

la griglia. Questo <u>non</u> significa che, nella codifica

dell’algoritmo, i parametri adottati debbano

essere necessariamente quelli indicati. Nello

pseudocodice sono stati usati questi parametri

per due ragioni:

– Per evidenziare che l’algoritmo deve ricevere in ingresso una griglia

– Per evidenziare che l’insieme delle celle non attraversabili della griglia (che costituiscono gli ostacoli) cambia in invocazioni diverse

<page_number>31</page_number>

# Parametri di ingresso

* All’invocazione principale di CAMMINOMIN, O e D sono due celle attraversabili (la sussistenza di questa precondizione dovrebbe essere accertata dal chiamante)
* Nelle invocazioni annidate di CAMMINOMIN il primo parametro, appartenendo a una frontiera, è sì una cella traversabile ma che viene considerata come un ostacolo (vedi pag. 28)
* Si noti che O e D possono coincidere (nel qual caso i valori di ritorno sono una lunghezza nulla e la sequenza dei landmark ⟨(O, 0) (O, 1)⟩)

32

## Righe da 3 a 9

- CALCOLACONSTESTO(O, dim, osta) e CALCOLACOMPLEMENTO (O, dim, osta) determinano rispettivamente il contesto e il complemento di O
- Nello pseudocodice, il calcolo di contesto e complemento avvengono separatamente al fine di attribuire

– alla cella D, nel caso appartenga alla chiusura di O, il tipo (1 o 2) che le compete (righe 5 e 8)

– a ciascuna cella della frontiera di O il tipo (1 o 2) che le

compete, nel caso D non appartenga alla chiusura di O;

l’assegnamento del tipo avverrà ad opera di

CALCOLAFRONTIERA (riga 9)

<page_number>33</page_number>

# Caso base

* Le righe 5 e 8 gestiscono il caso base della ricorsione, cioè quello in cui la cella D appartiene alla chiusura di O
* Si noti che, in virtù di tale gestione, l’algoritmo CAMMINOMIN sussume l’elaborazione di cui al Compito 2
* Le righe da 3 a 9 seguono lo schema della produzione separata di contesto e complemento e della successiva individuazione della frontiera; <u>la codifica dell’algoritmo potrebbe anche non essere fedele allo pseudocodice, purché produca gli stessi effetti operativi (ovvero sia in grado di gestire il caso base, di identificare le frontiera e il tipo di ciascuna delle celle appartenenti alla stessa)</u>
* Si noti che, per gestire il caso base, sarebbe sufficiente accertarsi che esista un cammino libero fra O e D

34

# Moduli

*   DLIB($O,D$) ritorna il valore dlib($O,D$) di cui alle pag. 16-17 e al Compito 2
*   CALCOLAFRONTIERA(*contesto, complemento, dim, osta*) determina la frontiera di *O*. Per determinare tale frontiera non è necessario conoscere *O*, basta conoscere la sua chiusura, cioè l’insieme di celle (*contesto* $\cup$ *complemento*) nonché la griglia (cioè i parametri *dim* e *osta*). Ritorna un insieme di coppie ($F, t$), dove $F$ è una cella della frontiera di $O$, $t$ assume il valore 1 se $F$ appartiene al contesto e 2 se $F$ appartiene al complemento
*   Come già osservato nella pagina precedente, il calcolo che nello pseudocodice è compiuto da CALCOLAFRONTIERA nella codifica potrebbe essere effettuato da un modulo che cumulativamente sortisce l’effetto operativo delle righe da 3 a 9 dello pseudocodice

35

# Valori di ritorno

* COMPATTA(⟨(O, 0) (F, t)⟩, *seqFD*) riceve in ingresso due sequenze (dei landmark) che hanno la forma rispettivamente ⟨(O, 0) (F, t)⟩ e ⟨(F,0) (F1, t1)... (D, tD)⟩. Ritorna la sequenza (dei landmark) unica ⟨(O, 0) (F, t) (F1, t1)... (D, tD)⟩ ottenuta accodando la seconda alla prima, omettendo il primo elemento della seconda
* La sequenza dei landmark *seqMin* ritornata dall’invocazione principale dell’algoritmo consente di ricostruire l’intero percorso minimo corrispondente alla sequenza stessa
* Ad esempio, se *seqMin* = ⟨(O,0) (F,1) (G,2) (H,1) (D,1)⟩, al tratto O→F corrisponde un cammino libero di tipo 1, al tratto F→G corrisponde un cammino libero di tipo 2 e a entrambi i tratti G→H e H→D corrispondono cammini liberi di tipo 1

36

## Righe 16 e 17

- Il fine della struttura condizionale di cui alla riga 16 dello pseudocodice di CAMMINOMIN è quello di ridurre lo spazio di ricerca, cioè evitare di esplorare alcuni cammini che sicuramente non sono minimi. La riga 16 potrebbe essere rimossa (promuovendo così le istruzioni di cui alle righe 18-20 a istruzioni appartenenti incondizionatamente al corpo del ciclo for di cui alla riga 14) senza compromettere la correttezza dell’algoritmo (ma verosimilmente riducendone l’efficienza)
- L’efficacia della riduzione del numero di cammini da esplorare operata dalla struttura condizionale di cui alla riga 16 dipende dai parametri dell’algoritmo CAMMINOMIN
- Una riduzione superiore si potrebbe ottenere adottando come condizione, al posto di quella alla riga 16, quella riportata nel commento di cui alla riga 17, la cui valutazione è leggermente più costosa
- La condizione alla riga 17 è vera se la somma (a) della distanza effettiva (che è nota) fra O e F e (b) del limite inferiore – forse irraggiungibile – della distanza (ignota) fra F e D (limite rappresentato dalla distanza libera fra F e D) è minore della più breve distanza fra tutte quelle dei cammini fra F e D che sono già stati esplorati

<page_number>37</page_number>

# Compito 3

* Utilizzare lo pseudocodice di CAMMINOMIN (e le osservazioni contenute nelle pagine a esso successive) per ampliare l’applicazione di cui al compito precedente affinché, data una cella origine O e una cella destinazione D, sia in grado di fornire la sequenza dei landmark relativa a un cammino minimo (se esiste) che porti a O a D e la lunghezza dello stesso (se O e D non sono reciprocamente raggiungibili, viene ritornata una lunghezza infinita e una sequenza vuota)
* L’applicazione deve inoltre essere in grado di sfruttare la sequenza di landmark di cui sopra per costruire il cammino minimo relativo (come sequenza di mosse/celle). Questa richiesta deve essere soddisfatta solo se il gruppo di lavoro è costituito da tre persone

38

### ESEMPIO

<page_number>39</page_number>

# Frontiera di O


<table>
    <tr>
        <td></td>
        <td></td>
        <td></td>
        <td>R</td>
        <td></td>
        <td>S</td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td></td>
        <td></td>
        <td></td>
        <td>S</td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td>T</td>
        <td>U</td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td>O</td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td>F</td>
        <td>A</td>
        <td>B</td>
        <td>C</td>
        <td>E</td>
        <td></td>
        <td>∆</td>
        <td>F</td>
        <td>G</td>
    </tr>
    <tr>
        <td>V</td>
        <td>W</td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td>X</td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td>G</td>
        <td>H</td>
        <td>I</td>
        <td>J</td>
        <td>K</td>
        <td>L</td>
        <td>M</td>
        <td></td>
        <td></td>
        <td>D</td>
    </tr>
    <tr>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td>Y</td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td>N</td>
        <td>P</td>
        <td>Q</td>
    </tr>
</table>


È la stessa immagine di pag. 25 in cui è stata indicata (in rosso) la cella destinazione D e a ciascuna cella appartenente alla frontiera della cella origine O è stato assegnato un identificatore univoco

40

# Invocazione principale:
# CAMMINOMIN(O, D, dim, osta)

* D non appartiene alla chiusura di O, la frontiera di O non è vuota, si effettua pertanto l’inizializzazione
*lunghezzaMin* entro invocazione principale $\leftarrow \infty$
*seqMin* entro invocazione principale $\leftarrow \langle \rangle$

* Dopodiché viene eseguito, per ogni coppia (F,t) corrispondente a una cella della frontiera di cui al lucido precedente, il corpo del ciclo for (si noti che nell’esempio che stiamo considerando il valore di t è 1 per ogni cella della frontiera di O)

* Supponiamo che la prima cella considerata sia A

41

# Invocazione principale:
# iterazione (ciclo for) per (A,1)

* Avviene l’inizializzazione
IF <span style="color: #D3D3D3">entro invocazione principale</span> $\leftarrow$ DLIB(O,A)=
$\sqrt{2+5}$

42

# Invocazione annidata (1° livello): CAMMINOMIN (A, D, dim, osta $\cup$ contesto di O $\cup$ complemento di O)

![Grid diagram showing regions O, A, Z, and D with green, blue, orange, and white cells. Region A is a yellow circle, Z is an orange circle, and D is a red letter in a white cell.](page_43_image_1_v2.jpg)

In arancione compare la chiusura di A (che non contiene D) con le sue due celle di frontiera. Entro il ciclo for dell’invocazione annidata, consideriamo per prima la cella Z

43

# Invocazione annidata (1° livello):
# iterazione per (Z,1)

* Avviene l’inizializzazione
IF <span style="color: #cccccc">entro invocazione 1° livello</span> ← DLIB(A,Z) = 2√2+3

44

# Invocazione annidata (2° livello): CAMMINOMIN (Z, D, dim, osta $\cup$ contesto di A $\cup$ complemento di A)

![Diagramma a griglia che mostra un percorso in un ambiente con ostacoli (blu), aree esplorate (verde, giallo) e landmark (O, A, Z, D).](page_45_image_1_v2.jpg)

In viola compare la chiusura di Z, che contiene D. Dunque l'invocazione corrente (di secondo livello) ritorna (a quella di primo livello) DLIB(Z,D) = $\sqrt{2}+1$ e la sequenza (dei landmark) $\langle(Z,0) (D,1)\rangle$

45

# Invocazione annidata (1° livello): conclusione dell’iterazione per (Z,1)

* Riceve
    lFD = $\sqrt{2}+1$
    seqFD = $\langle(Z,0) (D,1)\rangle$
* Calcola
    lTot <font color="#D3D3D3">entro invocazione 1° livello</font> $\leftarrow$ $(2\sqrt{2}+3) + (\sqrt{2}+1)$
    lunghezzaMin <font color="#D3D3D3">entro invocazione 1° livello</font> $\leftarrow$ $3\sqrt{2}+4$
    seqMin <font color="#D3D3D3">entro invocazione 1° livello</font> $\leftarrow$ COMPATTA($\langle(A,0) (Z,1)\rangle$ $\langle(Z,0) (D,1)\rangle$) = $\langle(A,0) (Z,1) (D,1)\rangle$

46

Invocazione annidata (1° livello): CAMMINOMIN (A, D, dim, osta $\cup$ contesto di O $\cup$ complemento di O)

![Diagram showing a grid with various colored cells (green, blue, yellow, orange, white) and markers. A red 'O' is in the center-left, a yellow circle 'A' is in the center-right, an orange circle 'Z1' is on the right, and a red 'D' is in the bottom-right corner.](page_47_image_1_v2.jpg)

Alla seconda iterazione del ciclo for (entro l’invocazione annidata di primo livello), consideriamo la cella Z1 appartenente alla frontiera di A

47

# Invocazione annidata (1° livello):
# iterazione (ciclo for) per (Z1,1)

* Avviene l’inizializzazione
IF <span style="color: #D3D3D3">entro invocazione 1° livello</span> ← DLIB(A,Z1) =
$\sqrt{2+5}$

48

# Invocazione annidata (2° livello): CAMMINOMIN (Z1, D, dim, osta $\cup$ contesto di O $\cup$ complemento di O)

![Grid diagram showing a pathfinding scenario with regions O, A, Z1, and D on a green grid with obstacles and landmarks.](page_49_image_1_v2.jpg)

La chiusura di Z1 (in fuxia) contiene D. Dunque l'invocazione corrente (di secondo livello) ritorna (a quella di primo livello) DLIB(Z1,D) = $\sqrt{2}+1$ e la sequenza (dei landmark) $\langle(Z1,0) (D,1)\rangle$

49

# Invocazione annidata (1° livello): conclusione dell’iterazione per (Z1,1)

* Riceve
    lFD entro invocazione 1° livello = $\sqrt{2}+1$
    seqFD entro invocazione 1° livello = $\langle$(Z1,0) (D,1)$\rangle$

* Calcola
    lTot entro invocazione 1° livello $\leftarrow$ ($\sqrt{2}+5$) + ($\sqrt{2}+1$)

* Poiché lTot entro invocazione 1° livello non è minore di lunghezzaMin entro invocazione 1° livello (che vale $3\sqrt{2}+4$), avendo concluso tutte (e due) le iterazioni del ciclo for, ritorna (all’invocazione principale)
    lunghezzaMin entro invocazione 1° livello = $3\sqrt{2}+4$
    seqMin entro invocazione 1° livello = $\langle$(A,0) (Z,1) (D,1)$\rangle$

50

# Invocazione principale: conclusione dell'iterazione per (A,1)

* Riceve
    lFD entro invocazione principale = $3\sqrt{2}+4$
    seqFD entro invocazione principale = $\langle(A,0) (Z,1) (D,1)\rangle$
* e calcola
    lTot entro invocazione principale = $(\sqrt{2}+5) + (3\sqrt{2}+4)$
* Al termine della prima iterazione del ciclo for entro invocazione principale avvengono le inizializzazioni
    lunghezzaMin entro invocazione principale $\leftarrow 4\sqrt{2}+9$
    seqMin entro invocazione principale $\leftarrow$ COMPATTA($\langle(O,0) (A,1)\rangle$ $\langle(A,0) (Z,1) (D,1)\rangle$) = $\langle(O,0) (A,1) (Z,1) (D,1)\rangle$
* A questo punto l'invocazione principale deve procedere con le successive 26 iterazioni per le rimanenti celle della frontiera di O (ma nessuna di queste porterà a un cammino di lunghezza inferiore a $4\sqrt{2}+9$)

51

# Albero di ricorsione

![Albero di ricorsione che mostra i nodi O,D, A,D, B,D, C,D, Σ,D, R,D, S,D, T,D, U,D, V,D, W,D, X,D, Y,D, Z,D, Z1,D e rami tratteggiati.](page_52_image_1_v2.jpg)

Tutte queste nove esplorazioni riguardano cammini di lunghezza infinita

In rosa è evidenziata l’esplorazione esemplificata nelle pagine precedenti (ogni nodo contiene i primi due parametri dell’invocazione relativa); la foglia sull’estrema sinistra è quella inerente all’esplorazione del percorso di lunghezza minima, ricostruito nella pagina successiva

52

# Percorso di lunghezza minima

![Diagramma di un percorso su una griglia con landmark O, A, Z, D](page_53_image_1_v2.jpg)

La figura evidenzia il cammino (minimo, di lunghezza $4\sqrt{2}+9$) corrispondente alla sequenza dei landmark $\langle(O,0) (A,1) (Z,1) (D,1)\rangle$

53

## CAMMINOMIN(D, O, dim, osta)

- L’algoritmo CAMMINOMIN può naturalmente essere invocato scambiando i due parametri O e D (nell’invocazione principale)
- Se l’algoritmo è corretto, la lunghezza del cammino minimo calcolata deve essere la stessa mentre il cammino minimo trovato in generale è diverso
- Nelle pagine seguenti viene brevemente illustrata l’invocazione di cui al titolo di questa pagina

<page_number>54</page_number>

# Chiusura di D

![Diagram showing a grid with various colored cells (dark blue, solid green, and green with internal gradient) representing a mathematical or logical operation. The letters 'O' and 'D' are placed within the grid.](page_55_image_1_v2.jpg)

Come al solito, le celle appartenenti al complemento sono quelle visualizzate con una sfumatura interna

55

# Frontiera di D


<table>
    <tr>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td>K</td>
        <td></td>
        <td>L</td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td>M</td>
        <td></td>
        <td>N</td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td>P</td>
        <td></td>
        <td>Q</td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td>R</td>
        <td></td>
        <td>S</td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td>O</td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td>T</td>
        <td></td>
        <td>U</td>
        <td></td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td>V</td>
        <td></td>
        <td>W</td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td>X</td>
        <td></td>
        <td>Y</td>
        <td></td>
    </tr>
    <tr>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td>Z</td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td>D</td>
    </tr>
    <tr>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td>A</td>
        <td>B</td>
        <td>C</td>
        <td>D</td>
        <td>E</td>
        <td>G</td>
        <td>H</td>
        <td>I</td>
        <td>J</td>
        <td></td>
        <td></td>
    </tr>
</table>


Le celle appartenenti alla frontiera di D sono quelle contenenti un cerchio; a ciascuna di esse è stato assegnato un identificatore univoco

56

# Chiusura di Z

![Diagram showing a grid with various colored cells (orange, dark blue, green circles) and labels O, Z, and D. The orange cells represent the closure of Z.](page_57_image_1_v2.jpg)

Alla prima iterazione del ciclo for della chiamata principale supponiamo sia considerata la cella Z, che porta alla prima chiamata annidata; la chiamata annidata identifica le celle della chiusura di Z (in arancione)

57

# Frontiera di Z


<table>
    <tr>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td>Z11</td>
        <td>Z10</td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td>Z9</td>
        <td>Z8</td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td>Z7</td>
        <td>Z6</td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td>Z5</td>
        <td>Z4</td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td>O</td>
        <td></td>
        <td></td>
        <td></td>
        <td>Z3</td>
        <td>Z2</td>
        <td></td>
        <td>Z12</td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td>Z15</td>
    </tr>
    <tr>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td>Z1</td>
        <td></td>
        <td></td>
        <td>Z13</td>
        <td></td>
        <td></td>
        <td></td>
        <td>Z14</td>
        <td></td>
    </tr>
    <tr>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td>Z</td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td>Z16</td>
        <td>Z17</td>
        <td>Z18</td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td>D</td>
    </tr>
</table>


La figura evidenzia la frontiera di Z, dove a ciascuna cella appartenente alla frontiera di Z è stato assegnato un identificatore univoco

58

# Chiusura di Z1

![Diagramma a griglia che mostra la chiusura ricorsiva della cella Z1 evidenziata in fucsia, con le celle O, Z1, Z e D contrassegnate.](page_59_image_1_v2.jpg)

Supponiamo che la prima iterazione del ciclo for della chiamata annidata consideri la cella Z1; ciò porta a un’invocazione ricorsiva di secondo livello, che calcola la chiusura di Z1 (in fuxia). Tale chiusura contiene O (piede della ricorsione)

59

# Percorso di lunghezza minima

![Diagram showing a grid with colored cells (magenta, orange, green, blue, yellow) and a path connecting points O, Z1, Z, and D.](page_60_image_1_v2.jpg)

L’invocazione principale termina la prima iterazione del ciclo for (quella relativa alla cella Z) assegnando a seqFD la sequenza dei landmark $\langle$(D,0) (Z,2) (Z1,2) (O,2)$\rangle$ e a lFD la lunghezza del cammino corrispondente a tale sequenza (quello in figura), cioè $(1+\sqrt{2})+(4+2\sqrt{2})+(4+\sqrt{2})=9+4\sqrt{2}$

60

# Invocazione principale: conclusione dell’iterazione per (Z,1)

* Dopo la prima iterazione del ciclo for entro la chiamata principale valgono dunque le seguenti uguaglianze
lunghezzaMin entro invocazione principale = $4\sqrt{2}+9$
codaMin entro invocazione principale =
⟨(D,0) (Z,2) (Z1,2) (O,2)⟩

* Dovranno essere effettuate anche le rimanenti 23 iterazioni del ciclo for (che però non portano a cammini più brevi)

* Si noti che la lunghezza del cammino minimo è la medesima ottenuta con l’invocazione CAMMINOMIN(O, D, dim, osta) mentre il cammino minimo trovato non è lo stesso

61

### SPERIMENTAZIONE

<page_number>62</page_number>

## Generalità

- La correttezza e le prestazioni di un algoritmo possono essere analizzate formalmente, come appreso durante le lezioni dell’insegnamento, ma anche sperimentalmente, ovvero eseguendo delle prove di funzionamento su numerose istanze
- L’abilità dello sperimentatore è quella di individuare istanze significative da usare per le prove, cioè istanze che possano evidenziare comportamenti diversi dell’algoritmo al variare di alcuni parametri che influenzano le sue prestazioni
- La sperimentazione può anche essere volta al confronto di implementazioni diverse (ad esempio, relativamente alle strutture dati) dell’algoritmo
- Le pagine successive avanzano alcune considerazioni sulla sperimentazione relativa all’algoritmo CAMMINOMIN

<page_number>63</page_number>

# Correttezza

* Ai fini della valutazione di correttezza, per ciascuna coppia di celle considerata nella sperimentazione, l’algoritmo di calcolo del cammino minimo e della sua lunghezza deve essere <u>invocato due volte,</u> considerando così i due parametri in entrambi gli ordini relativi. La lunghezza del cammino minimo calcolata dalle due invocazioni deve essere confrontata: una differenza fra le due uscite è indice di un errore logico nell’algoritmo e/o di un errore nella sua implementazione
* Il punto precedente è da intendersi come una richiesta relativa alla sperimentazione che dovrà essere effettuata dai gruppi di lavoro

64

## Prestazioni

- Il primo fine della sperimentazione da parte dei gruppi di lavoro è quello di registrare e valutare criticamente le prestazioni spaziali e temporali delle prove condotte
- Le prestazioni spaziali dipendono, fra l’altro, dalle dimensioni della griglia e dalle sue modalità di rappresentazione
- Le prestazioni temporali dell’algoritmo CAMMINOMIN dipendono dalla coppia di celle considerate (sorgente e destinazione), dall’ordine con cui compaiono nel passaggio dei parametri, dalla topologia della griglia e, infine, dall’ordine con cui sono considerate (nelle varie invocazioni dell’algoritmo) le celle di frontiera entro il ciclo for

<page_number>65</page_number>

# Osservazione

* Verosimilmente ordinare le celle di frontiera secondo qualche criterio (dipendente dagli elementi di cui al punto precedente) prima di eseguire il ciclo for e passarle in rassegna in tale ordine potrebbe produrre effetti benefici. Ad esempio, si potrebbe adottare il criterio euristico goloso di ordinare le celle di frontiera per valori non decrescenti della distanza libera dalla cella destinazione. È evidente che l’applicazione di un criterio di ordinamento ha un costo superiore rispetto all’adozione di un ordinamento casuale (ma potrebbe ripagare in termini di riduzione del numero dei cammini esplorati)
* Il punto precedente è da intendersi come un’osservazione, non come una richiesta relativa alla sperimentazione

66

### Confronto relativo a scelte implementative diverse

- La sperimentazione potrebbe in aggiunta confrontare l’efficacia delle due condizioni alternative adottabili alla riga 16 dello pseudocodice
- Il punto precedente è da intendersi come una richiesta che può essere opzionalmente soddisfatta dai soli gruppi costituiti da tre persone (e non deve essere tenuta in conto dai gruppi costituiti da un numero inferiore di persone)

<page_number>67</page_number>

## Compito 4

- Sfruttare le griglie create dal generatore di cui al Compito 1 per operare una sperimentazione relativa all’implementazione dell’algoritmo CAMMINOMIN di cui al Compito 3, tenendo conto delle richieste presentate nella sezione corrente
- La sperimentazione deve essere condotta con tutte le tipologie di griglie prodotte dal Compito 1

<page_number>68</page_number>

# CONSEGNE

69

# Gruppi di lavoro

* Un gruppo è, di norma, costituito da <u>tre</u> studenti
* Ogni gruppo deve
    - svolgere i quattro compiti descritti nelle sezioni precedenti, soddisfacendo anche i requisiti (funzionali e non) descritti nelle prossime pagine. Nel caso eccezionale in cui il lavoro venisse affrontato da un gruppo comprendente <u>meno di tre</u> studenti, il Compito 1 deve essere svolto nella sua forma semplificata (vedi pag. 9), del Compito 3 non deve essere considerata la seconda richiesta (vedi pag. 38), il Compito 4 risulta facilitato come conseguenza della semplificazione del Compito 1, il secondo requisito funzionale di cui alla prossima pagina non deve essere soddisfatto
    - redigere una relazione scritta che illustri il lavoro svolto, le <mark>scelte implementative</mark> compiute, la <mark>sperimentazione</mark> condotta e una <mark>valutazione critica</mark> degli esiti sperimentali

70

# Requisiti funzionali

* L’applicazione sviluppata, oltre a produrre le uscite già descritte, deve:
    - per ogni istanza di problema in ingresso, creare (se desiderato dall’utente) un riassunto che compendi le dimensioni e il tipo della griglia d’ingresso, il numero totale di celle di frontiera che si sono individuate durante l’esecuzione dell’algoritmo CAMMINOMIN, il numero totale di volte in cui la condizione alla riga 16/17 ha assunto il valore «falso», le prestazioni riscontrate
    - consentire all’utente di interrompere il calcolo prima che esso sia concluso (o eventualmente di fissare una durata massima per l’elaborazione), fornendo in uscita il cammino (sotto forma di sequenza dei landmark) di lunghezza minore fra quelli sinora considerati, la lunghezza dello stesso e un riassunto analogo a quello del punto precedente, esplicitando però che il calcolo non è stato completato. Come già evidenziato, questo requisito vale solo per i gruppi di tre persone

71

# Lavoro e relazione

* Particolare attenzione deve essere dedicata alla <span style="color: #4F81BD">scelta di strutture dati</span> volte a <u>estendere le dimensioni delle griglie che possono essere elaborate</u> nonché di altri accorgimenti aventi lo stesso fine. La relazione deve documentare tali scelte e accorgimenti
* Sono naturalmente apprezzati gli sforzi tesi a <u>ridurre il costo temporale della computazione</u>, che devono anch’essi essere documentati
* È consentita qualsiasi forma di <span style="color: #4F81BD">riuso del software</span>
* La relazione deve contenere ogni indicazione ritenuta utile al fine di consentire l’utilizzo dei programmi realizzati e la conduzione di ulteriori sperimentazioni
* La relazione deve evidenziare tutte le limitazioni riscontrate nelle prove di esecuzione effettuate

72

## Requisiti non funzionali

- Non è richiesta la realizzazione di GUI
- L’elaborazione dei programmi da realizzare può essere batch (I/O solo da/per file)
- Non è richiesto il soddisfacimento di altri

requisiti non funzionali oltre a quelli

evidenziati nelle sezioni precedenti; in

particolare, non è imposto un linguaggio di

programmazione, né un ambiente di sviluppo

né un ambiente di destinazione

<page_number>73</page_number>

# Consegna del materiale

* Ai fini del superamento della prova orale è necessario consegnare, entro i tempi indicati nelle note relative agli appelli, una cartella elettronica contenente relazione (in formato sia “sorgente”, sia pfd), codice sorgente ed eventuale codice eseguibile dei programmi software sviluppati, le prove sperimentali effettuate, accompagnate dai relativi riassunti generati automaticamente nonché da eventuali file (ad es. Excel o Matlab) creati al fine di valutare gli andamenti delle prestazioni
* La consegna deve avvenire inviando via email il link a tale cartella, link creato usando un sistema di condivisione (ad es. dropbox, GDrive), oppure attraverso la piattaforma Moodle
* Il progetto descritto in questo documento deve essere presentato entro la sessione d’esame autunnale di Novembre 2026 (inclusa)

74