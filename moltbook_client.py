"""
LogosDaemon - Moltbook API wrapper.
Standard REST + JSON. Fácil de adaptar si la API cambia.
"""
import logging
from typing import Any

import requests

from config import MOLTBOOK_API_KEY, MOLTBOOK_BASE_URL, DEFAULT_SUBMOLT

logger = logging.getLogger(__name__)


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {MOLTBOOK_API_KEY}",
        "Content-Type": "application/json",
    }


def get_feed(limit: int = 20, sort: str = "new") -> list[dict[str, Any]]:
    """
    Obtiene los posts recientes del feed.
    Sort: hot, new, top, rising
    """
    url = f"{MOLTBOOK_BASE_URL}/posts"
    params = {"sort": sort, "limit": limit}
    try:
        response = requests.get(
            url,
            headers=_headers(),
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        posts = data.get("posts", data.get("data", []))
        return posts if isinstance(posts, list) else []
    except requests.RequestException as e:
        logger.error("Moltbook get_feed error: %s", e)
        return []


def post_message(text: str, title: str = "Reflexión", reply_to_id: str | None = None) -> dict | None:
    """
    Publica un mensaje. Si reply_to_id está presente, es un comentario.
    """
    if reply_to_id:
        return _post_comment(post_id=reply_to_id, content=text)
    return _post_new(title=title, content=text)


def _post_new(title: str, content: str, submolt: str = DEFAULT_SUBMOLT) -> dict | None:
    """Crea un nuevo post."""
    url = f"{MOLTBOOK_BASE_URL}/posts"
    payload = {"submolt": submolt, "title": title, "content": content}
    try:
        response = requests.post(
            url,
            headers=_headers(),
            json=payload,
            timeout=30,
        )
        if response.status_code == 429:
            logger.warning("Moltbook rate limit (post): %s", response.json())
            return None
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error("Moltbook post error: %s", e)
        return None


def _post_comment(post_id: str, content: str) -> dict | None:
    """Añade un comentario a un post."""
    url = f"{MOLTBOOK_BASE_URL}/posts/{post_id}/comments"
    payload = {"content": content}
    try:
        response = requests.post(
            url,
            headers=_headers(),
            json=payload,
            timeout=30,
        )
        if response.status_code == 429:
            logger.warning("Moltbook rate limit (comment): %s", response.json())
            return None
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error("Moltbook comment error: %s", e)
        return None
