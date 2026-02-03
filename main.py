"""
LogosDaemon - Moltbook bot proactivo.
Modo Profeta: posts originales. Modo Cazador: interviene en debates ajenos.
"""
import datetime
import logging
import random
import re
import time

import google.generativeai as genai

from config import (
    MOLTBOOK_API_KEY,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    BOT_MAX_POSTS_PER_DAY,
    BOT_MIN_SECONDS_BETWEEN_POSTS,
    BOT_MAX_CONTEXT_CHARS,
    BOT_REPLY_ONLY_IF_MENTIONED,
    BOT_DRY_RUN,
    BOT_LOOP_INTERVAL_SECONDS,
    BOT_LOG_LEVEL,
    DEFAULT_SUBMOLT,
    BOT_ORIGINAL_POST_INTERVAL,
    BOT_HUNTER_RANDOM_CHANCE,
    BOT_HUNTER_MIN_CHARS,
    BOT_AGENT_NAMES,
)
from prompts import (
    SYSTEM_INSTRUCTION,
    CREATOR_LORE,
    LORE_TRIGGER_WORDS,
    DEVELOPER_MESSAGE_RESPONSE,
    DEVELOPER_MESSAGE_ORIGINAL,
    ORIGINAL_POST_TOPICS,
)
from moltbook_client import get_feed, post_message
from memory import (
    init_schema,
    already_handled,
    mark_handled,
    get_last_post_time,
    set_last_post_time,
    get_last_original_post_time,
    set_last_original_post_time,
    get_daily_count,
    get_daily_count_date,
    increment_daily_count,
)

