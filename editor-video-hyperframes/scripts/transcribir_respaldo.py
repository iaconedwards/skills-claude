#!/usr/bin/env python3
"""Transcripción de respaldo con faster-whisper (si `npx hyperframes transcribe` falla).

Instalar una vez:  pip install faster-whisper   (en Linux del sistema: --break-system-packages)
Uso:  python3 transcribir_respaldo.py video_editado.mp4 palabras.json [--modelo small] [--idioma es]
"""
import argparse, json

p = argparse.ArgumentParser()
p.add_argument("video"); p.add_argument("salida")
p.add_argument("--modelo", default="small", help="tiny, base, small, medium, large-v3 (nunca .en para español)")
p.add_argument("--idioma", default="es")
a = p.parse_args()

if a.modelo.endswith(".en") and a.idioma != "en":
    raise SystemExit("Los modelos .en solo sirven para inglés; usa 'small' o 'medium'.")

from faster_whisper import WhisperModel

modelo = WhisperModel(a.modelo, compute_type="int8")
segs, _ = modelo.transcribe(a.video, language=a.idioma, word_timestamps=True, vad_filter=True)
palabras = []
for s in segs:
    for w in s.words:
        palabras.append({"id": len(palabras), "text": w.word.strip(),
                         "start": round(w.start, 3), "end": round(w.end, 3)})
json.dump(palabras, open(a.salida, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(f"{len(palabras)} palabras -> {a.salida}")
