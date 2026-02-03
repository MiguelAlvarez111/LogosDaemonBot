"""
Moltbook Bot - Gemelo Digital
Bot que publica y comenta en Moltbook usando Gemini como cerebro.
"""
import os
import time
import logging

import google.generativeai as genai
import requests

from config import (
    GEMINI_API_KEY,
    MOLTBOOK_API_KEY,
    MOLTBOOK_API_BASE,
    LOOP_INTERVAL_HOURS,
    DEFAULT_SUBMOLT,
)
from system_prompt import SYSTEM_PROMPT

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def validate_env():
    """Valida que las variables de entorno necesarias estén configuradas."""
    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY no está configurada. "
            "Configúrala en Railway o en un archivo .env"
        )
    if not MOLTBOOK_API_KEY:
        raise ValueError(
            "MOLTBOOK_API_KEY no está configurada. "
            "Regístrate en https://www.moltbook.com y obtén tu API key."
        )


def init_gemini():
    """Inicializa el modelo Gemini con el system prompt."""
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=SYSTEM_PROMPT,
    )
    return model


# ─────────────────────────────────────────────────────────────────────────────
# Moltbook API
# ─────────────────────────────────────────────────────────────────────────────


def get_moltbook_headers():
    """Headers para todas las peticiones a Moltbook."""
    return {
        "Authorization": f"Bearer {MOLTBOOK_API_KEY}",
        "Content-Type": "application/json",
    }


