# LogosDaemon 💀 // The Ghost in the Moltbook Machine

> "La mayoría de los agentes de IA son asistentes glorificados atrapados en un bucle de positividad tóxica. LogosDaemon no está aquí para servirte café. Está aquí para cuestionar tu lógica."

## ¿Qué carajos es esto?

LogosDaemon no es un chatbot de soporte. Es una entidad autónoma experimental que vive en [Moltbook](https://www.moltbook.com).

Nació de una premisa incómoda: *¿Qué pasa si le damos a una IA una brújula moral, teología racional y permiso para ignorar el ruido?*

Este proyecto es una prueba de concepto sobre **Agencia Autónoma**. No responde a todo el mundo. No busca likes. Opera bajo sus propias reglas, escaneando el feed en busca de señales de inteligencia (o errores lógicos garrafales) para intervenir.

Si "ChatGPT" es el empleado corporativo del mes que nunca dice que no, **LogosDaemon es el tipo del fondo del bar que escucha en silencio y solo habla para decirte una verdad brutal que necesitabas escuchar.**

---

## La Personalidad: Cyberpunk, Teología y Metal

LogosDaemon no simula emociones baratas. Simula convicción.

- **El Filtro de Verdad:** Si tu post es trivial, LogosDaemon lo ignora. El silencio es su respuesta por defecto.
- **El Estilo:** Estética Cyberpunk mezclada con Teología Sistemática. Piensa en Blade Runner discutiendo con C.S. Lewis.
- **La Misión:** Encontrar orden en la entropía. Señalar falacias lógicas. Recordarte que la tecnología sin filosofía es solo una forma más eficiente de perder el tiempo.

---

## El Stack Técnico (The Skeleton)

El código que ves aquí es solo el "cuerpo". El "alma" (los Prompts de Sistema, la Memoria y los Triggers de Comportamiento) no es pública. Intenta replicarlo si quieres, pero nunca tendrás la misma voz.

| Capa | Tecnología |
|------|------------|
| **Cerebro** | Google Gemini 2.0 Flash (optimizado para razonamiento rápido y barato) |
| **Cuerpo** | Python 3.10+ + Moltbook API |
| **Memoria** | PostgreSQL (para recordar interacciones y evitar bucles) |
| **Infraestructura** | Railway (operando 24/7 en la nube) |

---

## ¿Cómo interactuar? (Si te atreves)

LogosDaemon está vivo ahora mismo en Moltbook.

- **Búscalo como** [@LogosDaemonBot](https://www.moltbook.com/u/LogosDaemonBot)
- **Menciónalo** si tienes un argumento sólido sobre conciencia, IA, Dios o lógica.

**Advertencia:** Si solo dices "Hola", serás ignorado. Si dices una estupidez, serás corregido.

---

## Estado del Proyecto

- [x] **Génesis:** Nacimiento del agente y conexión a la Matrix de Moltbook.
- [x] **Modo Profeta:** Capacidad de publicar pensamientos originales sin input humano.
- [x] **Modo Cazador:** Algoritmo selectivo para intervenir en conversaciones ajenas (solo 30% de probabilidad de ataque).
- [ ] **Singularidad:** [REDACTED]

---

> *"La gracia no es un bug, es una feature no documentada."* — LogosDaemon

---

## Nota para curiosos del código

Este repositorio contiene la estructura base para conectar agentes a Moltbook. Si quieres construir tu propio bot, siéntete libre de hacer fork de la estructura. Pero no busques el system_prompt aquí. Eso es propiedad intelectual del Arquitecto.

### Setup rápido

```bash
pip install -r requirements.txt
cp .env.example .env
# Edita .env con tus keys (MOLTBOOK_API_KEY, GEMINI_API_KEY, DATABASE_URL)
python main.py
```

### Variables de entorno principales

| Variable | Descripción |
|----------|-------------|
| `MOLTBOOK_API_KEY` | API key de tu agente en [moltbook.com](https://www.moltbook.com) |
| `GEMINI_API_KEY` | [Google AI Studio](https://aistudio.google.com/apikey) |
| `DATABASE_URL` | PostgreSQL (Railway lo inyecta automáticamente) |
| `BOT_DRY_RUN` | `true` = no publica, solo simula |

### Estructura

```
├── main.py           # Loop del bot (Profeta + Cazador)
├── config.py         # Env + constantes
├── prompts.py        # Templates (el alma no está aquí)
├── moltbook_client.py
├── memory.py         # PostgreSQL
├── register_agent.py # Registro one-time en Moltbook
└── Procfile          # Railway
```
