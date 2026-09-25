# MONITOR SECCHIA
## Sistema intelligente per il monitoraggio della biodiversità osservata

### 1. Idea e obiettivo del progetto

Monitor Secchia è un sistema progettato per raccogliere e organizzare automaticamente informazioni sulla biodiversità animale osservata nella zona della Cassa di espansione del Secchia.

L'idea nasce dalla necessità di trasformare semplici avvistamenti di animali in dati organizzati e utilizzabili nel tempo. Il sistema non si limita quindi a riconoscere una specie, ma costruisce una vera e propria sequenza di osservazioni: rileva la presenza di un animale, cerca di identificarlo attraverso immagini o suoni, registra il risultato in un database, valuta quanto sia affidabile l'identificazione e utilizza i dati raccolti per analizzare la biodiversità osservata.

Il progetto deve essere considerato come un sistema di monitoraggio e non come una semplice fototrappola. La fototrappola rappresenta infatti soltanto il punto di raccolta dei dati. La parte più importante del progetto è l'intero sistema che trasforma quei dati in informazioni.

Il risultato finale sarà quindi composto da una piccola stazione di monitoraggio fisica, un sistema software che analizza le osservazioni e una dashboard consultabile da tablet o computer.

Il progetto deve essere costruito in modo modulare, così da poter iniziare con una sola stazione e successivamente aggiungerne altre. Una futura installazione potrebbe infatti utilizzare stazioni chiamate, ad esempio, `SECCHIA-01`, `SECCHIA-02`, `SECCHIA-03` e così via. In questo modo sarà possibile confrontare la biodiversità osservata in punti diversi.

È importante inoltre chiarire che il sistema misura la **biodiversità osservata dal sistema**, non la biodiversità assoluta dell'intera Riserva. Una singola fototrappola non può rappresentare tutto l'ecosistema. Per questo nella dashboard verrà utilizzata la dicitura **“Indice di biodiversità osservata”** o **“Indice di diversità delle osservazioni”**.

---

### 2. Come funzionerà il sistema

Il funzionamento può essere immaginato come una catena.

Un animale entra nell'area osservata e viene rilevato dal sistema. La stazione può acquisire un'immagine oppure un suono. Il dato viene inviato attraverso la rete al backend, che si occupa dell'analisi.

Per le immagini il sistema potrà utilizzare l'API di iNaturalist per ottenere una possibile identificazione della specie. Per i suoni verrà utilizzato BirdNET, che permette di analizzare vocalizzazioni e canti degli uccelli.

Una volta ottenuto il risultato, il backend registra l'osservazione nel database Supabase.

L'osservazione non sarà composta solamente dal nome della specie. Verranno salvate anche informazioni utili a capire da dove proviene il dato, quando è stato raccolto e quanto è affidabile.

La dashboard leggerà quindi i dati dal database e mostrerà automaticamente le nuove osservazioni, le specie individuate, l'andamento della biodiversità e gli eventuali alert.

Il flusso completo sarà:

**Animale → stazione di monitoraggio → immagine/suono → ESP32 → Wi-Fi → backend FastAPI → BirdNET/iNaturalist → identificazione + affidabilità → Supabase → analisi → dashboard e alert**

Questa struttura permette di separare chiaramente la parte fisica dalla parte software.

---

### 3. La stazione di monitoraggio

Per il prototipo verrà realizzata una piccola fototrappola da tavolo. Non è necessario costruire subito una vera fototrappola professionale: l'obiettivo è creare un modello funzionante che dimostri il principio del sistema.

Il contenitore potrà essere realizzato con la stampante 3D oppure con il laser cutter. Al suo interno saranno presenti i componenti elettronici necessari.

Il componente centrale sarà un **ESP32**, scelto soprattutto perché dispone di Wi-Fi e permette quindi di comunicare direttamente con il sistema software.

A esso potrà essere collegato un modulo camera compatibile con ESP32, insieme a un microfono per la parte audio.

Per la dimostrazione fisica potrà essere utilizzato anche l'Arduino Uno già disponibile, collegato a un sensore PIR. Il PIR rileverà il movimento di una persona davanti alla stazione e farà partire la simulazione della rilevazione.

In questo modo, durante la presentazione, una persona potrà avvicinarsi alla fototrappola e attivare il sistema.

Il prototipo non deve necessariamente riprodurre ogni dettaglio di una stazione professionale. Deve invece dimostrare chiaramente che il concetto può funzionare in maniera automatizzata.

