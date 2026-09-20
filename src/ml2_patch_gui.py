# -*- coding: utf-8 -*-
"""Patch Italiana per Moonlighter 2: The Endless Vault (v1.0).

Traduzione: TWR - autore PolyZen (originariamente per la build Early Access).
Questo programma la riporta sulla 1.0 e traduce le stringhe aggiunte nel frattempo.

I testi del gioco stanno tutti in un unico oggetto Unity `Gridly.Project`: una
tabella con una riga per stringa e una colonna per lingua. La patch scrive
l'italiano in una di quelle colonne e rinomina la voce corrispondente nel menu
delle lingue, cosi nel gioco compare "Italiano" come voce a se.
"""
import os, sys, gzip, json, struct, shutil, threading, collections
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

APP = "Patch Italiana - Moonlighter 2"
CREDITI = "Traduzione dei TWR - autore PolyZen"

# codice colonna -> etichetta nel menu a tendina
LINGUE = [
    ("plPL", "al posto del Polacco  (consigliato)"),
    ("ptBR", "al posto del Portoghese"),
    ("ruRU", "al posto del Russo"),
    ("jaJP", "al posto del Giapponese"),
    ("koKR", "al posto del Coreano"),
    ("zhCN", "al posto del Cinese"),
    ("deDE", "al posto del Tedesco"),
    ("frFR", "al posto del Francese"),
    ("esES", "al posto dello Spagnolo"),
    ("enUS", "al posto dell'Inglese"),
]
KEY_LANG_NAME = "UI|MAINMENU_SETTINGS_LANGUAGE_CURRENT"

def res_path(name):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)

# ------------------------------------------------------------------ Gridly
class Reader:
    def __init__(self, b, i=0): self.b, self.i = b, i
    def i32(self):
        v = struct.unpack_from("<i", self.b, self.i)[0]; self.i += 4; return v
    def align(self): self.i += (-self.i) % 4
    def string(self):
        n = self.i32()
        if n < 0 or self.i + n > len(self.b): raise ValueError("stringa non valida")
        s = self.b[self.i:self.i+n].decode("utf-8"); self.i += n; self.align(); return s

def parse(raw):
    r = Reader(raw, 28)
    mono, project = r.string(), r.string()
    grids = []
    for _ in range(r.i32()):
        a, name, b, gid = r.string(), r.string(), r.string(), r.string()
        recs = []
        for _ in range(r.i32()):
            rid = r.string(); cells = {}; order = []
            for _ in range(r.i32()):
                col, val = r.string(), r.string()
                cells[col] = val; order.append(col)
            recs.append({"id": rid, "path": r.string(), "cells": cells, "order": order})
        grids.append({"name": name, "id": gid, "a": a, "b": b, "records": recs})
    return {"mono_name": mono, "project": project, "grids": grids, "consumed": r.i}

def wstr(s):
    b = s.encode("utf-8"); out = struct.pack("<i", len(b)) + b
    return out + b"\x00" * ((-len(out)) % 4)

def serialize(d, header, tail):
    o = [header, wstr(d["mono_name"]), wstr(d["project"]), struct.pack("<i", len(d["grids"]))]
    for g in d["grids"]:
        o += [wstr(g["a"]), wstr(g["name"]), wstr(g["b"]), wstr(g["id"]),
              struct.pack("<i", len(g["records"]))]
        for r in g["records"]:
            o += [wstr(r["id"]), struct.pack("<i", len(r["order"]))]
            for c in r["order"]:
                o += [wstr(c), wstr(r["cells"][c])]
            o.append(wstr(r["path"]))
    o.append(tail)
    return b"".join(o)

def find_project(path):
    import UnityPy
    env = UnityPy.load(path)
    best = None
    for o in env.objects:
        if o.type.name != "MonoBehaviour":
            continue
        raw = o.get_raw_data()
        if len(raw) < 1_000_000:
            continue
        try:
            d = parse(raw)
        except Exception:
            continue
        if d["project"] and d["grids"]:
            if best is None or len(raw) > len(best[1].get_raw_data()):
                best = (env, o, d)
    if best is None:
        raise RuntimeError("Asset dei testi non trovato. Versione del gioco non supportata?")
    return best

