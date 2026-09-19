# -*- coding: utf-8 -*-
"""
Patch Italiana per Moonlighter 2: The Endless Vault (versione 1.0) - riga di comando
===================================================================================

Traduzione: TWR - autore PolyZen (realizzata per la build Early Access).
Idea e realizzazione della patch per la 1.0: Nefer.

Come funziona
-------------
I testi del gioco stanno in un unico oggetto Unity `Gridly.Project`: una tabella
con una riga per stringa e una colonna per lingua. La patch scrive l'italiano in
una di quelle colonne e rinomina la voce corrispondente nel menu delle lingue,
cosi nel gioco compare "Italiano" come voce a se' e l'inglese resta inglese.

Requisiti
---------
  python -m pip install UnityPy

Uso
---
  python ml2_patch_it.py "<cartella _Data>"                 # italiano al posto del polacco
  python ml2_patch_it.py "<cartella _Data>" --lingua ptBR   # ...al posto del portoghese
  python ml2_patch_it.py "<cartella _Data>" --ripristina

Lingue sostituibili: plPL ptBR ruRU jaJP koKR zhCN deDE frFR esES enUS
"""
import sys, os, gzip, json, struct, shutil, collections

try:
    import UnityPy
except ImportError:
    sys.exit("Manca UnityPy. Installalo con:  python -m pip install UnityPy")
UnityPy.config.FALLBACK_UNITY_VERSION = "2022.3.0f1"

LINGUE = ["plPL", "ptBR", "ruRU", "jaJP", "koKR", "zhCN", "deDE", "frFR", "esES", "enUS"]

def res_path(name):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)

# ---------------------------------------------------------------- Gridly
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
        sys.exit(f"Asset dei testi non trovato in {path}: versione non supportata?")
    return best

# ---------------------------------------------------------------- main
def main():
    args = [a for a in sys.argv[1:]]
    if not args:
        sys.exit(__doc__)
    data_dir = args[0]
    target = "plPL"
    if "--lingua" in args:
        target = args[args.index("--lingua") + 1]
        if target not in LINGUE:
            sys.exit(f"Lingua non valida. Scegli fra: {' '.join(LINGUE)}")

    dst = os.path.join(data_dir, "data.unity3d")
    orig = os.path.join(data_dir, "data.unity3d.orig")
    if not os.path.isfile(dst):
        sys.exit(f"Non trovo data.unity3d in {data_dir}")

    if "--ripristina" in args:
        if not os.path.isfile(orig):
            sys.exit("Backup non trovato: niente da ripristinare.")
        shutil.copy2(orig, dst)
        print("Ripristinato il file originale.")
        return

    if not os.path.isfile(orig):
        print("Creo il backup data.unity3d.orig ...")
        shutil.copy2(dst, orig)
    else:
        print("Backup gia presente, riparto da quello.")

    with gzip.open(res_path("italiano.json.gz"), "rb") as f:
        it = json.loads(f.read().decode("utf-8"))
    meta = it.pop("_meta", {})
    print(f"Testi italiani: {len(it)} voci  ({meta.get('traduzione', '')})")

    print("Apro data.unity3d ...")
    env, obj, d = find_project(orig)
    raw = obj.get_raw_data()
    header, tail = raw[:28], raw[d["consumed"]:]

    cols = set()
    for g in d["grids"]:
        for r in g["records"]:
            cols.update(r["cells"])
    if target not in cols:
        sys.exit(f"La lingua {target} non esiste in questa versione del gioco.")

    stat = collections.Counter()
    for g in d["grids"]:
        for r in g["records"]:
            if target not in r["cells"]:
                continue
            k = f"{g['name']}|{r['id']}"
            if k in it:
                r["cells"][target] = it[k]; stat["italiano"] += 1
            else:
                r["cells"][target] = r["cells"].get("enUS", r["cells"][target])
                stat["inglese"] += 1

    tot = sum(stat.values())
    print(f"Tradotte {stat['italiano']} stringhe su {tot} ({stat['italiano']*100/tot:.1f}%).")

    new_raw = serialize(d, header, tail)
    chk = parse(new_raw)
    assert chk["consumed"] + len(tail) == len(new_raw), "errore di riserializzazione"
    assert sum(len(g["records"]) for g in chk["grids"]) == tot, "conteggio record alterato"

    print("Riscrivo il bundle (puo richiedere un minuto) ...")
    obj.set_raw_data(new_raw)
    with open(dst, "wb") as f:
        f.write(env.file.save(packer="original"))
    print(f"Fatto: {dst}")
    print("Avvia il gioco, vai in Impostazioni e scegli la lingua ITALIANO.")

if __name__ == "__main__":
    main()