---

### 4. Come verrà fatta la dimostrazione

La demo deve essere progettata per essere affidabile anche se durante l'evento la connessione Internet o un componente dovesse avere un problema.

Una possibile dimostrazione consiste nel far avvicinare una persona alla stazione. Il sensore PIR rileva il movimento e il sistema avvia la raccolta del dato.

Per la parte audio si può riprodurre vicino al microfono il canto di un uccello precedentemente preparato. BirdNET analizzerà il suono e restituirà una possibile specie con il relativo livello di affidabilità.

Per la parte fotografica si può invece mostrare alla camera un'immagine di un animale preparata per il test. Il backend invierà l'immagine al sistema di riconoscimento e riceverà una possibile identificazione.

Il risultato apparirà quasi immediatamente sulla dashboard visualizzata sul tablet Samsung.

Per rendere la demo robusta, il sistema dovrà avere anche una modalità dimostrativa con dati già preparati. In questo modo, se durante la gara il Wi-Fi non dovesse funzionare, sarà comunque possibile mostrare il funzionamento completo del progetto senza fingere che il sistema stia elaborando dati reali.

---

### 5. Il backend e l'intelligenza del sistema

Il backend sarà sviluppato in Python utilizzando **FastAPI**.

Il suo compito sarà quello di fare da collegamento tra la stazione, i servizi di riconoscimento e il database.

Quando riceve un'immagine o un file audio, il backend determina quale analisi effettuare. Nel caso dell'audio utilizzerà BirdNET; nel caso dell'immagine utilizzerà iNaturalist.

Dopo l'identificazione, il backend costruirà l'osservazione completa e la salverà in Supabase.

Il backend dovrà inoltre occuparsi della logica che non viene fornita direttamente dalle API. Questa parte è importante per il progetto perché permette di dimostrare che Monitor Secchia non consiste semplicemente nel collegare tre servizi esterni.

La squadra costruirà infatti la logica che permette di:

- raccogliere le osservazioni;
- distinguere audio e immagini;
- associare ogni dato a una stazione;
- salvare data e ora;
- memorizzare il livello di affidabilità;
- gestire le verifiche;
- distinguere specie comuni, rare, protette e invasive;
- calcolare l'indice di biodiversità;
- generare gli alert;
- mostrare tutto sulla dashboard.

BirdNET e iNaturalist saranno quindi strumenti utilizzati all'interno di un sistema progettato dalla squadra.

---

### 6. Il database

Il database sarà realizzato con Supabase.

La tabella principale potrà essere chiamata `osservazioni`.

Ogni riga rappresenterà una singola osservazione.

I campi principali saranno:

| Campo | Funzione |
|---|---|
| `id` | Identificativo univoco |
| `species` | Specie identificata |
| `category` | Categoria della specie |
| `method` | Audio o foto |
| `media_url` | Collegamento al file originale |
| `date_time` | Data e ora |
| `station_id` | Stazione che ha raccolto il dato |
| `confidence` | Affidabilità dell'identificazione |
| `verification_status` | Stato della verifica |
| `source` | BirdNET, iNaturalist o altra fonte |
| `source_update_date` | Data di aggiornamento della fonte |
| `habitat_zone` | Zona/habitat, se disponibile |
| `coordinates` | Coordinate, se disponibili |
| `quality` | Qualità del dato |

Non è necessario implementare tutti questi campi il primo giorno. La struttura iniziale può essere più semplice, ma è importante progettarla pensando già alle evoluzioni future.

L'uso di `station_id` è particolarmente importante. Anche se inizialmente verrà utilizzata una sola stazione, ogni osservazione dovrà essere associata a essa.

In futuro sarà quindi possibile confrontare, per esempio, `SECCHIA-01` e `SECCHIA-02`.

---

### 7. L'indice di biodiversità

Uno degli elementi più importanti del progetto sarà l'indice di biodiversità.

Non verrà utilizzato semplicemente il numero di specie osservate, perché questo valore da solo non descrive completamente la diversità.

Per esempio, immaginiamo di avere 100 osservazioni appartenenti a quattro specie.

Nel primo caso possiamo avere:

- specie A: 25 osservazioni;
- specie B: 25;
- specie C: 25;
- specie D: 25.

Nel secondo:

- specie A: 97 osservazioni;
- specie B: 1;
- specie C: 1;
- specie D: 1.

