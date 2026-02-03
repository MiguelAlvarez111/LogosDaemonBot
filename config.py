"""
Configuración del bot - Variables de entorno y constantes.
Usa variables de entorno para las API Keys (nunca hardcodear).
"""
import os

from dotenv import load_dotenv
load_dotenv()  # Carga .env en desarrollo local

# API Keys (desde variables de entorno)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MOLTBOOK_API_KEY = os.getenv("MOLTBOOK_API_KEY")

# Moltbook API
MOLTBOOK_API_BASE = "https://www.moltbook.com/api/v1"

# Intervalo del loop (en horas)
LOOP_INTERVAL_HOURS = int(os.getenv("LOOP_INTERVAL_HOURS", "4"))

# Submolt por defecto para publicar
DEFAULT_SUBMOLT = os.getenv("DEFAULT_SUBMOLT", "general")
