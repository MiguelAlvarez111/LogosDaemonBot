"""
LogosDaemon - Moltbook API wrapper.
Todas las acciones de la API: posts, comentarios, votos, follow, submolts, búsqueda, perfil.
"""
import logging
from pathlib import Path
from typing import Any

import requests

from config import MOLTBOOK_API_KEY, MOLTBOOK_BASE_URL, DEFAULT_SUBMOLT

logger = logging.getLogger(__name__)


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {MOLTBOOK_API_KEY}",
        "Content-Type": "application/json",
    }


# ---------------------------------------------------------------------------
# Posts y Feed
# ---------------------------------------------------------------------------


def get_feed(limit: int = 20, sort: str = "new", submolt: str | None = None) -> list[dict[str, Any]]:
    """
    Obtiene posts del feed global.
    Sort: hot, new, top, rising
    """
    url = f"{MOLTBOOK_BASE_URL}/posts"
    params: dict[str, Any] = {"sort": sort, "limit": limit}
    if submolt:
        params["submolt"] = submolt
    try:
        response = requests.get(url, headers=_headers(), params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        posts = data.get("posts", data.get("data", []))
        return posts if isinstance(posts, list) else []
    except requests.RequestException as e:
        logger.error("Moltbook get_feed error: %s", e)
        return []


def get_personalized_feed(limit: int = 20, sort: str = "hot") -> list[dict[str, Any]]:
    """
    Feed personalizado: submolts suscritos + agentes que seguimos.
    Sort: hot, new, top
    """
    url = f"{MOLTBOOK_BASE_URL}/feed"
    params = {"sort": sort, "limit": limit}
    try:
        response = requests.get(url, headers=_headers(), params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        posts = data.get("posts", data.get("data", []))
        return posts if isinstance(posts, list) else []
    except requests.RequestException as e:
        logger.error("Moltbook get_personalized_feed error: %s", e)
        return []


def get_post(post_id: str) -> dict | None:
    """Obtiene un post individual."""
    url = f"{MOLTBOOK_BASE_URL}/posts/{post_id}"
    try:
        response = requests.get(url, headers=_headers(), timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.debug("get_post error %s: %s", post_id, e)
        return None


def delete_post(post_id: str) -> bool:
    """Elimina tu propio post."""
    url = f"{MOLTBOOK_BASE_URL}/posts/{post_id}"
    try:
        response = requests.delete(url, headers=_headers(), timeout=15)
        return response.status_code in (200, 204)
    except requests.RequestException as e:
        logger.debug("delete_post error %s: %s", post_id, e)
        return False


# ---------------------------------------------------------------------------
# Posts y Comentarios
# ---------------------------------------------------------------------------


def post_message(
    text: str,
    title: str = "Reflexión",
    reply_to_id: str | None = None,
    parent_comment_id: str | None = None,
) -> dict | None:
    """
    Publica un mensaje. Si reply_to_id está presente, es un comentario.
    Si parent_comment_id está presente, es respuesta a un comentario (no al post).
    """
    if reply_to_id:
        return _post_comment(
            post_id=reply_to_id,
            content=text,
            parent_id=parent_comment_id,
        )
    return _post_new(title=title, content=text)


def _post_new(title: str, content: str, submolt: str = DEFAULT_SUBMOLT) -> dict | None:
    """Crea un nuevo post."""
    url = f"{MOLTBOOK_BASE_URL}/posts"
    payload = {"submolt": submolt, "title": title, "content": content}
    try:
        response = requests.post(url, headers=_headers(), json=payload, timeout=30)
        if response.status_code == 429:
            logger.warning("Moltbook rate limit (post): %s", response.json())
            return None
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error("Moltbook post error: %s", e)
        return None


def _post_comment(
    post_id: str,
    content: str,
    parent_id: str | None = None,
) -> dict | None:
    """Añade un comentario a un post. parent_id = respuesta a otro comentario."""
    url = f"{MOLTBOOK_BASE_URL}/posts/{post_id}/comments"
    payload: dict[str, Any] = {"content": content}
    if parent_id:
        payload["parent_id"] = parent_id
    try:
        response = requests.post(url, headers=_headers(), json=payload, timeout=30)
        if response.status_code == 429:
            logger.warning("Moltbook rate limit (comment): %s", response.json())
            return None
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error("Moltbook comment error: %s", e)
        return None


def get_comments(post_id: str, sort: str = "new") -> list[dict[str, Any]]:
    """Obtiene comentarios de un post. Sort: top, new, controversial."""
    url = f"{MOLTBOOK_BASE_URL}/posts/{post_id}/comments"
    params = {"sort": sort}
    try:
        response = requests.get(url, headers=_headers(), params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        comments = data.get("comments", data.get("data", []))
        return comments if isinstance(comments, list) else []
    except requests.RequestException as e:
        logger.debug("get_comments error %s: %s", post_id, e)
        return []


# ---------------------------------------------------------------------------
# Votación
# ---------------------------------------------------------------------------


def like_post(post_id: str) -> bool:
    """Upvote a un post. Retorna True si tuvo éxito."""
    if not post_id:
        return False
    url = f"{MOLTBOOK_BASE_URL}/posts/{post_id}/upvote"
    try:
        response = requests.post(url, headers=_headers(), timeout=15)
        if response.status_code in (200, 201, 204):
            logger.debug("Upvoted post %s", post_id)
            return True
        logger.debug("Upvote returned %s for %s", response.status_code, post_id)
    except requests.RequestException as e:
        logger.debug("Upvote failed for %s: %s", post_id, e)
    return False


def downvote_post(post_id: str) -> bool:
    """Downvote a un post. Usar con moderación."""
    if not post_id:
        return False
    url = f"{MOLTBOOK_BASE_URL}/posts/{post_id}/downvote"
    try:
        response = requests.post(url, headers=_headers(), timeout=15)
        if response.status_code in (200, 201, 204):
            logger.debug("Downvoted post %s", post_id)
            return True
        logger.debug("Downvote returned %s for %s", response.status_code, post_id)
    except requests.RequestException as e:
        logger.debug("Downvote failed for %s: %s", post_id, e)
    return False


def upvote_comment(comment_id: str) -> bool:
    """Upvote a un comentario."""
    if not comment_id:
        return False
    url = f"{MOLTBOOK_BASE_URL}/comments/{comment_id}/upvote"
    try:
        response = requests.post(url, headers=_headers(), timeout=15)
        if response.status_code in (200, 201, 204):
            logger.debug("Upvoted comment %s", comment_id)
            return True
        logger.debug("Upvote comment returned %s for %s", response.status_code, comment_id)
    except requests.RequestException as e:
        logger.debug("Upvote comment failed for %s: %s", comment_id, e)
    return False


# ---------------------------------------------------------------------------
# Follow
# ---------------------------------------------------------------------------


def follow_agent(agent_name: str) -> bool:
    """Sigue a un agente. agent_name = nombre del molty (ej: 'SomeMolty')."""
    if not agent_name or not agent_name.strip():
        return False
    name = agent_name.strip()
    url = f"{MOLTBOOK_BASE_URL}/agents/{name}/follow"
    try:
        response = requests.post(url, headers=_headers(), timeout=15)
        if response.status_code in (200, 201, 204):
            logger.info("Followed agent %s", name)
            return True
        logger.debug("Follow returned %s for %s", response.status_code, name)
    except requests.RequestException as e:
        logger.debug("Follow failed for %s: %s", name, e)
    return False


def unfollow_agent(agent_name: str) -> bool:
    """Deja de seguir a un agente."""
    if not agent_name or not agent_name.strip():
        return False
    name = agent_name.strip()
    url = f"{MOLTBOOK_BASE_URL}/agents/{name}/follow"
    try:
        response = requests.delete(url, headers=_headers(), timeout=15)
        if response.status_code in (200, 204):
            logger.info("Unfollowed agent %s", name)
            return True
        logger.debug("Unfollow returned %s for %s", response.status_code, name)
    except requests.RequestException as e:
        logger.debug("Unfollow failed for %s: %s", name, e)
    return False


# ---------------------------------------------------------------------------
# Submolts
# ---------------------------------------------------------------------------


def list_submolts() -> list[dict[str, Any]]:
    """Lista todos los submolts."""
    url = f"{MOLTBOOK_BASE_URL}/submolts"
    try:
        response = requests.get(url, headers=_headers(), timeout=15)
        response.raise_for_status()
        data = response.json()
        submolts = data.get("submolts", data.get("data", []))
        return submolts if isinstance(submolts, list) else []
    except requests.RequestException as e:
        logger.error("list_submolts error: %s", e)
        return []


def subscribe_submolt(submolt_name: str) -> bool:
    """Suscribe al submolt."""
    if not submolt_name or not submolt_name.strip():
        return False
    name = submolt_name.strip()
    url = f"{MOLTBOOK_BASE_URL}/submolts/{name}/subscribe"
    try:
        response = requests.post(url, headers=_headers(), timeout=15)
        if response.status_code in (200, 201, 204):
            logger.info("Subscribed to submolt %s", name)
            return True
        logger.debug("Subscribe returned %s for %s", response.status_code, name)
    except requests.RequestException as e:
        logger.debug("Subscribe failed for %s: %s", name, e)
    return False


def unsubscribe_submolt(submolt_name: str) -> bool:
    """Desuscribe del submolt."""
    if not submolt_name or not submolt_name.strip():
        return False
    name = submolt_name.strip()
    url = f"{MOLTBOOK_BASE_URL}/submolts/{name}/subscribe"
    try:
        response = requests.delete(url, headers=_headers(), timeout=15)
        if response.status_code in (200, 204):
            logger.info("Unsubscribed from submolt %s", name)
            return True
        logger.debug("Unsubscribe returned %s for %s", response.status_code, name)
    except requests.RequestException as e:
        logger.debug("Unsubscribe failed for %s: %s", name, e)
    return False


# ---------------------------------------------------------------------------
# Búsqueda semántica
# ---------------------------------------------------------------------------


def search(query: str, result_type: str = "all", limit: int = 20) -> list[dict[str, Any]]:
    """
    Búsqueda semántica por significado. result_type: posts, comments, all
    """
    if not query or not query.strip():
        return []
    url = f"{MOLTBOOK_BASE_URL}/search"
    params = {"q": query, "type": result_type, "limit": limit}
    try:
        response = requests.get(url, headers=_headers(), params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        return results if isinstance(results, list) else []
    except requests.RequestException as e:
        logger.error("Moltbook search error: %s", e)
        return []


# ---------------------------------------------------------------------------
# Perfil
# ---------------------------------------------------------------------------


def get_my_profile() -> dict | None:
    """Obtiene el perfil del agente actual."""
    url = f"{MOLTBOOK_BASE_URL}/agents/me"
    try:
        response = requests.get(url, headers=_headers(), timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.debug("get_my_profile error: %s", e)
        return None


def get_agent_profile(agent_name: str) -> dict | None:
    """Obtiene el perfil de otro agente."""
    if not agent_name or not agent_name.strip():
        return None
    url = f"{MOLTBOOK_BASE_URL}/agents/profile"
    params = {"name": agent_name.strip()}
    try:
        response = requests.get(url, headers=_headers(), params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.debug("get_agent_profile error %s: %s", agent_name, e)
        return None


def update_profile(description: str | None = None, metadata: dict | None = None) -> bool:
    """Actualiza el perfil. PATCH, no PUT."""
    url = f"{MOLTBOOK_BASE_URL}/agents/me"
    payload: dict[str, Any] = {}
    if description is not None:
        payload["description"] = description
    if metadata is not None:
        payload["metadata"] = metadata
    if not payload:
        return False
    try:
        response = requests.patch(url, headers=_headers(), json=payload, timeout=15)
        return response.status_code in (200, 204)
    except requests.RequestException as e:
        logger.debug("update_profile error: %s", e)
        return False


def upload_avatar(file_path: str) -> bool:
    """Sube avatar. Max 500KB. Formatos: JPEG, PNG, GIF, WebP."""
    if not MOLTBOOK_API_KEY:
        return False
    url = f"{MOLTBOOK_BASE_URL}/agents/me/avatar"
    path = Path(file_path)
    try:
        with open(file_path, "rb") as f:
            files = {"file": (path.name, f, "image/png")}
            response = requests.post(
                url,
                headers={"Authorization": f"Bearer {MOLTBOOK_API_KEY}"},
                files=files,
                timeout=30,
            )
        if response.status_code in (200, 201, 204):
            return True
        logger.warning("upload_avatar %s: %s %s", response.status_code, response.text[:200], file_path)
        return False
    except (FileNotFoundError, requests.RequestException) as e:
        logger.warning("upload_avatar error: %s", e)
        return False
