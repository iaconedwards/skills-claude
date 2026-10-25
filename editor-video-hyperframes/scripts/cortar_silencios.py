#!/usr/bin/env python3
"""Detecta y elimina silencios de un video con FFmpeg.

Uso:
  python3 cortar_silencios.py ENTRADA.mp4 SALIDA.mp4 [--modo suave|normal|agresivo]
                              [--umbral -32dB] [--min-silencio 0.5] [--margen 0.12]

Genera junto a SALIDA un archivo cortes.json con los segmentos conservados.
"""
import argparse, json, os, re, subprocess, sys

MODOS = {
    "suave":    {"umbral": "-35dB", "min_silencio": 0.8,  "margen": 0.20},
    "normal":   {"umbral": "-32dB", "min_silencio": 0.5,  "margen": 0.12},
    "agresivo": {"umbral": "-30dB", "min_silencio": 0.35, "margen": 0.07},
}

p = argparse.ArgumentParser()
p.add_argument("entrada"); p.add_argument("salida")
p.add_argument("--modo", choices=MODOS, default="normal")
p.add_argument("--umbral"); p.add_argument("--min-silencio", type=float)
p.add_argument("--margen", type=float)
a = p.parse_args()

cfg = dict(MODOS[a.modo])
if a.umbral: cfg["umbral"] = a.umbral
if a.min_silencio is not None: cfg["min_silencio"] = a.min_silencio
if a.margen is not None: cfg["margen"] = a.margen
NOISE, MIN_SIL, PAD = cfg["umbral"], cfg["min_silencio"], cfg["margen"]

dur = float(subprocess.check_output(
    ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.entrada]).strip())
r = subprocess.run(["ffmpeg", "-hide_banner", "-i", a.entrada, "-af",
                    f"silencedetect=noise={NOISE}:d={MIN_SIL}", "-f", "null", "-"],
                   capture_output=True, text=True)
starts = [max(0.0, float(x)) for x in re.findall(r"silence_start: (-?[\d.]+)", r.stderr)]
ends = [float(x) for x in re.findall(r"silence_end: (-?[\d.]+)", r.stderr)]
if len(ends) < len(starts):
    ends.append(dur)

keep, cur = [], 0.0
for s, e in zip(starts, ends):
    ini, fin = cur, min(s + PAD, dur)
    if fin - ini > 0.08:
        keep.append([ini, fin])
    cur = max(e - PAD, 0.0)
termina_en_silencio = bool(ends) and ends[-1] >= dur - 0.05
if not termina_en_silencio and dur - cur > 0.08:
    keep.append([cur, dur])

merged = []
for ini, fin in keep:
    if merged and ini <= merged[-1][1] + 0.02:
        merged[-1][1] = max(merged[-1][1], fin)
    else:
        merged.append([ini, fin])

if not merged:
    sys.exit("No se detectó voz: baja el umbral (ej. --umbral -40dB) o revisa el audio.")

outdir = os.path.dirname(os.path.abspath(a.salida))
expr = "+".join(f"between(t,{i:.3f},{f:.3f})" for i, f in merged)
filtro = os.path.join(outdir, "filtro_cortes.txt")
with open(filtro, "w") as fh:
    fh.write(f"[0:v]select='{expr}',setpts=N/FRAME_RATE/TB[v];"
             f"[0:a]aselect='{expr}',asetpts=N/SR/TB[a]")

subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", a.entrada,
                "-filter_complex_script", filtro, "-map", "[v]", "-map", "[a]",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", a.salida], check=True)

final = sum(f - i for i, f in merged)
with open(os.path.join(outdir, "cortes.json"), "w") as fh:
    json.dump({"modo": a.modo, "parametros": cfg, "segmentos": [[round(i, 3), round(f, 3)] for i, f in merged],
               "duracion_original": round(dur, 3), "duracion_final": round(final, 3)}, fh, indent=1)
print(f"Original {dur:.1f}s -> final {final:.1f}s | {len(merged)} segmentos | "
      f"{dur - final:.1f}s eliminados ({100 * (dur - final) / dur:.0f}%)")