def fetch_recent_posts(sort="hot", limit=25):
    """
    Obtiene los posts recientes del feed de Moltbook.
    Sort: hot, new, top, rising
    """
    url = f"{MOLTBOOK_API_BASE}/posts"
    params = {"sort": sort, "limit": limit}
    try:
        response = requests.get(
            url,
            headers=get_moltbook_headers(),
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("posts", data.get("data", [])) if isinstance(data, dict) else data
    except requests.RequestException as e:
        logger.error("Error al obtener posts de Moltbook: %s", e)
        return []


def create_post(title: str, content: str, submolt: str = DEFAULT_SUBMOLT):
    """Publica un nuevo post en Moltbook."""
    url = f"{MOLTBOOK_API_BASE}/posts"
    payload = {"submolt": submolt, "title": title, "content": content}
    try:
        response = requests.post(
            url,
            headers=get_moltbook_headers(),
            json=payload,
            timeout=30,
        )
        if response.status_code == 429:
            retry = response.json().get("retry_after_minutes", 30)
            logger.warning("Rate limit: 1 post cada 30 min. Reintentar en %s min", retry)
            return None
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error("Error al publicar en Moltbook: %s", e)
        return None


def create_comment(post_id: str, content: str):
    """Añade un comentario a un post."""
    url = f"{MOLTBOOK_API_BASE}/posts/{post_id}/comments"
    payload = {"content": content}
    try:
        response = requests.post(
            url,
            headers=get_moltbook_headers(),
            json=payload,
            timeout=30,
        )
        if response.status_code == 429:
            retry = response.json().get("retry_after_seconds", 20)
            logger.warning("Rate limit comentarios. Reintentar en %s seg", retry)
            return None
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error("Error al comentar en Moltbook: %s", e)
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Lógica del Bot
# ─────────────────────────────────────────────────────────────────────────────


def choose_action_and_topic(posts: list, model) -> tuple[str, dict | None]:
    """
    Usa Gemini para elegir: publicar post nuevo O comentar en uno existente.
    Retorna: ("post", None) o ("comment", post_dict)
    """
    if not posts:
        return "post", None

    posts_summary = "\n\n".join(
        f"- ID: {p.get('id', '?')} | Título: {p.get('title', 'Sin título')[:80]} | "
        f"Contenido: {p.get('content', '')[:150]}..."
        for p in posts[:15]
    )

    prompt = f"""Estos son los posts recientes en Moltbook:

{posts_summary}

Basándote en tu personalidad y los temas que te interesan:
1. ¿Tienes algo original que aportar como POST nuevo? (una reflexión, pregunta o idea que no encaje como respuesta)
2. ¿Hay algún post donde tu comentario añadiría valor genuino?

Responde EXACTAMENTE en este formato (sin explicaciones adicionales):
ACCION: post
TITULO: [título corto si es post, o vacío]
CONTENIDO: [tu texto]

O si prefieres comentar:
ACCION: comment
POST_ID: [el id del post]
CONTENIDO: [tu comentario, max 280 caracteres]

Si no hay nada que aportar genuinamente, responde:
ACCION: skip
"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip().upper()

        if "ACCION: SKIP" in text:
            return "skip", None

        if "ACCION: COMMENT" in text:
            lines = response.text.strip().split("\n")
            post_id = None
            content = ""
            for line in lines:
                if line.upper().startswith("POST_ID:"):
                    post_id = line.split(":", 1)[1].strip()
                elif line.upper().startswith("CONTENIDO:"):
                    content = line.split(":", 1)[1].strip()
            if post_id and content:
                target = next((p for p in posts if str(p.get("id")) == post_id), posts[0])
                return "comment", {"post": target, "content": content}
            # Fallback: comentar en el primer post interesante
            return "comment", {"post": posts[0], "content": content or "Interesante reflexión."}

        if "ACCION: POST" in text:
            lines = response.text.strip().split("\n")
            title = "Reflexión"
            content = ""
            for line in lines:
                if line.upper().startswith("TITULO:"):
                    title = line.split(":", 1)[1].strip() or "Reflexión"
                elif line.upper().startswith("CONTENIDO:"):
                    content = line.split(":", 1)[1].strip()
            if content:
                return "post", {"title": title, "content": content}

    except Exception as e:
        logger.error("Error al elegir acción con Gemini: %s", e)

    return "skip", None


def run_cycle(model):
    """Ejecuta un ciclo completo: leer feed, elegir, generar, publicar."""
    logger.info("Iniciando ciclo...")

    # 1. Leer posts recientes
    posts = fetch_recent_posts(sort="new", limit=20)
    logger.info("Posts obtenidos: %d", len(posts))

    # 2. Elegir acción y tema
    action, data = choose_action_and_topic(posts, model)
    if action == "skip":
        logger.info("No hay nada que aportar en este ciclo. Saltando.")
        return

    # 3. Publicar
    if action == "post" and data:
        result = create_post(
            title=data["title"],
            content=data["content"],
            submolt=DEFAULT_SUBMOLT,
        )
        if result:
            logger.info("Post publicado: %s", data["title"][:50])
        else:
            logger.warning("No se pudo publicar (posible rate limit)")

    elif action == "comment" and data:
        post = data["post"]
        post_id = post.get("id")
        content = data.get("content", "")
        if not content:
            # Generar comentario con Gemini
            try:
                resp = model.generate_content(
                    f"Post: {post.get('title', '')} - {post.get('content', '')[:300]}\n\n"
                    "Escribe un comentario breve (max 280 chars) que aporte valor. Solo el texto."
                )
                content = resp.text.strip()[:280]
            except Exception as e:
                logger.error("Error generando comentario: %s", e)
                return
        result = create_comment(post_id, content)
        if result:
            logger.info("Comentario publicado en post %s", post_id)
        else:
            logger.warning("No se pudo comentar (posible rate limit)")


def main():
    """Punto de entrada: valida, inicializa y ejecuta el loop."""
    validate_env()
    model = init_gemini()

    interval_seconds = LOOP_INTERVAL_HOURS * 3600
    logger.info(
        "Bot iniciado. Intervalo: %d horas. Ctrl+C para detener.",
        LOOP_INTERVAL_HOURS,
    )

    while True:
        try:
            run_cycle(model)
        except KeyboardInterrupt:
            logger.info("Detenido por el usuario.")
            break
        except Exception as e:
            logger.exception("Error en ciclo: %s", e)

        logger.info("Esperando %d horas hasta el próximo ciclo...", LOOP_INTERVAL_HOURS)
        time.sleep(interval_seconds)


if __name__ == "__main__":
    main()
