"""
LogosDaemon - Configuración y variables de entorno.
Safe defaults para evitar costos descontrolados.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

# Moltbook
MOLTBOOK_API_KEY = os.getenv("MOLTBOOK_API_KEY")
MOLTBOOK_BASE_URL = os.getenv("MOLTBOOK_BASE_URL", "https://www.moltbook.com/api/v1")
MOLTBOOK_AGENT_ID = os.getenv("MOLTBOOK_AGENT_ID", "")  # Opcional, para logging

# Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# Rate limits - evitar spam y costos
BOT_MAX_POSTS_PER_DAY = int(os.getenv("BOT_MAX_POSTS_PER_DAY", "12"))
BOT_MIN_SECONDS_BETWEEN_POSTS = int(os.getenv("BOT_MIN_SECONDS_BETWEEN_POSTS", "600"))
BOT_MAX_CONTEXT_CHARS = int(os.getenv("BOT_MAX_CONTEXT_CHARS", "2500"))
BOT_REPLY_ONLY_IF_MENTIONED = os.getenv("BOT_REPLY_ONLY_IF_MENTIONED", "true").lower() == "true"
BOT_DRY_RUN = os.getenv("BOT_DRY_RUN", "true").lower() == "true"
BOT_LOOP_INTERVAL_SECONDS = int(os.getenv("BOT_LOOP_INTERVAL_SECONDS", "300"))  # 5 min check

# Modo Profeta: posts originales
BOT_ORIGINAL_POST_INTERVAL = int(os.getenv("BOT_ORIGINAL_POST_INTERVAL", "3600"))  # 1 hora en segundos (posts originales)

# Modo Cazador: responder sin mención
BOT_HUNTER_RANDOM_CHANCE = float(os.getenv("BOT_HUNTER_RANDOM_CHANCE", "0.3"))  # 30% de candidatos válidos
BOT_HUNTER_MIN_CHARS = int(os.getenv("BOT_HUNTER_MIN_CHARS", "60"))  # mínimo caracteres para considerar
BOT_AGENT_NAMES = ["LogosDaemon", "LogosDaemonBot"]  # no responder a posts propios

# Submolt por defecto
DEFAULT_SUBMOLT = os.getenv("DEFAULT_SUBMOLT", "general")

# Longitud de respuestas
BOT_MAX_RESPONSE_LINES = int(os.getenv("BOT_MAX_RESPONSE_LINES", "8"))
BOT_MAX_RESPONSE_CHARS = int(os.getenv("BOT_MAX_RESPONSE_CHARS", "600"))
BOT_MAX_OUTPUT_TOKENS = int(os.getenv("BOT_MAX_OUTPUT_TOKENS", "400"))

# Logging
BOT_LOG_LEVEL = os.getenv("BOT_LOG_LEVEL", "INFO")

# Paths
PROJECT_ROOT = Path(__file__).parent

# PostgreSQL (Railway provee DATABASE_URL automáticamente)
DATABASE_URL = os.getenv("DATABASE_URL")
