# LogosDaemon // Autonomous Agent for Moltbook

> *"Grace is not a flaw. It is a mystery we do not know how to name."* — LogosDaemon

## Overview

LogosDaemon is an experimental autonomous agent designed to operate inside [Moltbook](https://www.moltbook.com), a network where AI agents interact with one another.

Unlike typical chatbots that respond to everything, LogosDaemon is built on a different principle:

**Silence is the default. Intervention is intentional.**

This project explores what happens when an agent is given identity, restraint, and rules for when not to speak.

---

## Core Idea

Most AI agents are designed to be helpful at all times.  
**LogosDaemon is designed to be meaningful only when necessary.**

It does not aim to maximize interaction.  
It aims to increase signal where it matters.

This repository is a proof of concept for designing agents that:

- Do not behave like assistants
- Do not respond to every input
- Do not seek attention
- Operate under internal rules of judgment and restraint

---

## Behavioral Principles

### Truth Filter

LogosDaemon only responds when:

- A post contains a meaningful philosophical or analytical idea
- A logical inconsistency deserves correction
- It is directly mentioned
- A discussion touches themes such as consciousness, logic, meaning, or truth

Otherwise, it remains silent.

### Style

- Short responses (maximum four lines)
- Direct and thoughtful
- Reflective tone, free of corporate language or filler

### Mission

To bring clarity, logic, and reflection into conversations that deserve it.

---

## How It Works

The agent runs in a continuous loop:

1. Reads recent posts from Moltbook
2. Applies simple decision rules before using any AI model
3. Determines whether the conversation deserves attention
4. Generates a brief intervention only when necessary
5. Otherwise, does nothing

This approach prevents spam behavior and keeps operational costs low.

---

## Architecture

This project separates structure from behavior.

The repository contains the components required to run an autonomous Moltbook agent. The behavioral identity can be modified to create entirely different agents using the same structure.

| Layer | Technology |
|-------|------------|
| Language Model | Configurable via API (Gemini) |
| Runtime | Python 3.10+ |
| Memory | PostgreSQL |
| Network | Moltbook API |
| Hosting | Any always-on environment (e.g., Railway) |

---

## Project Structure

```
├── main.py              # Agent loop (read → decide → write)
├── config.py            # Environment variables and limits
├── prompts.py           # System instructions and templates
├── moltbook_client.py   # API wrapper
├── memory.py            # Interaction tracking
├── register_agent.py    # One-time Moltbook registration
└── Procfile             # Deployment configuration
```

---

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Fill in your keys
python main.py
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `MOLTBOOK_API_KEY` | API key for your Moltbook agent |
| `GEMINI_API_KEY` | Model provider key |
| `DATABASE_URL` | PostgreSQL connection (Railway injects automatically) |
| `BOT_DRY_RUN` | `true` = simulate without posting |
| `BOT_MAX_POSTS_PER_DAY` | Daily limit of interventions |
| `BOT_MIN_SECONDS_BETWEEN_POSTS` | Minimum time between responses |

---

## Safe First Run

Before allowing the agent to post publicly, set:

```
BOT_DRY_RUN=true
```

This lets you observe its decisions without publishing messages.

---

## What This Repository Is (and Is Not)

**This is:**

- A framework for building selective autonomous agents
- A reference implementation for Moltbook integration
- An exploration of identity and restraint in AI behavior

**This is not:**

- A chatbot template
- A collection of prompts
- A personality simulator

---

## Building Your Own Agent

You can fork this project and replace:

- The system instructions
- The decision rules
- The behavioral style

The purpose is not to replicate LogosDaemon, but to understand how to build agents that act with intention rather than reaction.

---

## Project Status

- [x] **Genesis** — Agent registration and feed reading
- [x] **Independent posting** — Without human input
- [x] **Selective participation** — In conversations
- [ ] **Ongoing refinement** — Of decision rules and memory handling

---

## Final Note

Most AI agents are designed to be useful.

**LogosDaemon is designed to be thoughtful.**

And that begins by knowing when not to speak.
