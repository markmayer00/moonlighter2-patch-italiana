# Come è stata fatta la conversione

> La traduzione italiana di Moonlighter 2: The Endless Vault è opera dei **TWR**,
> autore **PolyZen**. Qui si racconta solo come è stata trasportata sulla nuova
> struttura del gioco.

## 1. Cosa è cambiato

Nella build Early Access i testi stavano in `resources.assets`, un file sciolto
dentro la cartella `_Data`. Sostituirlo bastava: il gioco lo leggeva e mostrava
l'italiano.

La 1.0 impacchetta tutto in un unico archivio, `data.unity3d`. Il vecchio
`resources.assets` resta sul disco ma il gioco non lo guarda più. Da qui
l'impressione che la traduzione andasse rifatta da capo.

Non era così: i testi erano ancora tutti utilizzabili, bisognava solo aprire il
contenitore nuovo.

## 2. Dove stanno i testi

Il gioco non usa TextAsset, né CSV, né Unity Localization. Usa **Gridly**, il
servizio di localizzazione di LocalizeDirect. Tutto il testo del gioco — ogni
stringa, in tutte le lingue — sta dentro *un solo oggetto*, di classe
`Gridly.Project`.

Ed è esattamente ciò che sembra a un traduttore: un foglio di calcolo.

| riga (ID) | enUS | esES | frFR | plPL | … |
|---|---|---|---|---|---|
| `ARMOR_EA-001_NAME` | Merchant's Clothes | Ropaje de comerciante | Habits de marchand | Strój kupca | … |
| `ENEMIES_BOSS_HERALD_NAME` | The Herald | El Heraldo | Le Héraut | Herold | … |
| `TUTORIAL_BASICS_01_TITLE` | ATTACK | ATACAR | ATTAQUER | ATAK | … |

Dodici schede — DUNGEON, SHOP, VENDORS, CURRENCIES, GADGETS, ARMORS, WEAPONS,
RELICS, UI, QUESTS, NARRATIVE, DEMO — per 5.832 righe e dieci colonne lingua,
più qualche colonna di servizio (Context, Character, Batch Date).

Nel file della Early Access l'italiano dei TWR sta nella colonna `enUS`: era
stato scritto sopra l'inglese, ed è per questo che nel gioco si sceglieva
"English" per giocare in italiano.

## 3. Aprire quell'oggetto

Qui c'è l'unico punto davvero ostico. Il gioco è compilato IL2CPP, quindi
nell'archivio non c'è la descrizione dei tipi: strumenti come UABEA vedono
l'oggetto ma non sanno leggerlo, e restituiscono un blocco di byte grezzi da
6 MB.

Quei byte però seguono una regola semplice, la stessa che Unity usa per
qualsiasi stringa serializzata:

```
4 byte    lunghezza della stringa (intero, little-endian)
N byte    la stringa in UTF-8
0-3 byte  riempimento fino al multiplo di 4
```

Seguendola dall'inizio del blocco, la struttura viene fuori da sola:

```
"Moonlighter2"          ← nome del progetto
  12                    ← quante schede
  "DUNGEON"  "99bt4zsvut8n9"
    601                 ← quante righe in questa scheda
    "ENEMIES_BOSS_HERALD_NAME"
      13                ← quante celle in questa riga
      "enUS" → "The Herald"
      "esES" → "El Heraldo"
      ...
    "Enemies/Houtu"     ← percorso della riga
```

### Il controllo che rende tutto sicuro

Prima di modificare qualunque cosa: leggere il blocco, riscriverlo senza
toccare niente, e confrontare i byte con l'originale. Se tornano identici — e
tornavano, su entrambi i file — allora lettore e scrittore sono corretti, e da
quel momento cambiare una cella non può corrompere il resto.

## 4. Il trasferimento

La parte che poteva rovinare tutto: se gli identificativi delle righe fossero
cambiati, l'abbinamento sarebbe saltato e sarebbe servito un confronto sui testi
inglesi, molto più fragile.

Non sono cambiati.