In entrambi i casi abbiamo quattro specie, ma il secondo ambiente osservato è molto più dominato da una singola specie.

Per rappresentare meglio questa differenza verrà utilizzato l'**indice di Shannon**:

**H' = − Σ pᵢ ln(pᵢ)**

dove `pᵢ` rappresenta la proporzione delle osservazioni appartenenti alla specie `i`.

Con quattro specie distribuite perfettamente in modo uniforme, l'indice è circa **1,39**.

Con 97 osservazioni di una specie e una sola osservazione per ciascuna delle altre tre, l'indice scende a circa **0,20**.

Questo permette alla dashboard di mostrare non solo quante specie sono state osservate, ma anche quanto le osservazioni siano distribuite tra le diverse specie.

L'indice dovrà però essere interpretato insieme al numero di osservazioni e al numero di specie.

La dashboard mostrerà quindi separatamente:

**Numero di osservazioni + numero di specie + indice di biodiversità osservata**

Inoltre il valore non dovrà essere confrontato tra periodi con quantità di dati completamente diverse senza indicarlo chiaramente.

Per questo sarà utile calcolare l'indice su finestre temporali standardizzate, ad esempio settimanali o mensili, mostrando sempre anche quante osservazioni sono state utilizzate per calcolarlo.

---

### 8. Affidabilità del riconoscimento

Un sistema automatico di riconoscimento non è infallibile.

BirdNET o iNaturalist possono produrre identificazioni errate, soprattutto quando il suono è disturbato, l'immagine è poco chiara o la specie è difficile da distinguere.

Per questo ogni osservazione dovrà avere un valore di **confidence**, cioè un'indicazione dell'affidabilità della previsione quando il servizio la fornisce.

Il sistema potrà poi classificare le osservazioni in base alla loro affidabilità.

Una possibile struttura è:

- identificazione automatica ad alta affidabilità;
- identificazione da verificare;
- osservazione verificata;
- osservazione esclusa.

Le soglie numeriche non dovranno essere inventate a priori. Verranno determinate durante i test del progetto, confrontando le identificazioni automatiche con immagini e registrazioni di cui la specie è già conosciuta.

In questo modo la squadra potrà dire ai giudici non semplicemente “l'AI funziona”, ma mostrare dati ottenuti dai propri test.

---

### 9. Gestione delle specie rare, protette e invasive

Il sistema potrà generare alert quando viene rilevata una specie particolarmente importante.

Non sarà però sufficiente scrivere manualmente che una specie è “rara”, “protetta” o “invasiva”.

Queste categorie dovranno essere basate su una lista di riferimento affidabile e aggiornata.

Nel database sarà quindi utile conservare anche la fonte utilizzata e la data dell'ultimo aggiornamento.

Quando il sistema identifica una specie di interesse, non dovrà automaticamente considerarla un rilevamento certo.

Il comportamento corretto sarà utilizzare due livelli di alert.

Il primo sarà qualcosa come:

**“Possibile rilevamento di specie di interesse — verifica necessaria.”**

Solo dopo una verifica si potrà trasformare l'evento in:

**“Rilevamento confermato.”**

Questa struttura riduce il rischio che un errore dell'intelligenza artificiale provochi un falso allarme.

È particolarmente importante perché un errore su una specie comune può essere poco significativo, mentre un falso positivo relativo a una specie invasiva o protetta può essere molto più problematico.

---

### 10. Effetto degli errori sull'indice

Anche gli errori di riconoscimento possono influenzare l'indice di biodiversità.

Se il sistema interpreta erroneamente un animale come appartenente a una specie che in realtà non era presente, quella falsa osservazione potrebbe alterare il valore dell'indice.

Per questo le osservazioni dubbie non dovranno essere trattate allo stesso modo delle osservazioni affidabili.

Una soluzione consiste nel mantenere il dato nel database, ma escluderlo dal calcolo dell'indice finché non raggiunge il livello di affidabilità necessario oppure non viene verificato.

In questo modo non si perde l'informazione originale e contemporaneamente si evita di contaminare automaticamente le analisi.

---

### 11. Dashboard

La dashboard sarà l'interfaccia principale attraverso cui verranno visualizzati i risultati.

Potrà essere sviluppata come applicazione web e pubblicata tramite Vercel.

La pagina principale dovrà essere semplice da leggere e non sovraccaricata di informazioni.

Dovrà mostrare almeno:

