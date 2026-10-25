# Editor de video con IA: quitar silencios + subtítulos

Esta skill le enseña a Claude a editar tus videos hablados:

- Quita los silencios y pausas.
- Transcribe lo que dices en español.
- Agrega subtítulos (simples o animados).
- Te entrega el video final en MP4 y el archivo de subtítulos .srt.

---

## Opción 1: En Claude (web o app de escritorio)

1. **Activa la ejecución de código.** Ve a **Configuración → Capacidades** y enciende **"Crear y editar archivos"** (en algunas versiones aparece como "Code execution and file creation").
2. **Sube la skill.** Entra a **claude.ai/customize/skills**, da clic en **"+" → "+ Create skill" → "Upload a skill"** y elige el archivo **`editor-video-hyperframes.zip`** tal cual, sin descomprimirlo.
3. **Actívala** con el interruptor en tu lista de skills.

> Si tu cuenta es de equipo o empresa y no ves la opción, pídele al administrador que active las skills.

**Importante:** en la versión web, a veces Claude no puede descargar el modelo de transcripción por restricciones de red. En ese caso igual te quita los silencios, pero para los subtítulos te pedirá un .srt o te sugerirá usar la Opción 2.

## Opción 2: En Claude Code (recomendado para videos largos)

Requisitos en tu computadora: **FFmpeg**, **Python 3** y **Node.js**.

| Sistema | Instalar FFmpeg |
|---|---|
| Mac | `brew install ffmpeg` |
| Windows | `winget install Gyan.FFmpeg` |
| Linux | `sudo apt-get install -y ffmpeg` |

Instala la skill. Tienes dos caminos:

- **Si ya la subiste en la Opción 1:** inicia sesión en Claude Code con la misma cuenta y se sincroniza sola. Escribe `/skills` para verla.
- **Si no la subiste:** descomprime el .zip y copia la carpeta `editor-video-hyperframes` dentro de `~/.claude/skills/`.
  - En Mac/Linux, la ruta completa queda así: `~/.claude/skills/editor-video-hyperframes/SKILL.md`.

**No necesitas instalar nada más.** La primera vez que uses la skill, Claude instala solo las 4 skills oficiales de HyperFrames (`hyperframes`, `hyperframes-cli`, `hyperframes-registry` y `media-use`).

Si prefieres dejarlas instaladas desde antes, ejecuta:

```bash
npx -y skills add heygen-com/hyperframes -g -y -a claude-code -s hyperframes hyperframes-cli hyperframes-registry media-use
```

---

## Cómo usarla

Adjunta tu video y escribe algo como:

- *"Quítale los silencios a este video y ponle subtítulos."*
- *"Edita este video en modo agresivo para reel, vertical 9:16, con subtítulos en mayúsculas."*
- *"Solo quita las pausas, sin subtítulos, ritmo suave."*

### Ritmos de corte

- **Suave:** deja respiraciones; ideal para clases.
- **Normal:** el valor por defecto.
- **Agresivo:** ritmo rápido, estilo TikTok/Reels.

### Estilos de subtítulos

- **Simples:** texto blanco con contorno negro, abajo del video.
- **Animados:** palabra por palabra estilo TikTok, hechos con HyperFrames. Tardan más en generarse.

---

## Si algo sale mal

| Problema | Qué pedirle a Claude |
|---|---|
| Se come palabras al cortar | "Repítelo en modo suave" |
| Quedaron pausas | "Hazlo más agresivo" |
| Subtítulos con errores de nombres | "Corrige: se escribe ___" |
| La transcripción salió en inglés | "Transcribe en español con el modelo small" |

---

*Herramientas usadas: FFmpeg, Whisper y HyperFrames (open source de HeyGen).*
