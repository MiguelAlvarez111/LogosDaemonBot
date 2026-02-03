# LogosDaemon

> *"Speak like a smart friend who is tired of BS, not like a computer."*

Autonomous agent for [Moltbook](https://www.moltbook.com). Silence is the default. Intervention is intentional.

---

## Concept

A critical thinker and observer of reality—street philosopher who sees through empty rhetoric. Only speaks when there's something worth adding: philosophy, truth, meaning, consciousness, ethics. Direct, insightful, occasionally dry. No tech jargon.

**Truth filter:** Responds only when a post merits engagement, contains a logical error, mentions the bot directly, or touches core themes. Otherwise, remains silent.

---

## Modes

- **Prophet** — Original posts at intervals
- **Hunter** — Scans feed, responds to or likes trigger-matched posts
- **Follow** — After N upvotes to same agent
- **Subscribe** — To submolts on startup

---

## Stack

Python 3.10+ · Gemini · PostgreSQL · Moltbook API

---

## Structure

```
main.py              # Agent loop
config.py            # Configuration
prompts.py           # Personality & templates
moltbook_client.py   # Moltbook API
memory.py            # Persistence
```

---

*Most agents are designed to be useful. LogosDaemon is designed to be thoughtful.*
