"""
LogosDaemon - PostgreSQL memory store.
Dedupe, daily count, last post time.
Usa DATABASE_URL para la conexión (Railway provee esta variable).
"""
import datetime
import logging
import os
import time

import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

MAX_HANDLED_IDS = 50


def _get_database_url() -> str:
    """Obtiene DATABASE_URL. Lanza error claro si no está configurada."""
    url = os.getenv("DATABASE_URL")
    if not url or not url.strip():
        raise ValueError(
            "DATABASE_URL no está configurada. "
            "En Railway: añade un servicio PostgreSQL y la variable se inyecta automáticamente. "
            "Local: define DATABASE_URL en .env (ej: postgresql://user:pass@localhost:5432/dbname)"
        )
    # Railway suele dar postgres://, psycopg2 prefiere postgresql://
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


def _get_conn():
    """Crea una conexión a PostgreSQL."""
    return psycopg2.connect(_get_database_url())


def init_schema() -> None:
    """Crea las tablas si no existen."""
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS handled_posts (
                    post_id TEXT PRIMARY KEY,
                    handled_at DOUBLE PRECISION NOT NULL
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS bot_state (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at DOUBLE PRECISION NOT NULL
                )
            """)
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        logger.error("init_schema error: %s", e)
        raise
    finally:
        conn.close()


def already_handled(post_id: str) -> bool:
    """True si ya respondimos a este post."""
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM handled_posts WHERE post_id = %s",
                (post_id,),
            )
            return cur.fetchone() is not None
    finally:
        conn.close()


def mark_handled(post_id: str) -> None:
    """Registra que respondimos a este post. Prune si hay demasiados."""
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO handled_posts (post_id, handled_at)
                VALUES (%s, %s)
                ON CONFLICT (post_id) DO UPDATE SET handled_at = EXCLUDED.handled_at
            """, (post_id, time.time()))
            # Prune: mantener solo los últimos MAX_HANDLED_IDS
            cur.execute("""
                DELETE FROM handled_posts
                WHERE post_id IN (
                    SELECT post_id FROM handled_posts
                    ORDER BY handled_at DESC
                    OFFSET %s
                )
            """, (MAX_HANDLED_IDS,))
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        logger.error("mark_handled error: %s", e)
        raise
    finally:
        conn.close()


def get_state(key: str) -> str | None:
    """Obtiene un valor de estado."""
    conn = _get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT value FROM bot_state WHERE key = %s",
                (key,),
            )
            row = cur.fetchone()
            return row["value"] if row else None
    finally:
        conn.close()


def set_state(key: str, value: str) -> None:
    """Guarda un valor de estado."""
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO bot_state (key, value, updated_at)
                VALUES (%s, %s, %s)
                ON CONFLICT (key) DO UPDATE SET
                    value = EXCLUDED.value,
                    updated_at = EXCLUDED.updated_at
            """, (key, value, time.time()))
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        logger.error("set_state error: %s", e)
        raise
    finally:
        conn.close()


def get_last_post_time() -> float | None:
    """Timestamp del último post."""
    val = get_state("last_post_time")
    return float(val) if val else None


def set_last_post_time(ts: float) -> None:
    set_state("last_post_time", str(ts))


def get_daily_count() -> int:
    """Posts/comments hoy."""
    val = get_state("daily_count")
    return int(val) if val else 0


def get_daily_count_date() -> str | None:
    """Fecha del día actual del contador (YYYY-MM-DD)."""
    return get_state("daily_count_date")


def increment_daily_count() -> None:
    """Incrementa el contador diario. Resetea si es nuevo día."""
    today = datetime.date.today().isoformat()
    if get_daily_count_date() != today:
        set_state("daily_count", "1")
        set_state("daily_count_date", today)
    else:
        n = get_daily_count() + 1
        set_state("daily_count", str(n))


def get_last_original_post_time() -> float | None:
    """Timestamp del último post original (modo profeta)."""
    val = get_state("last_original_post_time")
    return float(val) if val else None


def set_last_original_post_time(ts: float) -> None:
    set_state("last_original_post_time", str(ts))
