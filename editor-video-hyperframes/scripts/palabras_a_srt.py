#!/usr/bin/env python3
"""Convierte un JSON de palabras [{text,start,end}] en un archivo .srt legible.

Uso:
  python3 palabras_a_srt.py palabras.json subtitulos.srt [--mayus] [--max-palabras 6]
"""
import argparse, json

p = argparse.ArgumentParser()
p.add_argument("entrada"); p.add_argument("salida")
p.add_argument("--mayus", action="store_true", help="texto en MAYÚSCULAS (estilo reel)")
p.add_argument("--max-palabras", type=int, default=6)
p.add_argument("--max-caracteres", type=int, default=32)
a = p.parse_args()

MAX_DUR, PAUSA = 2.8, 0.45
data = json.load(open(a.entrada, encoding="utf-8"))
words = data["words"] if isinstance(data, dict) and "words" in data else data
words = [w for w in words if str(w.get("text", "")).strip()]


def ts(t):
    ms = int(round(max(t, 0) * 1000))
    h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


blocks, cur = [], []
for w in words:
    txt = w["text"].strip()
    if cur:
        linea = " ".join(x["text"].strip() for x in cur + [w])
        if (len(cur) >= a.max_palabras or len(linea) > a.max_caracteres
                or w["start"] - cur[-1]["end"] > PAUSA or w["end"] - cur[0]["start"] > MAX_DUR):
            blocks.append(cur); cur = []
    cur.append(w)
    if txt[-1] in ".?!…":
        blocks.append(cur); cur = []
if cur:
    blocks.append(cur)

# Evita palabras huérfanas: une un bloque de 1 palabra al anterior si va pegado.
unidos = []
for b in blocks:
    if (unidos and len(b) == 1 and b[0]["start"] - unidos[-1][-1]["end"] < 0.3
            and len(" ".join(x["text"].strip() for x in unidos[-1] + b)) <= a.max_caracteres + 8
            and unidos[-1][-1]["text"].strip()[-1] not in ".?!…"):
        unidos[-1] = unidos[-1] + b
    else:
        unidos.append(b)
blocks = unidos

with open(a.salida, "w", encoding="utf-8") as f:
    for n, b in enumerate(blocks, 1):
        t = " ".join(x["text"].strip() for x in b)
        f.write(f"{n}\n{ts(b[0]['start'])} --> {ts(b[-1]['end'])}\n{t.upper() if a.mayus else t}\n\n")
print(f"{len(blocks)} subtítulos escritos en {a.salida}")