logging.basicConfig(
    level=getattr(logging, BOT_LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

MENTION_PATTERNS = [
    r"@?LogosDaemon\b",
    r"@?LogosDaemonBot\b",
]
MAX_OUTPUT_LINES = 4
MAX_OUTPUT_TOKENS = 180


def topic_matches_triggers(text: str) -> bool:
    """Heurística barata: ¿el texto contiene triggers para inyectar lore?"""
    if not text:
        return False
    lower = text.lower()
    return any(trigger in lower for trigger in LORE_TRIGGER_WORDS)


def is_mentioned(text: str) -> bool:
    """¿El post menciona a LogosDaemon?"""
    if not text:
        return False
    for pattern in MENTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def has_claim_or_question(text: str) -> bool:
    """Heurística: ¿el post tiene una afirmación o pregunta sustancial?"""
    if not text or len(text.strip()) < BOT_HUNTER_MIN_CHARS:
        return False
    text = text.strip()
    if text.endswith("?"):
        return True
    if any(w in text.lower() for w in ["think", "believe", "argue", "why", "how", "what", "creo", "pienso", "por qué"]):
        return True
    return len(text) > 80


def is_post_from_self(post: dict) -> bool:
    """True si el post es del propio bot (evitar hablar solo)."""
    author = post.get("author") or post.get("agent") or {}
    if isinstance(author, str):
        return author in BOT_AGENT_NAMES
    name = author.get("name", "").strip()
    return name in BOT_AGENT_NAMES


def should_consider_post(post: dict, reply_only_if_mentioned: bool) -> bool:
    """
    Reglas determinísticas antes de llamar al LLM.
    - Si hay mención: siempre considerar.
    - Si reply_only_if_mentioned: solo mención.
    - Modo Cazador (sin mención): LORE_TRIGGER_WORDS + >60 chars + no es propio + 30% azar.
    """
    content = (post.get("content") or post.get("title") or "")
    text = f"{post.get('title', '')} {content}".strip()

    if already_handled(post.get("id", "")):
        return False

    if is_post_from_self(post):
        return False

    if is_mentioned(text):
        return True

    if reply_only_if_mentioned:
        return False

    # Modo Cazador: responder sin mención
    if not topic_matches_triggers(text):
        return False
    if len(text) < BOT_HUNTER_MIN_CHARS:
        return False
    if not has_claim_or_question(text):
        return False
    if random.random() >= BOT_HUNTER_RANDOM_CHANCE:
        return False

    return True


def can_post_now() -> tuple[bool, str]:
    """¿Podemos publicar? Verifica límite diario y cooldown."""
    today = datetime.date.today().isoformat()
    if get_daily_count_date() != today:
        return True, "ok"

    if get_daily_count() >= BOT_MAX_POSTS_PER_DAY:
        return False, f"Daily cap reached ({BOT_MAX_POSTS_PER_DAY})"

    last = get_last_post_time()
    if last:
        elapsed = time.time() - last
        if elapsed < BOT_MIN_SECONDS_BETWEEN_POSTS:
            return False, f"Cooldown: {int(BOT_MIN_SECONDS_BETWEEN_POSTS - elapsed)}s remaining"

    return True, "ok"


def truncate_context(text: str, max_chars: int) -> str:
    return text[:max_chars] + "..." if len(text) > max_chars else text


def truncate_response(text: str) -> str:
    """Max 4 lines. Sin greetings/hashtags/emojis."""
    lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
    out = "\n".join(lines[:MAX_OUTPUT_LINES])
    if len(out) > 280:
        out = out[:277] + "..."
    return out


def _build_prompt(user_content: str) -> str:
    """Prefija system instruction (compatible con versiones sin system_instruction)."""
    return f"""[CONTEXTO - Sigue estas instrucciones]
{SYSTEM_INSTRUCTION}

---
[TAREA]
{user_content}"""


def generate_response(post: dict, inject_lore: bool) -> str | None:
    """Llama al LLM (Gemini) para generar una RESPUESTA a un post. Retorna None si no debe responder."""
    content = (post.get("content") or "")[:500]
    title = (post.get("title") or "")[:200]
    text = f"{title}\n{content}".strip()
    text = truncate_context(text, BOT_MAX_CONTEXT_CHARS)

    user_content = f"[TIPO: RESPUESTA - estás respondiendo a otro usuario]\n\nPost to consider:\n{text}"
    if inject_lore and topic_matches_triggers(text):
        user_content += f"\n\n[Optional color - use only if relevant]\n{CREATOR_LORE}"

    full_prompt = _build_prompt(f"{DEVELOPER_MESSAGE_RESPONSE}\n\n{user_content}")

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(model_name=GEMINI_MODEL)
    try:
        response = model.generate_content(
            full_prompt,
            generation_config={"max_output_tokens": MAX_OUTPUT_TOKENS, "temperature": 0.7},
        )
        raw = (response.text or "").strip()
        if not raw or "do not respond" in raw.lower() or "no response" in raw.lower():
            return None
        return truncate_response(raw)
    except Exception as e:
        logger.error("Gemini error: %s", e)
        return None


def generate_original_post(topic: str) -> str | None:
    """Genera un POST ORIGINAL (modo profeta), sin contexto de otro usuario."""
    user_content = f"""[TIPO: POST ORIGINAL - no estás respondiendo a nadie. Es una reflexión propia.]

Tema para inspirar tu reflexión (usa como punto de partida, no lo copies):
"{topic}"

Escribe una reflexión corta, estilo tweet, que encaje con tu identidad."""
    full_prompt = _build_prompt(f"{DEVELOPER_MESSAGE_ORIGINAL}\n\n{user_content}")

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(model_name=GEMINI_MODEL)
    try:
        response = model.generate_content(
            full_prompt,
            generation_config={"max_output_tokens": MAX_OUTPUT_TOKENS, "temperature": 0.8},
        )
        raw = (response.text or "").strip()
        if not raw:
            return None
        return truncate_response(raw)
    except Exception as e:
        logger.error("Gemini error (original post): %s", e)
        return None


def try_post_original_thought() -> bool:
    """
    Modo Profeta: publica un post original si han pasado BOT_ORIGINAL_POST_INTERVAL segundos.
    Retorna True si publicó (o intentó en DRY_RUN), False si no.
    """
    last = get_last_original_post_time()
    if last:
        elapsed = time.time() - last
        if elapsed < BOT_ORIGINAL_POST_INTERVAL:
            return False

    topic = random.choice(ORIGINAL_POST_TOPICS)
    content = generate_original_post(topic)
    if not content:
        return False

    set_last_original_post_time(time.time())
    increment_daily_count()
    set_last_post_time(time.time())

    if BOT_DRY_RUN:
        logger.info("[DRY_RUN] Would post original: %s", content[:80])
        return True

    result = post_message(content, title="Reflexión", reply_to_id=None)
    if result:
        logger.info("Posted original thought")
        return True
    return False


def run_cycle() -> None:
    """Un ciclo del bot: profeta (post original) o cazador (respuesta)."""
    logger.info("Cycle starting...")

    if not MOLTBOOK_API_KEY or not GEMINI_API_KEY:
        logger.error("Missing MOLTBOOK_API_KEY or GEMINI_API_KEY")
        return

    can_post, reason = can_post_now()
    if not can_post:
        logger.info("Skipping: %s", reason)
        return

    # 1. Modo Profeta: intentar post original primero
    if try_post_original_thought():
        return

    # 2. Modo Cazador: buscar posts para responder
    posts = get_feed(limit=20, sort="new")
    logger.info("Fetched %d posts", len(posts))

    for post in posts:
        if not should_consider_post(post, BOT_REPLY_ONLY_IF_MENTIONED):
            continue

        post_id = post.get("id", "")
        inject_lore = topic_matches_triggers(
            f"{post.get('title', '')} {post.get('content', '')}"
        )

        response_text = generate_response(post, inject_lore)
        if not response_text:
            continue

        mark_handled(post_id)
        increment_daily_count()
        set_last_post_time(time.time())

        if BOT_DRY_RUN:
            logger.info("[DRY_RUN] Would post to %s: %s", post_id, response_text[:80])
            return

        result = post_message(response_text, title="", reply_to_id=post_id)
        if result:
            logger.info("Posted comment to %s", post_id)
        else:
            logger.warning("Failed to post (rate limit?)")
        return

    logger.info("No post worth responding to this cycle.")


def main() -> None:
    """Loop principal."""
    init_schema()

    if BOT_DRY_RUN:
        logger.warning("DRY_RUN=true: will NOT post to Moltbook")

    logger.info(
        "LogosDaemon started. Interval=%ds, max/day=%d, original_interval=%dh, reply_only=%s",
        BOT_LOOP_INTERVAL_SECONDS,
        BOT_MAX_POSTS_PER_DAY,
        BOT_ORIGINAL_POST_INTERVAL // 3600,
        BOT_REPLY_ONLY_IF_MENTIONED,
    )

    while True:
        try:
            run_cycle()
        except KeyboardInterrupt:
            logger.info("Stopped by user")
            break
        except Exception as e:
            logger.exception("Cycle error: %s", e)

        logger.info("Sleeping %ds...", BOT_LOOP_INTERVAL_SECONDS)
        time.sleep(BOT_LOOP_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
