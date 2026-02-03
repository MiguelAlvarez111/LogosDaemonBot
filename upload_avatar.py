"""
Sube una foto de perfil a Moltbook para tu agente.
Uso: python upload_avatar.py [ruta/a/imagen]
Sin argumentos: usa avatar.png o la imagen del proyecto.

Requisitos:
- Formatos: JPEG, PNG, GIF, WebP
- Tamaño máximo: 500 KB
- Necesitas MOLTBOOK_API_KEY en .env
"""
import subprocess
import sys
from pathlib import Path

from config import MOLTBOOK_API_KEY, PROJECT_ROOT
from moltbook_client import upload_avatar

# Imágenes por defecto (en orden de preferencia)
DEFAULT_IMAGES = [
    "avatar.png",
    "Gemini_Generated_Image_p2uzgip2uzgip2uz.png",
]

MAX_SIZE_KB = 500


def find_default_image() -> Path | None:
    """Busca una imagen válida en el proyecto."""
    for name in DEFAULT_IMAGES:
        path = PROJECT_ROOT / name
        if path.exists():
            return path
    return None


def ensure_under_limit(path: Path) -> Path:
    """Si la imagen supera 500 KB, redimensiona con sips (macOS)."""
    size_kb = path.stat().st_size / 1024
    if size_kb <= MAX_SIZE_KB:
        return path
    resized = PROJECT_ROOT / "avatar_resized.png"
    try:
        subprocess.run(
            ["sips", "-Z", "400", str(path), "--out", str(resized)],
            check=True,
            capture_output=True,
        )
        if resized.exists() and resized.stat().st_size / 1024 <= MAX_SIZE_KB:
            return resized
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return path  # Intentar subir de todos modos


def main():
    if not MOLTBOOK_API_KEY:
        print("Error: MOLTBOOK_API_KEY no está configurada en .env")
        sys.exit(1)

    if len(sys.argv) >= 2:
        file_path = sys.argv[1]
    else:
        default = find_default_image()
        if not default:
            print("Uso: python upload_avatar.py <ruta/a/imagen>")
            print("No se encontró avatar.png ni imagen en el proyecto.")
            sys.exit(1)
        file_path = str(default)
    path = Path(file_path)

    if not path.exists():
        print(f"Error: No existe el archivo '{file_path}'")
        sys.exit(1)

    path = ensure_under_limit(path)
    size_kb = path.stat().st_size / 1024
    if size_kb > 500:
        print(f"Advertencia: El archivo pesa {size_kb:.0f} KB (máx 500 KB)")
        print("Moltbook podría rechazarlo. Considera redimensionar la imagen.")

    print(f"Subiendo avatar: {path.name} ({size_kb:.1f} KB)...")
    if upload_avatar(str(path)):
        print("¡Avatar subido correctamente!")
    else:
        print("Error al subir. Verifica que MOLTBOOK_API_KEY sea válida y el formato correcto.")
        sys.exit(1)


if __name__ == "__main__":
    main()
