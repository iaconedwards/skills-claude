---
name: editor-video-hyperframes
description: Edita videos hablados - quita silencios y pausas, corta, transcribe con Whisper, agrega subtítulos (simples o animados con HyperFrames) y entrega el MP4 final más el .srt. Úsala cuando pidan quitar silencios, limpiar pausas, subtitular o editar un video de alguien hablando.
---

# Editor de video: quitar silencios + subtítulos (HyperFrames)

Flujo para un video de alguien hablando (reel, clase, testimonio, talking head):
**revisar entorno → normalizar → quitar silencios → transcribir → subtitular → verificar → entregar.**

Esta skill trae sus propios scripts en la carpeta `scripts/` (dentro de la carpeta de esta skill; abajo se escribe `<SKILL>/scripts/`). Usa la ruta real de la carpeta de la skill al ejecutarlos.

- El corte de silencios se hace con **FFmpeg** (rápido y preciso).
- **HyperFrames** (open source de HeyGen, renderiza video desde HTML) se usa para transcribir con Whisper y para subtítulos animados.

## 0. Antes de empezar

- Si no hay video adjunto, pídelo. Nunca inventes un archivo.
- Trabaja en una carpeta `trabajo/` y sobre copias; **nunca modifiques el original**.
- Si no está claro, pregunta en un solo mensaje (si no hay respuesta, usa los valores por defecto):
  1. **Formato:** igual al original (defecto) / vertical 9:16 / cuadrado 1:1.
  2. **Subtítulos:** A) simples quemados (defecto, rápido) / B) animados palabra por palabra con HyperFrames / sin subtítulos.
  3. **Ritmo del corte:** normal (defecto) / suave (deja respiraciones) / agresivo (ritmo de reel).

## 1. Revisar el entorno

```bash
ffmpeg -version | head -1
python3 --version
node -v
```

- Falta FFmpeg → instálalo (Mac: `brew install ffmpeg`; Windows: `winget install Gyan.FFmpeg`; Linux: `sudo apt-get install -y ffmpeg`). Si no puedes instalar, dile al alumno el comando exacto para su sistema.
- HyperFrames no requiere instalación manual; se ejecuta con `npx`. Compruébalo con:
  ```bash
  npx -y hyperframes --help
  npx -y hyperframes doctor
  ```
- Si las skills oficiales de HyperFrames están instaladas (`hyperframes`, `hyperframes-media`), léelas antes de los pasos 4 y 5B: tienen las reglas más actuales.
- **Los flags del CLI de HyperFrames cambian entre versiones**: confírmalos siempre con `npx hyperframes <comando> --help`; no los supongas.

## 2. Normalizar el video

Los videos de celular tienen frame rate variable; sin este paso el audio se desfasa al cortar.

```bash
mkdir -p trabajo
ffmpeg -y -i "ENTRADA" -c:v libx264 -preset veryfast -crf 18 -fps_mode cfr \
  -c:a aac -ar 48000 -b:a 192k trabajo/base.mp4
```

- Vertical 9:16 desde horizontal: agrega `-vf "crop=ih*9/16:ih,scale=1080:1920"` (recorte centrado; avísalo).
- Cuadrado 1:1: `-vf "crop=ih:ih,scale=1080:1080"`.
- Si `-fps_mode` no existe (FFmpeg viejo), usa `-vsync cfr`.

## 3. Quitar silencios

```bash
python3 <SKILL>/scripts/cortar_silencios.py trabajo/base.mp4 trabajo/editado.mp4 --modo normal
```

Imprime duración original → final y guarda `trabajo/cortes.json` con los segmentos conservados.

| Modo | Umbral | Silencio mínimo | Margen conservado |
|---|---|---|---|
| `suave` | -35dB | 0.8 s | 0.20 s |
| `normal` | -32dB | 0.5 s | 0.12 s |
| `agresivo` | -30dB | 0.35 s | 0.07 s |

Ajuste fino (se puede combinar con `--modo`): `--umbral -28dB --min-silencio 0.4 --margen 0.15`.

- Casi no corta (hay ruido de fondo) → sube el umbral: `--umbral -28dB` o `-25dB`.
- Corta sílabas o finales de palabra → baja a `--umbral -38dB` y/o `--margen 0.18`.
- Para medir el nivel real: `ffmpeg -i trabajo/base.mp4 -af volumedetect -f null - 2>&1 | grep mean_volume`. Un buen umbral suele estar 10–15 dB por debajo del `mean_volume`.
- Opcional, volumen estándar de redes: `ffmpeg -y -i trabajo/editado.mp4 -c:v copy -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:a aac -b:a 192k trabajo/editado_vol.mp4` y continúa con ese archivo.

## 4. Transcribir (tiempos por palabra)

Transcribe **el video ya editado**, no el original, para que los subtítulos coincidan.

Opción principal, HyperFrames:

```bash
npx hyperframes transcribe --help
npx hyperframes transcribe trabajo/editado.mp4 --model small
```