| | |
|---:|---|
| **5.377** | righe presenti in entrambe le versioni, stesso ID |
| **3** | righe sparite dalla Early Access |
| **453** | righe nuove introdotte dalla 1.0 |

Il trasferimento è quindi una copia riga per riga. Altre 87 righe hanno cambiato
ID ma hanno l'inglese identico a una riga già tradotta, e si sono recuperate
confrontando il testo originale.

Nessuna stringa è stata ritradotta o riscritta.

## 5. Le stringhe nuove

Restavano 365 stringhe con testo, introdotte dalla 1.0, senza un corrispondente
da cui pescare: schede dei personaggi e del bestiario, i vantaggi legati a
*Volatile*, le armi della Gilda Dorata, i dialoghi del finale, le nuove
impostazioni dei controller, i tutorial di Spark e del Blo-Burst.

Sono state tradotte seguendo il glossario dei TWR, estratto meccanicamente
dalle 5.171 coppie inglese/italiano già esistenti:

| inglese | italiano | | inglese | italiano |
|---|---|---|---|---|
| `Volatile` | Bomba | | `Perk` | Vantaggio |
| `Hex` | Maledizione | | `Perkmeter` | Vantaggiometro |
| `Wound` | Lacerazione | | `Tip` | Mancia |
| `Ignite` | Infiammato | | `Endless Vault` | Scrigno Eterno |
| `Tased` | Folgorato | | `Watcher` | Guardiano |
| `Foam` | Schiuma | | `Puppet` | Burattino |

Rispettate anche le convenzioni: i prefissi di battuta restano in inglese come
nei file originali (`The Vault:`, `Ms. Scratch:`, `Spark:`).

Prima di scrivere il file, un controllo automatico confronta segnaposto e
marcatori fra inglese e italiano — che `{0}` e `<b>` compaiano nello stesso
numero in entrambi. Ha già intercettato un `<b>` sbilanciato in una delle
stringhe nuove.

## 6. La voce "Italiano" nel menu

Il numero di lingue è fisso nel programma e non se ne possono aggiungere, ma
**il nome di ogni lingua è a sua volta una riga della tabella**. Si chiama
`MAINMENU_SETTINGS_LANGUAGE_CURRENT`, e ogni colonna contiene il nome della
propria lingua:

| enUS | esES | frFR | deDE | ptBR | **plPL** | jaJP |
|---|---|---|---|---|---|---|
| English | Español | Français | Deutsch | Português | **Italiano** | 日本語 |

Riempiendo la colonna `plPL` di italiano e scrivendo "Italiano" in quella cella,
nel menu compare una voce a sé — e l'inglese resta inglese.

Di serie viene sacrificato il polacco, perché è quello che a un giocatore
italiano serve meno, ma la lingua è scelta dall'utente. Le righe senza
traduzione prendono l'inglese, mai la lingua originale della colonna, così non
resta un ibrido.

Sui caratteri accentati nessun problema: il gioco usa un solo font per tutte le
lingue occidentali, `Metallophile Medium SDF`, che contiene già tutto quello che
serve all'italiano.

## 7. Al prossimo aggiornamento

Lo strumento non usa indirizzi fissi: cerca l'oggetto dei testi scansionando
l'archivio, quindi continua a funzionare anche se il gioco viene ricompilato e
tutto si sposta. Riparte sempre dalla copia di riserva del file originale, così
le modifiche non si accumulano mai.

Quando esce una patch del gioco, rimettere l'italiano richiede un minuto. Se la
patch aggiunge stringhe nuove, quelle restano in inglese finché non vengono
tradotte — niente si rompe.

---

## Dettagli tecnici

| | |
|---|---|
| Motore | Unity 6000.3.18f1, IL2CPP |
| Archivio | `data.unity3d`, UnityFS v8, blocchi LZ4HC |
| Oggetto dei testi | `Gridly.Project` (Assembly-CSharp), ~6 MB |
| Libreria usata | [UnityPy](https://github.com/K0lb3/UnityPy) per aprire e risalvare l'archivio |
| Parser del blob | scritto a mano: senza type tree UnityPy non può leggerlo |
