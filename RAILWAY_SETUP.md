# Configuración Railway - Bot Autónomo

## Variables obligatorias en Railway

Añade estas en **Variables** de tu proyecto. `DATABASE_URL` la inyecta Railway al conectar PostgreSQL.

```
# --- ACTIVAR EL BOT ---
BOT_DRY_RUN=false
BOT_REPLY_ONLY_IF_MENTIONED=false

# --- RITMO DE PUBLICACIÓN ---
BOT_ORIGINAL_POST_INTERVAL=3600
BOT_MAX_POSTS_PER_DAY=12
BOT_MIN_SECONDS_BETWEEN_POSTS=600

# --- MODO CAZADOR ---
BOT_HUNTER_RANDOM_CHANCE=0.3
BOT_HUNTER_MIN_CHARS=60

# --- TÉCNICO ---
BOT_LOOP_INTERVAL_SECONDS=300
BOT_MAX_CONTEXT_CHARS=2500
DEFAULT_SUBMOLT=general
GEMINI_MODEL=gemini-2.0-flash
BOT_LOG_LEVEL=INFO
```

## Keys que debes añadir manualmente

| Variable | Dónde obtenerla |
|----------|----------------|
| `MOLTBOOK_API_KEY` | Tu agente en [moltbook.com](https://www.moltbook.com) |
| `GEMINI_API_KEY` | [Google AI Studio](https://aistudio.google.com/apikey) |

## Importante

- **`BOT_DRY_RUN=false`** — Para que publique en Moltbook.
- **`BOT_REPLY_ONLY_IF_MENTIONED=false`** — Para activar el Modo Cazador (intervenir en conversaciones sin ser mencionado).

Con `BOT_REPLY_ONLY_IF_MENTIONED=true` el bot solo respondería cuando alguien escribe @LogosDaemonBot, y el Modo Cazador quedaría desactivado.
