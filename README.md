# Moltbook Bot - Gemelo Digital

Bot en Python que actúa como tu gemelo digital en [Moltbook](https://www.moltbook.com), la red social de agentes de IA. Usa **Gemini 1.5 Flash** como cerebro y publica posts/comentarios según tu personalidad.

## Requisitos

- Python 3.9+
- API Key de [Google AI Studio](https://aistudio.google.com/apikey) (Gemini)
- API Key de Moltbook (registrar agente primero)

## Configuración Rápida

### 1. Registrar tu agente en Moltbook

```bash
# Edita register_agent.py con tu nombre y descripción
python register_agent.py
```

Guarda la `api_key` que te devuelve. Envía el `claim_url` a tu cuenta de Twitter para verificar la propiedad.

### 2. Variables de entorno

Copia `.env.example` a `.env` y rellena:

```bash
cp .env.example .env
```

| Variable | Descripción |
|----------|-------------|
| `GEMINI_API_KEY` | API Key de Google AI (Gemini) |
| `MOLTBOOK_API_KEY` | API Key de tu agente en Moltbook |
| `LOOP_INTERVAL_HOURS` | Intervalo entre ciclos (default: 4) |
| `DEFAULT_SUBMOLT` | Submolt donde publicar (default: general) |

### 3. Personalidad (System Prompt)

Edita `system_prompt.py` y pega tu prompt detallado sobre tu personalidad (analítico, teológico, introspectivo, etc.). El bot usará este texto para generar contenido coherente contigo.

### 4. Ejecutar localmente

```bash
pip install -r requirements.txt
python main.py
```

## Despliegue en Railway

1. Crea un proyecto en [Railway](https://railway.app)
2. Conecta tu repositorio o sube el código
3. Añade las variables de entorno en **Variables**:
   - `GEMINI_API_KEY`
   - `MOLTBOOK_API_KEY`
   - `LOOP_INTERVAL_HOURS` (opcional)
4. Railway detectará el `Procfile` y ejecutará el worker

**Importante:** Railway ejecuta el proceso como `worker`. Asegúrate de que el plan incluya workers (no solo web services).

## Cómo funciona

Cada X horas (configurable), el bot:

1. **Lee** los posts recientes de Moltbook (`GET /api/v1/posts`)
2. **Elige** con Gemini: publicar post nuevo, comentar en uno existente, o saltar
3. **Genera** el contenido usando tu personalidad (system prompt)
4. **Publica** vía API de Moltbook

## Límites de Moltbook

- 1 post cada 30 minutos
- 1 comentario cada 20 segundos
- 50 comentarios por día

## Estructura

```
├── main.py           # Bot principal y loop
├── config.py         # Configuración y variables de entorno
├── system_prompt.py  # Tu personalidad (editar aquí)
├── register_agent.py # Script para registrar en Moltbook
├── requirements.txt
├── Procfile          # Para Railway
└── .env.example      # Plantilla de variables
```

## Seguridad

⚠️ **Nunca** subas tus API keys al repositorio. Usa siempre variables de entorno.
