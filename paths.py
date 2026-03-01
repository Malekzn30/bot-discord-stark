# 📁 Configuration des chemins du bot

import os

# Chemins de base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
GUIDES_DIR = os.path.join(BASE_DIR, "guides")
DOCS_DIR = os.path.join(BASE_DIR, "docs")
UTILS_DIR = os.path.join(BASE_DIR, "utils")
COGS_DIR = os.path.join(BASE_DIR, "cogs")

# Chemins des fichiers de données
TICKETS_CONFIG_PATH = os.path.join(DATA_DIR, "tickets_config.json")
TICKETS_DATA_PATH = os.path.join(DATA_DIR, "tickets_data.json")
TICKETS_PANELS_PATH = os.path.join(DATA_DIR, "tickets_panels.json")

# Chemins des guides
TICKETS_GUIDE_PATH = os.path.join(GUIDES_DIR, "TICKETS_GUIDE.md")
VOICE_GUIDE_PATH = os.path.join(GUIDES_DIR, "VOICE_GUIDE.md")

# Assurer que les dossiers existent
for directory in [DATA_DIR, GUIDES_DIR, DOCS_DIR, UTILS_DIR]:
    os.makedirs(directory, exist_ok=True)

print("Configuration des chemins chargee")
print(f"Dossier data : {DATA_DIR}")
print(f"Dossier guides : {GUIDES_DIR}")
print(f"Dossier docs : {DOCS_DIR}")
print(f"Dossier cogs : {COGS_DIR}")