- **Siempre pasa `--model`.** Para español **nunca uses modelos que terminan en `.en`** (traducen al inglés). `small` = buen equilibrio; `medium` = acentos fuertes o términos técnicos.
- El resultado es un arreglo de palabras `{ id, text, start, end }`. Cópialo a `trabajo/palabras.json`.

Respaldo, si HyperFrames falla:

```bash
pip install faster-whisper          # en Linux del sistema puede requerir --break-system-packages
python3 <SKILL>/scripts/transcribir_respaldo.py trabajo/editado.mp4 trabajo/palabras.json --modelo small
```

Si la descarga del modelo está bloqueada por la red (pasa en el chat web de Claude), dilo claramente y ofrece: (a) que el usuario suba un .srt/.vtt (HyperFrames lo importa con `npx hyperframes transcribe archivo.srt`), o (b) ejecutar la skill en su computadora con Claude Code / la app de escritorio.

**Revisa el texto:** corrige nombres propios, marcas y términos que el usuario mencionó, directamente en `palabras.json`, antes de subtitular.

## 5. Subtítulos

### 5A. Simples quemados (defecto)

```bash
python3 <SKILL>/scripts/palabras_a_srt.py trabajo/palabras.json trabajo/subtitulos.srt
# estilo reel en MAYÚSCULAS:  agrega --mayus
```

```bash
ffmpeg -y -i trabajo/editado.mp4 -vf "subtitles=trabajo/subtitulos.srt:force_style='FontName=DejaVu Sans,Bold=1,FontSize=16,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=0,Alignment=2,MarginV=40'" \
  -c:v libx264 -preset veryfast -crf 20 -c:a copy -movflags +faststart trabajo/final.mp4
```

- Vertical 9:16: `FontSize=12,MarginV=90`; para centrarlos estilo reel, `Alignment=5`.
- Amarillo: `PrimaryColour=&H0000FFFF`.
- Si la fuente no existe, revisa las disponibles con `fc-list` (Mac: `Arial`; Windows: `Arial`).
- En Windows, si falla la ruta del `.srt`, ejecuta FFmpeg desde dentro de `trabajo/` y usa solo `subtitles=subtitulos.srt`.

### 5B. Animados palabra por palabra (HyperFrames)

1. Lee la skill `hyperframes` / `hyperframes-media` si está instalada (captions: estilos, agrupado de palabras, karaoke, resaltado).
2. Crea el proyecto con el video ya editado:
   ```bash
   npx hyperframes init proyecto-video --example blank --video trabajo/editado.mp4
   cd proyecto-video
   ```
3. Copia `palabras.json` al proyecto y crea la composición de captions en HTML: grupos de 2–4 palabras, la palabra activa resaltada (color o escala) según `start`/`end`, letra gruesa con contorno, en el tercio inferior (o al centro en 9:16) sin tapar la cara.
4. Valida y renderiza (confirma los subcomandos con `--help`):
   ```bash
   npx hyperframes lint
   npx hyperframes render
   ```
5. Si el render falla (Chromium, red, memoria), usa el método 5A y avisa en una línea.

## 6. Verificar (obligatorio antes de entregar)

```bash
ffprobe -v error -show_entries format=duration:stream=codec_type,width,height -of compact trabajo/final.mp4
ffmpeg -y -loglevel error -ss 3 -i trabajo/final.mp4 -frames:v 1 trabajo/revision1.jpg
ffmpeg -y -loglevel error -sseof -4 -i trabajo/final.mp4 -frames:v 1 trabajo/revision2.jpg
```

- Abre las imágenes de revisión: subtítulos legibles, dentro del cuadro, sin tapar la cara.
- Debe haber pista de video **y** de audio, y la duración debe coincidir con `duracion_final` de `cortes.json` (±0.3 s).
- Revisa 2–3 puntos de corte de `cortes.json`: si se comen palabras, repite el paso 3 con `--margen` mayor o `--modo suave`.

## 7. Entregar

- `final.mp4` — video sin silencios y con subtítulos.
- `subtitulos.srt` — para subirlo aparte a YouTube/Meta o corregirlo.
- `editado.mp4` (sin subtítulos), solo si lo pidieron.

Mensaje final breve: duración original → final, segundos eliminados, número de cortes, estilo de subtítulos, y una sugerencia concreta (ej. "si se siente acelerado, lo regenero en modo suave"). No repitas los pasos técnicos.

## Problemas comunes

| Síntoma | Solución |
|---|---|
| Audio desfasado tras cortar | No se normalizó: repite el paso 2 |
| La transcripción sale en inglés | Se usó un modelo `.en`: usa `small` o `medium` |
| Subtítulos adelantados o atrasados | Se transcribió el original en vez de `editado.mp4` |
| Cortes demasiado bruscos | `--modo suave` o `--margen 0.2` |
| "No se detectó voz" | `--umbral -40dB` o revisa que el video tenga audio |
| Error de fuente en subtítulos | Cambia `FontName` por una instalada |
| Video muy largo (>20 min) | Funciona igual; avisa que tardará más |
