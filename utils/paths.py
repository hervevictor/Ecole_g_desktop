import sys
import os


def get_app_dir() -> str:
    """
    Retourne le dossier où stocker les données persistantes (DB, avatars…).
    - Mode .app / .exe : dossier utilisateur permanent (survit aux mises à jour)
    - Mode développement : racine du projet
    """
    if getattr(sys, 'frozen', False):
        # Application bundlée — stocker en dehors du bundle pour persister
        if sys.platform == 'darwin':
            base = os.path.expanduser('~/Library/Application Support/G-Ecole')
        elif sys.platform == 'win32':
            base = os.path.join(
                os.environ.get('APPDATA', os.path.expanduser('~')), 'G-Ecole'
            )
        else:
            base = os.path.expanduser('~/.g-ecole')
        os.makedirs(base, exist_ok=True)
        return base

    # Mode développement : racine du projet
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
