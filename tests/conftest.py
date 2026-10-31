import sys
from pathlib import Path

# Récupère le dossier racine du projet (deux niveaux au-dessus de conftest.py ou un niveau au-dessus du dossier tests)
root_dir = Path(__file__).resolve().parent.parent

# Ajoute la racine au chemin d'importation de Python
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))