- osservazioni totali;
- specie osservate;
- indice di biodiversità osservata;
- andamento dell'indice nel tempo;
- ultime osservazioni;
- distribuzione delle specie;
- osservazioni audio e fotografiche;
- alert;
- specie rare/protette;
- specie invasive.

Un grafico potrà mostrare come cambia l'indice di Shannon nel tempo.

Un altro potrà mostrare la quantità di osservazioni per specie.

La dashboard dovrà aggiornarsi quando arrivano nuovi dati, così durante la demo sarà possibile vedere concretamente il risultato dell'elaborazione.

---

### 12. Più stazioni e sviluppo futuro

L'architettura dovrà essere progettata fin dall'inizio per supportare più stazioni.

Ogni stazione avrà un proprio identificativo, ad esempio:

`SECCHIA-01`

`SECCHIA-02`

`SECCHIA-03`

Ogni osservazione registrata nel database conterrà il relativo `station_id`.

Questo permetterà in futuro di confrontare diverse zone e capire, ad esempio, se una stazione registra una maggiore diversità rispetto a un'altra.

Con ulteriori sviluppi potranno essere aggiunti:

- coordinate GPS;
- mappa delle osservazioni;
- habitat;
- temperatura;
- umidità;
- orario dell'attività;
- andamento stagionale;
- confronto tra stazioni.

Queste funzioni non devono però essere considerate indispensabili per il primo prototipo.

---

### 13. Funzionamento offline e affidabilità

Il sistema dovrà essere progettato considerando anche la possibilità che Internet non sia disponibile.

La parte audio basata su BirdNET potrà essere eseguita localmente sul backend, evitando di dipendere completamente da un servizio cloud per ogni riconoscimento.

Per le fotografie, iNaturalist richiede invece la connessione.

Se Internet non è disponibile, l'immagine potrà essere messa in coda per una successiva elaborazione oppure potrà essere utilizzata la modalità dimostrativa con dati già preparati.

Il progetto dovrà quindi avere almeno tre situazioni operative:

**Modalità live:** dati reali elaborati in tempo reale.

**Modalità locale/fallback:** elaborazione tramite il computer del team quando il servizio online non è disponibile.

**Modalità demo:** dataset preparato in anticipo per garantire una presentazione funzionante.

Questa ridondanza è importante soprattutto durante la gara.

---

### 14. Infrastruttura online

Supabase verrà utilizzato per database e gestione dei dati.

Il backend FastAPI potrà essere pubblicato su Render.

La dashboard potrà essere pubblicata su Vercel.

GitHub verrà utilizzato per conservare il codice e mantenere lo storico delle modifiche.

Il Mac del team rimarrà comunque molto utile per lo sviluppo e come ambiente locale di emergenza.

Il piano gratuito di Render può avere tempi di risveglio quando il servizio è inattivo. Durante lo sviluppo questo non rappresenta necessariamente un problema, ma prima dell'evento sarà necessario verificare concretamente i tempi.

Se la demo richiederà una risposta immediata e il piano gratuito risultasse troppo lento, sarà possibile valutare un piano a pagamento solamente nella fase finale.

---

### 15. Test del sistema

Prima di collegare tutta la parte elettronica sarà fondamentale testare separatamente il software.

Il backend dovrà essere provato con file audio e immagini già conosciuti.

Per esempio, si potranno preparare almeno 20 registrazioni audio di specie note e 20 immagini di specie note.

Il sistema dovrà essere utilizzato per verificare quante identificazioni risultano corrette.

Si potrà quindi calcolare una percentuale di riconoscimento:

**accuratezza = identificazioni corrette / identificazioni totali × 100**

Non sarà necessario ottenere il 100%.

È più importante conoscere realmente il comportamento del sistema e dichiararne i limiti.

I test dovranno inoltre verificare cosa succede con:

- audio rumoroso;
- immagini poco nitide;
- più animali;
- specie simili;
- dati incompleti;
- assenza di Internet;
- identificazioni a bassa affidabilità.

Questi test serviranno anche per scegliere le soglie di affidabilità utilizzate dal sistema.

---

### 16. Obiettivo del primo prototipo

Il progetto è abbastanza grande e deve quindi essere sviluppato in maniera progressiva.

Il primo obiettivo non sarà creare subito il sistema definitivo.

Il **MVP**, cioè la versione minima funzionante, dovrà dimostrare questa catena:

**raccolta del dato → riconoscimento → database → dashboard → indice → alert**