def carica_italiano():
    with gzip.open(res_path("italiano.json.gz"), "rb") as f:
        data = json.loads(f.read().decode("utf-8"))
    data.pop("_meta", None)
    return data

# ------------------------------------------------------------------ ricerca automatica
def steam_paths():
    """Tutte le librerie Steam: registro + libraryfolders.vdf (anche su altri dischi)."""
    import re as _re
    bases = []
    try:
        import winreg
        for hive, key, val in ((winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam", "SteamPath"),
                               (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam", "InstallPath"),
                               (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam", "InstallPath")):
            try:
                with winreg.OpenKey(hive, key) as k:
                    bases.append(winreg.QueryValueEx(k, val)[0].replace("/", "\\"))
            except OSError:
                pass
    except ImportError:
        pass
    bases += [r"C:\Program Files (x86)\Steam", r"C:\Program Files\Steam", r"C:\Steam"]

    libs, seen = [], set()
    for b in bases:
        if not b or not os.path.isdir(b):
            continue
        found = [b]
        vdf = os.path.join(b, "steamapps", "libraryfolders.vdf")
        if os.path.isfile(vdf):
            try:
                txt = open(vdf, encoding="utf-8", errors="ignore").read()
                found += [p.replace("\\\\", "\\") for p in _re.findall(r'"path"\s+"([^"]+)"', txt)]
            except OSError:
                pass
        for p in found:
            common = os.path.join(p, "steamapps", "common")
            if os.path.isdir(common) and common.lower() not in seen:
                seen.add(common.lower()); libs.append(common)
    return libs

def dischi_fissi():
    """Lettere dei soli dischi fissi presenti: niente CD, chiavette o unita' di rete."""
    import string
    out = []
    try:
        import ctypes
        for L in string.ascii_uppercase:
            r = f"{L}:\\"
            if ctypes.windll.kernel32.GetDriveTypeW(ctypes.c_wchar_p(r)) == 3:  # DRIVE_FIXED
                out.append(L)
    except Exception:
        out = [L for L in string.ascii_uppercase if os.path.isdir(f"{L}:\\")]
    return out

def candidate_roots():
    roots, seen = [], set()
    def add(p):
        if p and os.path.isdir(p) and p.lower() not in seen:
            seen.add(p.lower()); roots.append(p)
    for p in steam_paths():
        add(p)
    for p in (r"C:\Program Files\Epic Games", r"C:\Program Files (x86)\Epic Games",
              r"C:\XboxGames", r"C:\GOG Games", r"C:\Program Files (x86)\GOG Galaxy\Games",
              r"C:\Games", r"C:\Giochi"):
        add(p)
    home = os.path.expanduser("~")
    for sub in ("Downloads", "Desktop", "Documents", "Games", "Giochi"):
        add(os.path.join(home, sub))
    dischi = dischi_fissi()
    for drive in dischi:
        for sub in ("SteamLibrary", "Games", "Giochi", "Epic Games", "XboxGames", "GOG Games"):
            add(f"{drive}:\\{sub}")
    for drive in dischi:
        add(f"{drive}:\\")
    return roots

SKIP_DIRS = {"windows", "appdata", "$recycle.bin", "system volume information",
             "programdata", "node_modules", "onedrive"}

def e_moonlighter(dirpath, filenames):
    """Distingue Moonlighter 2 dagli altri giochi Unity.

    Ogni build Unity ha un app.info di poche decine di byte con dentro
    l'editore e il nome del prodotto: qui e' "11BitStudios / Moonlighter 2
    The Endless Vault". Senza quello ci si affida al nome della cartella o
    dell'eseguibile che sta accanto.
    """
    if "app.info" in filenames:
        try:
            with open(os.path.join(dirpath, "app.info"), encoding="utf-8", errors="ignore") as f:
                return "moonlighter" in f.read(400).lower()
        except OSError:
            pass
    if "moonlighter" in os.path.basename(dirpath).lower():
        return True
    try:
        padre = os.path.dirname(dirpath)
        return any(f.lower().endswith(".exe") and "moonlighter" in f.lower()
                   for f in os.listdir(padre))
    except OSError:
        return False

def looks_like_game(dirpath, filenames, dirnames):
    return (os.path.basename(dirpath).endswith("_Data")
            and "data.unity3d" in filenames
            and ("il2cpp_data" in dirnames or "StreamingAssets" in dirnames)
            and e_moonlighter(dirpath, filenames))

def scan_game_dirs(progress=lambda s: None, want=8, stop=None):
    """Cerca le installazioni. `stop` e' un threading.Event: se scatta, si ferma."""
    def fermare():
        return stop is not None and stop.is_set()
    trovati, seen = [], set()
    for root in candidate_roots():
        if len(trovati) >= want or fermare():
            break
        progress(f"Cerco in {root} ...")
        depth_root = root.rstrip("\\").count(os.sep)
        limit = 6 if len(root) > 3 else 4
        for dirpath, dirnames, filenames in os.walk(root, topdown=True):
            if fermare():
                dirnames[:] = []
                break
            if dirpath.count(os.sep) - depth_root > limit:
                dirnames[:] = []
                continue
            dirnames[:] = [x for x in dirnames
                           if x.lower() not in SKIP_DIRS and not x.startswith("$")]
            if looks_like_game(dirpath, filenames, dirnames):
                key = os.path.normcase(dirpath)
                if key in seen:
                    continue
                seen.add(key)
                trovati.append(dirpath)
    return trovati

# ------------------------------------------------------------------ backup
def impronta(path, blocco=1 << 20):
    """SHA-256 di un file, letto a blocchi."""
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(blocco)
            if not b:
                break
            h.update(b)
    return h.hexdigest()

def contiene_italiano(path):
    """Apre il bundle e guarda se una delle lingue e' gia' stata tradotta.

    Il file viene letto in memoria invece che aperto per percorso: UnityPy
    terrebbe l'handle aperto e la copia del backup fallirebbe.
    """
    try:
        with open(path, "rb") as f:
            _, _, d = find_project(f.read())
    except Exception:
        return False
    for g in d["grids"]:
        for r in g["records"]:
            if r["id"] == "MAINMENU_SETTINGS_LANGUAGE_CURRENT":
                return "Italiano" in r["cells"].values()
    return False

def prepara_backup(data_dir, log):
    """Garantisce un backup che corrisponda alla versione del gioco installata ORA.

    Il patcher riparte sempre dal backup: se il gioco viene aggiornato e il
    backup resta quello vecchio, riapplicare la patch riporterebbe indietro il
    bundle. Per evitarlo ogni patch registra l'impronta del file prodotto; se
    al giro dopo data.unity3d non e' piu' quello, il gioco e' stato aggiornato
    e il backup va rifatto.
    """
    dst = os.path.join(data_dir, "data.unity3d")
    orig = os.path.join(data_dir, "data.unity3d.orig")
    info = os.path.join(data_dir, "data.unity3d.patchinfo")

    if not os.path.isfile(orig):
        log("Creo il backup (data.unity3d.orig) ...")
        shutil.copy2(dst, orig)
        return

    attuale = impronta(dst)
    registrato = None
    if os.path.isfile(info):
        try:
            with open(info, encoding="utf-8") as f:
                registrato = json.load(f).get("prodotto")
        except (OSError, ValueError):
            registrato = None

    if registrato is not None:
        valido = (attuale == registrato)
    elif attuale == impronta(orig):
        valido = True                 # il gioco non e' patchato: il backup e' una copia fedele
    else:
        log("Controllo se il gioco e' gia' tradotto ...")
        valido = contiene_italiano(dst)

    if valido:
        log("Backup verificato, riparto da quello.")
    else:
        log("Il gioco e' stato aggiornato: il vecchio backup non vale piu'.")
        log("Ne creo uno nuovo dalla versione installata adesso.")
        shutil.copy2(dst, orig)

def registra_patch(data_dir):
    """Annota cosa ha prodotto il patcher, per riconoscere un aggiornamento del gioco."""
    info = os.path.join(data_dir, "data.unity3d.patchinfo")
    try:
        with open(info, "w", encoding="utf-8") as f:
            json.dump({"prodotto": impronta(os.path.join(data_dir, "data.unity3d")),
                       "nota": "impronta del file scritto dalla patch italiana; "
                               "se non corrisponde, il gioco e' stato aggiornato"},
                      f, indent=1)
    except OSError:
        pass

# ------------------------------------------------------------------ patch
def do_patch(data_dir, target, log):
    """Scrive l'italiano nella colonna `target` e rinomina quella voce di menu."""
    dst = os.path.join(data_dir, "data.unity3d")
    orig = os.path.join(data_dir, "data.unity3d.orig")
    if not os.path.isfile(dst):
        raise RuntimeError(f"Non trovo data.unity3d in:\n{data_dir}")
    prepara_backup(data_dir, log)

    it = carica_italiano()
    log(f"Testi italiani caricati: {len(it)} voci.")

    log("Apro i file del gioco ...")
    with open(orig, "rb") as f:            # in memoria: l'handle non deve restare aperto
        env, obj, d = find_project(f.read())
    raw = obj.get_raw_data()
    header, tail = raw[:28], raw[d["consumed"]:]

    cols = set()
    for g in d["grids"]:
        for r in g["records"]:
            cols.update(r["cells"])
    if target not in cols:
        raise RuntimeError(f"La lingua {target} non esiste in questa versione del gioco.\n"
                           f"Disponibili: {', '.join(sorted(c for c in cols if len(c) == 4))}")

    stat = collections.Counter()
    for g in d["grids"]:
        for r in g["records"]:
            if target not in r["cells"]:
                continue
            k = f"{g['name']}|{r['id']}"
            if k in it:
                r["cells"][target] = it[k]; stat["italiano"] += 1
            else:
                # nessuna traduzione: meglio l'inglese che la lingua originale della colonna
                r["cells"][target] = r["cells"].get("enUS", r["cells"][target])
                stat["inglese"] += 1

    tot = sum(stat.values())
    log(f"Tradotte {stat['italiano']} stringhe su {tot} "
        f"({stat['italiano']*100/tot:.1f}%).")

    new_raw = serialize(d, header, tail)
    chk = parse(new_raw)
    if chk["consumed"] + len(tail) != len(new_raw):
        raise RuntimeError("Errore interno di riserializzazione: niente e stato modificato.")
    if sum(len(g["records"]) for g in chk["grids"]) != sum(len(g["records"]) for g in d["grids"]):
        raise RuntimeError("Conteggio righe alterato: niente e stato modificato.")

    log("Scrivo i file del gioco (puo richiedere un minuto) ...")
    obj.set_raw_data(new_raw)
    with open(dst, "wb") as f:
        f.write(env.file.save(packer="original"))
    registra_patch(data_dir)
    log("FATTO. Nel gioco vai in Impostazioni e scegli la lingua ITALIANO.")

def do_restore(data_dir, log):
    dst = os.path.join(data_dir, "data.unity3d")
    orig = os.path.join(data_dir, "data.unity3d.orig")
    if not os.path.isfile(orig):
        raise RuntimeError("Backup non trovato: non c'e nulla da ripristinare.")
    shutil.copy2(orig, dst)
    info = os.path.join(data_dir, "data.unity3d.patchinfo")
    if os.path.isfile(info):
        try:
            os.remove(info)
        except OSError:
            pass
    log("Ripristinati i file originali del gioco.")

# ------------------------------------------------------------------ GUI
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP)
        self.geometry("800x680")
        self.minsize(740, 600)
        self.busy = False
        self.scanning = False
        self.stop_scan = threading.Event()
        pad = {"padx": 10, "pady": 6}

        self.banner_src = None
        self.banner_img = None
        self._banner_w = 0
        self.banner_lbl = tk.Label(self, bd=0, highlightthickness=0)
        self._banner_job = None
        if self.load_banner():
            self.banner_lbl.pack(fill="x", side="top")
            self.bind("<Configure>", self.fit_banner)
        else:
            ttk.Label(self, text="Patch Italiana per Moonlighter 2: The Endless Vault",
                      font=("Segoe UI", 13, "bold")).pack(anchor="w", **pad)
        ttk.Label(self, text=CREDITI + "   ·   patch per la 1.0: MarkMayer",
                  foreground="#666").pack(anchor="w", padx=10, pady=(8, 0))

        f1 = ttk.LabelFrame(self, text="Cartella del gioco")
        f1.pack(fill="x", **pad)
        self.var_game = tk.StringVar()
        ttk.Entry(f1, textvariable=self.var_game).pack(side="left", fill="x", expand=True, padx=8, pady=8)
        ttk.Button(f1, text="Sfoglia...", command=self.pick_game).pack(side="left", padx=(0, 8))

        f2 = ttk.LabelFrame(self, text="Dove mettere l'italiano nel menu delle lingue")
        f2.pack(fill="x", **pad)
        self.var_lang = tk.StringVar(value=LINGUE[0][1])
        self.cmb = ttk.Combobox(f2, textvariable=self.var_lang, state="readonly",
                                values=[lbl for _, lbl in LINGUE])
        self.cmb.pack(side="left", fill="x", expand=True, padx=8, pady=8)
        ttk.Label(f2, text="la voce scelta diventera \"Italiano\"",
                  foreground="#666").pack(side="left", padx=(0, 8))

        f3 = ttk.Frame(self)
        f3.pack(fill="x", **pad)
        self.btn_auto = ttk.Button(f3, text="Trova il gioco", command=self.on_auto_button)
        self.btn_auto.pack(side="left")
        self.btn_go = ttk.Button(f3, text="APPLICA LA TRADUZIONE", command=self.apply)
        self.btn_go.pack(side="left", padx=8)
        self.btn_undo = ttk.Button(f3, text="Ripristina", command=self.restore)
        self.btn_undo.pack(side="left")
        self.var_music = tk.BooleanVar(value=False)
        ttk.Checkbutton(f3, text="♪ Musica", variable=self.var_music,
                        command=self.toggle_music).pack(side="right")

        self.bar = ttk.Progressbar(self, mode="indeterminate")
        self.bar.pack(fill="x", padx=10)

        self.txt = tk.Text(self, height=11, wrap="word", state="disabled",
                           bg="#1e1e1e", fg="#dcdcdc", insertbackground="#dcdcdc")
        self.txt.pack(fill="both", expand=True, padx=10, pady=(10, 4))

        self.scroll_lbl = tk.Label(self, anchor="w", font=("Consolas", 10, "bold"),
                                   bg="#000000", fg="#39ff14")
        self.scroll_lbl.pack(fill="x", padx=10, pady=(0, 10))
        self.scroll_text = (
            "*** MOONLIGHTER 2: THE ENDLESS VAULT - PATCH ITALIANA ***   "
            "la traduzione e opera dei TWR - autore PolyZen - tutto il merito e loro   ***   "
            "idea e realizzazione della patch per la 1.0: MARKMAYER   ***   "
            "5826 voci di testo riportate sulla nuova struttura del gioco   ***   "
            "nel gioco scegli la lingua ITALIANO   ***   "
            "il backup e automatico: puoi sempre tornare indietro   ***   "
            "buon divertimento, mercante!   ***      ")
        self.scroll_i = 0
        self.animate_scroll()

        self.log("Benvenuto.")
        self.log(CREDITI + ". Questo programma riporta il loro lavoro sulla versione 1.0")
        self.log("e aggiunge le stringhe introdotte dalla 1.0 (schede, nuovi vantaggi, armi, dialoghi).")
        self.log("Idea e realizzazione della patch: MarkMayer.")
        self.log("")
        self.log("Premi \"Trova il gioco\", poi \"APPLICA LA TRADUZIONE\".")

        self.music = None          # la musica parte solo se l'utente la accende
        self.after(300, self.autodetect)

    # ---------------- intestazione grafica ----------------
    def load_banner(self):
        """Carica banner.png, se c'e'. Senza immagine la finestra resta com'era."""
        p = res_path("banner.png")
        if not os.path.isfile(p):
            return False
        try:
            from PIL import Image
            self.banner_src = Image.open(p).convert("RGB")
            return True
        except Exception as e:
            print("banner non caricato:", e)
            return False

    def fit_banner(self, event=None):
        """Ridisegna il banner al termine del ridimensionamento, non a ogni evento."""
        if self.banner_src is None:
            return
        if getattr(self, "_banner_job", None):
            self.after_cancel(self._banner_job)
        self._banner_job = self.after(120, self._do_fit_banner)

    def _do_fit_banner(self):
        self._banner_job = None
        w = self.winfo_width()
        if w < 50 or w == self._banner_w:
            return
        self._banner_w = w
        try:
            from PIL import Image, ImageTk
            sw, sh = self.banner_src.size
            h = max(1, round(sh * w / sw))
            img = self.banner_src.resize((w, h), Image.LANCZOS)
            self.banner_img = ImageTk.PhotoImage(img)   # va tenuto vivo, altrimenti sparisce
            self.banner_lbl.configure(image=self.banner_img)
        except Exception as e:
            print("banner non ridimensionato:", e)

    # ---------------- musica e scroller ----------------
    def start_music(self):
        try:
            import chiptune
            self.music = chiptune.Player(on_error=self.music_error)
            self.music.start()
        except Exception as e:
            self.music = None
            self.music_error(e)

    def music_error(self, e):
        """Gli errori audio non vanno nascosti: il programma resta usabile, ma si vedono."""
        self.after(0, lambda: self.log(f"(musica non disponibile: {e})"))

    def toggle_music(self):
        if self.var_music.get():
            self.start_music()
        elif self.music:
            self.music.stop()

    def animate_scroll(self):
        t = self.scroll_text
        self.scroll_i = (self.scroll_i + 1) % len(t)
        self.scroll_lbl.configure(text=(t + t)[self.scroll_i:self.scroll_i + 98])
        self.after(70, self.animate_scroll)

    def destroy(self):
        if self.music:
            self.music.cleanup()      # ferma il suono e rimuove il file temporaneo
        super().destroy()

    # ---------------- utilita ----------------
    def log(self, s):
        self.txt.configure(state="normal")
        self.txt.insert("end", s + "\n")
        self.txt.see("end")
        self.txt.configure(state="disabled")
        self.update_idletasks()

    def set_busy(self, on):
        self.busy = on
        for b in (self.btn_go, self.btn_undo):
            b.configure(state="disabled" if on else "normal")
        # durante la ricerca il pulsante resta premibile: serve per interromperla
        self.btn_auto.configure(state="normal" if (not on or self.scanning) else "disabled")
        self.btn_auto.configure(text="Interrompi ricerca" if self.scanning else "Trova il gioco")
        self.bar.start(12) if on else self.bar.stop()

    def run_bg(self, fn):
        if self.busy:
            return
        self.set_busy(True)
        def worker():
            try:
                fn()
            except Exception as e:
                self.log("\nERRORE: " + str(e))
                messagebox.showerror(APP, str(e))
            finally:
                self.after(0, lambda: self.set_busy(False))
        threading.Thread(target=worker, daemon=True).start()

    def target_lang(self):
        lbl = self.var_lang.get()
        for code, l in LINGUE:
            if l == lbl:
                return code
        return "plPL"

    # ---------------- azioni ----------------
    def pick_game(self):
        p = filedialog.askdirectory(title="Scegli la cartella del gioco")
        if not p:
            return
        p = p.replace("/", "\\")
        if not os.path.isfile(os.path.join(p, "data.unity3d")) and os.path.isdir(p):
            for sub in sorted(os.listdir(p)):
                cand = os.path.join(p, sub)
                if sub.endswith("_Data") and os.path.isfile(os.path.join(cand, "data.unity3d")):
                    p = cand
                    break
        self.var_game.set(p)
        if self.scanning:
            self.cancel_scan()
        if not os.path.isfile(os.path.join(p, "data.unity3d")):
            messagebox.showwarning(APP, "In questa cartella non c'e data.unity3d.\n\n"
                                        "Scegli la cartella del gioco (quella con l'eseguibile)\n"
                                        "oppure direttamente la cartella che finisce con _Data.")

    def choose_install(self, found):
        box = tk.Toplevel(self)
        box.title("Quale installazione?")
        box.transient(self); box.grab_set()
        ttk.Label(box, text="Ho trovato piu installazioni del gioco.\nScegli quella da tradurre:",
                  justify="left").pack(anchor="w", padx=12, pady=(12, 6))
        var = tk.StringVar(value=found[0])
        for p in found:
            ttk.Radiobutton(box, text=p, value=p, variable=var).pack(anchor="w", padx=16)
        ttk.Button(box, text="Usa questa", command=box.destroy).pack(pady=12)
        self.wait_window(box)
        return var.get()
    def on_auto_button(self):
        """Lo stesso pulsante avvia la ricerca e la interrompe."""
        if self.scanning:
            self.cancel_scan()
        else:
            self.autodetect()

    def cancel_scan(self):
        self.stop_scan.set()
        self.log("Ricerca interrotta.")

    def autodetect(self):
        if self.busy:
            return
        self.stop_scan.clear()
        self.scanning = True

        def job():
            try:
                if self.var_game.get():
                    return
                self.log("")
                self.log("Cerco l'installazione del gioco...")
                self.log('Se sai dove si trova, usa "Sfoglia..." oppure "Interrompi ricerca".')
                found = scan_game_dirs(self.log, stop=self.stop_scan)
                if self.var_game.get():
                    return                      # nel frattempo l'ha scelta l'utente
                if self.stop_scan.is_set() and not found:
                    return
                if len(found) > 1:
                    self.log(f"Trovate {len(found)} installazioni.")
                    box, done = [found[0]], threading.Event()
                    def ask():
                        try:
                            box[0] = self.choose_install(found)
                        finally:
                            done.set()
                    self.after(0, ask)
                    done.wait(300)
                    self.var_game.set(box[0])
                    self.log("Uso: " + box[0])
                elif found:
                    self.var_game.set(found[0])
                    self.log("Trovato il gioco: " + found[0])
                else:
                    self.log('Gioco non trovato: indicalo a mano con "Sfoglia...".')
            finally:
                # lo stato dei pulsanti lo ripristina run_bg, che legge self.scanning
                self.scanning = False

        self.run_bg(job)

    def apply(self):
        g = self.var_game.get().strip()
        if not g:
            messagebox.showwarning(APP, "Indica prima la cartella del gioco.")
            return
        code = self.target_lang()
        nome = dict(LINGUE)[code].replace("al posto de", "").strip(" l'")
        if not messagebox.askyesno(APP,
                f"L'italiano prendera il posto della voce \"{nome}\" nel menu delle lingue,\n"
                "che si chiamera \"Italiano\". Le altre lingue restano come sono.\n\n"
                "Viene creato un backup automatico e puoi sempre premere \"Ripristina\".\n\n"
                "Procedo?"):
            return
        self.log("")
        self.run_bg(lambda: (do_patch(g, code, self.log),
                             messagebox.showinfo(APP, "Traduzione applicata.\n\n"
                                                      "Avvia il gioco, vai in Impostazioni\n"
                                                      "e scegli la lingua ITALIANO.")))

    def restore(self):
        g = self.var_game.get().strip()
        if not g:
            messagebox.showwarning(APP, "Indica prima la cartella del gioco.")
            return
        self.log("")
        self.run_bg(lambda: (do_restore(g, self.log),
                             messagebox.showinfo(APP, "Ripristinato: il gioco e tornato come prima.")))

if __name__ == "__main__":
    App().mainloop()
