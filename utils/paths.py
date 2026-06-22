import sys
import os


def get_app_dir() -> str:
    """Retourne le dossier racine de l'app (compatible PyInstaller bundle)."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