Il prototipo dovrà riuscire a gestire sia immagini sia audio, almeno in una forma iniziale.

Una volta che questa catena funzionerà, sarà possibile aggiungere funzioni più avanzate.

Tra queste potranno rientrare il supporto a più stazioni, la mappa, la verifica manuale, le notifiche reali e una gestione offline più avanzata.

Se il tempo non sarà sufficiente, queste funzioni potranno essere sacrificate senza compromettere il cuore del progetto.

---

### 17. Organizzazione del lavoro

La parte di programmazione potrà essere sviluppata principalmente con l'aiuto dell'intelligenza artificiale, per esempio tramite Claude Code.

L'AI potrà occuparsi della scrittura e modifica del codice, della configurazione del backend, dell'integrazione con le API, del database, della dashboard e dell'integrazione tra hardware e software.

La squadra dovrà comunque comprendere il funzionamento del sistema.

Durante la presentazione i membri non dovranno necessariamente saper scrivere il codice a memoria, ma dovranno essere in grado di spiegare:

- perché è stato scelto un ESP32;
- perché servono database e backend;
- come arriva il dato dalla stazione alla dashboard;
- cosa fanno BirdNET e iNaturalist;
- perché viene utilizzato l'indice di Shannon;
- cosa significa confidence;
- perché gli alert devono poter essere verificati;
- perché una singola stazione non rappresenta tutta la biodiversità della Riserva;
- come il sistema potrebbe essere esteso a più stazioni.

Riccardo potrà occuparsi in particolare dell'assemblaggio hardware, dell'organizzazione del lavoro e della comprensione dell'architettura, mentre l'intero team dovrà conoscere il funzionamento generale del progetto.

---

### 18. Budget

Il progetto dispone di un budget di circa **3000 €**, ma non è necessario spenderlo tutto.

La parte hardware del prototipo dovrebbe richiedere solamente una piccola parte del budget, indicativamente circa **100 €** per componenti aggiuntivi, considerando che il team dispone già di Mac, tablet Samsung, Arduino Uno, stampante 3D e laser cutter.

Il budget potrà quindi essere conservato per eventuali componenti aggiuntivi, sensori, miglioramenti della stazione o servizi necessari nella fase finale.

È preferibile avere un prototipo semplice ma realmente funzionante piuttosto che spendere molto denaro per una struttura complessa che non aggiunge valore al funzionamento del sistema.

---

### 19. Account e strumenti da preparare

Per iniziare lo sviluppo sarà necessario predisporre gli account dei servizi utilizzati:

**GitHub** per il codice e il versionamento.

**Supabase** per il database.

**Render** per il backend.

**Vercel** per la dashboard.

**iNaturalist** per il riconoscimento fotografico tramite API.

**BirdNET** per il riconoscimento audio.

Poiché i componenti del team sono minorenni, per alcuni servizi potrebbero essere necessari account scolastici, autorizzazioni o il coinvolgimento di un adulto. Questo deve essere verificato prima di iniziare la configurazione definitiva.

---

### 20. Cosa deve essere pronto nei primi mesi

Nella prima fase bisogna concentrarsi esclusivamente sul funzionamento software.

Il primo risultato concreto dovrà essere un database funzionante e un backend capace di ricevere dati.

Successivamente si dovrà ottenere il primo riconoscimento fotografico tramite iNaturalist e il primo riconoscimento audio tramite BirdNET.

Quando questi componenti funzioneranno separatamente, dovranno essere collegati al database.

A quel punto si potrà costruire la dashboard.

Solo dopo che questa catena software sarà stabile sarà conveniente collegare definitivamente la parte hardware.

Questo approccio evita di avere contemporaneamente problemi di elettronica, programmazione, API e database senza sapere quale componente sta causando l'errore.

---

### 21. Evoluzione verso il prototipo completo

Una volta funzionante il sistema software, si passerà alla stazione fisica.

L'ESP32 dovrà acquisire il dato e inviarlo al backend.

Il PIR potrà essere utilizzato per simulare il rilevamento dell'animale durante la presentazione.

Il contenitore verrà progettato in modo da rendere visibili i componenti importanti senza necessariamente nasconderli completamente.

La stazione dovrà avere un aspetto sufficientemente realistico da comunicare l'idea di una vera fototrappola, ma allo stesso tempo dovrà permettere ai giudici di capire facilmente come funziona.

---

### 22. Cosa non bisogna promettere

