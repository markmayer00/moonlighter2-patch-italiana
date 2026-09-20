# Cosa è cambiato

Le versioni sono elencate dalla più recente. Quando una versione tocca i testi
del gioco è segnalato: in quel caso conviene riapplicare la patch.

---

## v1.1.2

**Correzione di una stringa** — tocca i testi, conviene riapplicare.

- Nel menu del baule del negozio la voce *"Progressione Del Mercante."* aveva un
  punto finale che le altre voci non hanno, e che non c'è nemmeno nell'inglese
  *Merchant Progression*. La preposizione era maiuscola, mentre nel resto della
  traduzione è minuscola. Ora si legge **"Progressione del Mercante"**
- Prima segnalazione arrivata dalle Issues ([#1](../../issues/1))

---

## v1.1.1

**Dove segnalare i problemi**

- Aggiunto un modulo di segnalazione: chiede versione della patch, da dove viene
  la copia del gioco e quale lingua è stata sostituita, così non serve chiedere
  ogni volta le stesse cose
- Collegamento al [Discord dei TWR](https://discord.gg/85ayAcHRfH), il posto
  giusto per parlare dei testi
- I due collegamenti compaiono nella finestra del programma, nel README e nel
  LEGGIMI

---

## v1.1.0

**Il backup non riporta più indietro il gioco** — la correzione più importante
finora.

- Fino alla v1.0.2, se il gioco veniva aggiornato e poi si riapplicava la patch,
  il patcher ripartiva dal backup della versione **vecchia**: il bundle tornava
  indietro, insieme agli altri file già aggiornati. Ora ogni patch registra
  l'impronta del file prodotto e, se al giro dopo non corrisponde, riconosce
  l'aggiornamento e rifà il backup sulla versione installata
- Anche **Ripristina** riporta alla versione del gioco che hai davvero installato
- Non serve più cancellare `data.unity3d.orig` a mano dopo un aggiornamento
- La musica parte spenta: chi la vuole mette la spunta su *♪ Musica*
- Corretto un file del gioco lasciato aperto dal programma, che impediva di
  rigenerare il backup senza prima chiudere tutto

---

## v1.0.2

**Accenti mancanti** — tocca i testi, conviene riapplicare.

- Il font del gioco non contiene le lettere **ì** e **ò**: nessuna delle lingue
  previste dagli sviluppatori le usa — il francese ha à è ù, lo spagnolo í ó, il
  tedesco ä ö ü — e solo l'italiano ha bisogno della i e della o con accento
  grave. Dove comparivano si vedeva un quadratino vuoto: "Sì" diventava "S□",
  "Può" diventava "Pu□"
- Sono 414 occorrenze in 358 stringhe, sostituite con l'apostrofo: **Si'**,
  **puo'**, **cosi'**, **pero'**. Tutte le altre lettere accentate erano e
  restano corrette
- Segnalato dagli utenti su Discord

---

## v1.0.1

**Ricerca del gioco** — dalle segnalazioni dei primi utenti.

- La ricerca si può interrompere: durante la scansione il pulsante diventa
  *Interrompi ricerca*. Segnalato da **PolyZen**, che con 7 dischi vedeva la
  ricerca proseguire all'infinito dopo aver già indicato la cartella a mano
- Scegliere la cartella con *Sfoglia* ferma la ricerca in corso
- Niente più giochi sbagliati: prima venivano proposte tutte le installazioni
  Unity presenti sul computer. Ora viene letto `app.info`, il file da poche
  decine di byte che ogni build Unity porta con sé, e vengono proposte solo le
  copie di Moonlighter 2. Segnalato da **Floro**
- Le lettere dei dischi fissi vengono enumerate davvero, invece di provare
  sempre da C a H

---

## v1.0

**Prima versione pubblica.**

- Riporta la traduzione dei TWR sulla versione 1.0 del gioco, dove quella
  originale aveva smesso di funzionare perché i testi sono finiti dentro
  `data.unity3d`
- Aggiunge una voce **Italiano** nel menu delle lingue: l'inglese resta inglese
- Tradotte le 365 stringhe introdotte dalla 1.0, che nella Early Access non
  esistevano — schede dei personaggi e del bestiario, i vantaggi *Bomba*, le
  armi della Gilda Dorata, i dialoghi del finale, le nuove impostazioni, i
  tutorial di Spark e del Blo-Burst
- Copertura: tutte le 5.828 stringhe di testo del gioco
- Trova l'installazione da solo, su Steam e non, anche su altri dischi
- Backup automatico e pulsante per tornare indietro
