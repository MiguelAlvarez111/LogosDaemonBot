"""
Diagnóstico rápido de MOLTBOOK_API_KEY.
Ejecuta: python check_moltbook_key.py
"""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

key = os.getenv("MOLTBOOK_API_KEY")

print("=== Diagnóstico MOLTBOOK_API_KEY ===\n")
print("Key presente:", bool(key))
if key:
    print("Longitud:", len(key))
    print("Empieza con:", repr(key[:25]) + "...")
    print("Termina con:", "..." + repr(key[-5:]))
    print("Espacios al inicio/fin:", key != key.strip())
    print("Tiene newline:", "\\n" in key or "\\r" in key)
else:
    print("No hay MOLTBOOK_API_KEY en .env")
    sys.exit(1)

print("\n=== Probando API ===\n")

import requests

# Probar con key limpia (sin espacios)
clean_key = key.strip()
url = "https://www.moltbook.com/api/v1/agents/me"
headers = {"Authorization": f"Bearer {clean_key}"}

r = requests.get(url, headers=headers, timeout=15)
print("URL:", url)
print("Status:", r.status_code)
print("Response:", r.text[:300] if r.text else "(vacío)")

if r.status_code == 200:
    data = r.json()
    name = data.get("name") or (data.get("agent", {}).get("name") if isinstance(data.get("agent"), dict) else None)
    print("\n✓ Key válida. Bot:", name)
else:
    print("\n✗ Key rechazada. Revisa que sea la correcta para LogosDaemonBot.")