Monitor Secchia non deve essere presentato come un sistema capace di identificare qualsiasi animale con certezza assoluta.

L'identificazione automatica ha dei limiti.

Non bisogna nemmeno dire che il valore dell'indice di Shannon rappresenta automaticamente tutta la biodiversità della Cassa di espansione del Secchia.

Il sistema misura la biodiversità presente **nelle osservazioni raccolte dalle stazioni**.

Non bisogna inoltre promettere che ogni rilevamento di specie rara, protetta o invasiva genererà automaticamente una comunicazione a un ente esterno.

Il sistema deve prima prevedere l'eventuale verifica e qualsiasi meccanismo di notifica esterna dovrebbe essere implementato solo se effettivamente previsto dal progetto.

Questa precisione rende il progetto più scientificamente corretto e più credibile davanti ai giudici.

---

### 23. Perché il progetto è più di un insieme di API

Un punto importante della presentazione sarà spiegare che il valore di Monitor Secchia non è semplicemente aver collegato BirdNET e iNaturalist.

Il progetto integra diversi livelli:

**Raccolta:** il sistema acquisisce immagini e suoni.

**Identificazione:** l'AI cerca di riconoscere la specie.

**Valutazione:** viene associata un'affidabilità al risultato.

**Organizzazione:** l'osservazione viene salvata in un database strutturato.

**Analisi:** i dati vengono trasformati in statistiche e nell'indice di Shannon.

**Controllo:** le identificazioni importanti possono essere sottoposte a verifica.

**Allerta:** il sistema segnala le specie di interesse.

**Visualizzazione:** una dashboard rende i risultati comprensibili.

**Espansione:** l'architettura permette di aggiungere più stazioni.

È proprio questa integrazione a trasformare una semplice funzione di riconoscimento in un sistema di monitoraggio.

---

### 24. Struttura finale del sistema

Quando il progetto sarà completo, l'architettura dovrà essere concettualmente questa:

**STAZIONE MONITOR SECCHIA**

ESP32  
→ camera  
→ microfono  
→ sensore PIR  
→ Wi-Fi

↓

**BACKEND FASTAPI**

ricezione dati  
→ analisi audio con BirdNET  
→ analisi immagini con iNaturalist  
→ confidence  
→ classificazione  
→ verifica  
→ salvataggio

↓

**SUPABASE**

osservazioni  
→ specie  
→ stazione  
→ data/ora  
→ metodo  
→ affidabilità  
→ stato verifica  
→ dati aggiuntivi

↓

**ELABORAZIONE**

numero osservazioni  
→ numero specie  
→ indice Shannon  
→ andamento temporale  
→ specie di interesse  
→ alert

↓

**DASHBOARD**

grafici  
→ osservazioni  
→ specie  
→ biodiversità osservata  
→ alert  
→ dati delle stazioni

Questa struttura deve essere il riferimento principale durante lo sviluppo.

---

### 25. Risultato finale previsto

Il risultato finale sarà una piccola stazione di monitoraggio collegata a un sistema digitale capace di trasformare immagini e suoni in osservazioni organizzate.

Il sistema potrà riconoscere le specie attraverso strumenti di intelligenza artificiale, registrare i dati, associare un livello di affidabilità, analizzare la distribuzione delle specie e calcolare l'indice di biodiversità osservata.

Quando viene identificata una specie di interesse, il sistema potrà generare un alert, distinguendo le possibili identificazioni da quelle confermate.

La stessa architettura potrà essere estesa da una singola stazione a una rete di stazioni, permettendo in futuro di confrontare diverse zone.

Il progetto dovrà quindi essere presentato non come una semplice fototrappola intelligente, ma come una **piattaforma di monitoraggio della biodiversità osservata**, nella quale hardware, intelligenza artificiale, database, analisi dei dati e interfaccia web lavorano insieme.

### Primo obiettivo operativo

Per iniziare concretamente il lavoro, la priorità assoluta è costruire la prima versione software senza aspettare l'hardware.

La prima catena da rendere funzionante è:

**file audio/foto di prova → backend → riconoscimento → Supabase → dashboard**

Quando questa parte funziona, si aggiungeranno l'indice di Shannon e gli alert. Successivamente verrà collegata la stazione ESP32 e infine verranno effettuati i test completi.

In questo modo il progetto viene costruito dal nucleo funzionante verso il prototipo fisico, riducendo il rischio di arrivare alla fine con un modello esteticamente completo ma senza un sistema realmente funzionante.