# Skills para Claude

Colección de skills listas para instalar en Claude. Cada skill le enseña a Claude a hacer una tarea completa de principio a fin.

## Catálogo

| Skill | Qué hace | Descargar |
|---|---|---|
| **[editor-video-hyperframes](editor-video-hyperframes/)** | Quita silencios y pausas de videos hablados, transcribe en español y agrega subtítulos (simples o animados). Entrega MP4 + .srt. | [⬇️ .zip](descargas/editor-video-hyperframes.zip?raw=1) |

## Cómo instalar una skill

### En Claude (web o app de escritorio)

1. Activa la ejecución de código en **Configuración → Capacidades** ("Crear y editar archivos").
2. Descarga el **.zip** de la skill desde la tabla de arriba.
3. Entra a **[claude.ai/customize/skills](https://claude.ai/customize/skills)** y da clic en **"+" → "+ Create skill" → "Upload a skill"**.
4. Sube el .zip tal cual, sin descomprimirlo, y actívala.

### En Claude Code

- Si ya la subiste en claude.ai, se sincroniza sola al iniciar sesión con la misma cuenta. Escribe `/skills` para verla.
- O copia la carpeta de la skill dentro de `~/.claude/skills/`.

Cada carpeta trae su propio **LEEME.md** con requisitos e instrucciones de uso.
