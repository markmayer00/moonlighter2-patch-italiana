<p align="center">
  <img src="src/banner.png" alt="Moonlighter 2: The Endless Vault — traduzione italiana" width="900">
</p>

<p align="center">
  <a href="../../releases/latest"><img alt="Ultima versione" src="https://img.shields.io/github/v/release/markmayer00/moonlighter2-patch-italiana?label=versione&color=b9873a&cacheSeconds=1800"></a>
  <a href="../../releases"><img alt="Download" src="https://img.shields.io/github/downloads/markmayer00/moonlighter2-patch-italiana/total?label=download&color=b9873a&cacheSeconds=1800"></a>
  <img alt="Copertura" src="https://img.shields.io/badge/tradotto-100%25-1f6f52&cacheSeconds=1800">
  <a href="LICENSE"><img alt="Licenza del codice" src="https://img.shields.io/badge/codice-MIT-666"></a>
</p>

<p align="center">
  <a href="https://github.com/markmayer00/moonlighter2-patch-italiana/releases/latest/download/PatchItaliana_Moonlighter2.zip"><img src="src/bottone-download.png" alt="Scarica la patch" width="280"></a>
</p>

<p align="center">
  <sub>Windows · 25 MB · sempre l'ultima versione</sub><br>
  <sub>
    <a href="https://github.com/markmayer00/moonlighter2-patch-italiana/releases/latest/download/PatchItaliana_Moonlighter2_cartella.zip">versione cartella</a>, se l'antivirus blocca ·
    <a href="../../releases">tutte le versioni</a>
  </sub>
</p>

# Patch Italiana — Moonlighter 2: The Endless Vault

Riporta la traduzione italiana sulla versione **1.0** del gioco, dove quella
originale ha smesso di funzionare, e aggiunge una voce **Italiano** nel menu
delle lingue.

> **La traduzione è opera dei TWR — autore PolyZen**, e questa patch è
> pubblicata con il suo consenso.
> Il 92% delle stringhe viene parola per parola dal loro lavoro.
> Idea e realizzazione della patch per la 1.0: **MarkMayer**.
> Dettagli in [CREDITI.txt](CREDITI.txt).

**Copertura: 100%** — tutte le 5.828 stringhe di testo del gioco.
(Le altre 4 righe della tabella sono celle vuote o segnaposto degli
sviluppatori, lasciate in bianco anche dalle altre lingue.)

---

## "Windows ha protetto il PC"

È SmartScreen, e non significa che sia stato trovato un virus: avvisa per
qualsiasi programma che non abbia ancora una reputazione, cioè tutti quelli non
firmati con un certificato di code signing a pagamento. Premi **Ulteriori
informazioni → Esegui comunque**.

Se preferisci non fidarti di un eseguibile, il codice è tutto qui e puoi
ricompilarlo da solo in due minuti: vedi *Compilare dai sorgenti*.

## Come si usa

**Prima di estrarre:** clic destro sullo zip scaricato → Proprietà → spunta
**"Annulla blocco"** in basso → OK. Windows marca tutto quello che arriva da
internet e il marchio passa ai file estratti; togliendolo prima, l'avviso di
SmartScreen di solito non compare.

1. Doppio clic su `PatchItaliana_Moonlighter2.exe`
2. Il programma cerca il gioco da solo; se non lo trova, premi **Sfoglia...**
3. Premi **APPLICA LA TRADUZIONE**
4. Nel gioco: Impostazioni → Lingua → **Italiano**

Per tornare indietro c'è il pulsante **Ripristina**. Un backup del file
originale (`data.unity3d.orig`) viene creato in automatico alla prima
esecuzione, e viene rifatto da solo quando il gioco si aggiorna — così
riapplicare la patch non riporta mai indietro il bundle.

Funziona con qualsiasi copia PC della 1.0, Steam compresa. Attenzione: la
*verifica integrità dei file* di Steam rimette i file originali, e la patch va
riapplicata.

## Perché "al posto del Polacco"

Il gioco ha un numero fisso di lingue e non se ne possono aggiungere. Quello
che si può fare è riempire di italiano una lingua esistente e rinominare la sua
voce di menu in "Italiano". Di serie viene usato il polacco; dal menu a tendina
si può scegliere un'altra lingua da sostituire. Le altre restano intatte.

---

## Come funziona

I testi del gioco stanno tutti in un unico oggetto Unity `Gridly.Project`: una
tabella con una riga per stringa e una colonna per lingua. La patch scrive
l'italiano in una di quelle colonne e rinomina la voce corrispondente nel menu.

Gli identificativi delle righe non sono cambiati fra Early Access e 1.0, quindi
i testi si trasferiscono riga per riga senza ritradurre nulla.

Spiegazione estesa: **[docs/come-funziona.md](docs/come-funziona.md)**

## Compilare dai sorgenti

Serve Python 3.10+.

```bash
python -m venv .venv
.venv\Scripts\pip install UnityPy pyinstaller

# versione da riga di comando
.venv\Scripts\python src\ml2_patch_it.py "<cartella _Data del gioco>"
.venv\Scripts\python src\ml2_patch_it.py "<cartella _Data>" --lingua ptBR
.venv\Scripts\python src\ml2_patch_it.py "<cartella _Data>" --ripristina

# eseguibile con interfaccia
.venv\Scripts\pyinstaller --onefile --windowed ^
  --name PatchItaliana_Moonlighter2 ^
  --add-data "src\italiano.json.gz;." --add-data "src\banner.png;." ^
  --hidden-import chiptune --hidden-import winsound ^
  --collect-submodules UnityPy src\ml2_patch_gui.py
```

Compila **sempre da un ambiente virtuale pulito**: da un Python con molti
pacchetti installati, PyInstaller trascina dentro di tutto e l'eseguibile passa
da 24 MB a oltre 300.

### Il file dei testi

`src/italiano.json.gz` contiene le 5.826 stringhe italiane, incluse qui con il
consenso di PolyZen. Restano lavoro dei TWR e non sono coperte dalla licenza
del codice.

## Contenuto

| percorso | cosa fa |
|---|---|
| `src/ml2_patch_gui.py` | il programma con interfaccia |
| `src/ml2_patch_it.py` | versione da riga di comando |
| `src/chiptune.py` | la musica, sintetizzata a ogni avvio |
| `src/banner.png` | l'immagine dell'intestazione |
| `src/italiano.json.gz` | le 5.826 stringhe italiane |
| `docs/come-funziona.md` | com'è stata fatta la conversione |

---

## Licenza

Il **codice** di questo repository è rilasciato sotto licenza MIT — vedi
[LICENSE](LICENSE).

La **traduzione italiana non è coperta da questa licenza**: appartiene ai TWR.
La licenza MIT si applica esclusivamente agli script di conversione.

Moonlighter 2: The Endless Vault è di Digital Sun e 11 bit studios. Questa è
una patch amatoriale non ufficiale, senza alcun legame con loro.
