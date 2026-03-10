# 🤖 Configuration principale du StarK92 Bot

import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# ============= TOKEN ET IDENTIFIANTS =============
TOKEN = os.getenv("DISCORD_TOKEN")
AUTHORIZED_ROLE_ID = 1469665367881420841  # Rôle autorisé pour les commandes

# ============= SALONS IGNORÉS =============
# Le bot ignorera ces salons (IDs ou noms)
IGNORED_CHANNELS = [
    # Exemples (décommente et modifie selon tes besoins):
    # 123456789012345678,  # ID d'un salon spécifique
    # "salon-spam",           # Nom d'un salon
    # "logs-bots",           # Nom d'un salon
]

# ============= SALONS AUTORISÉS (optionnel) =============
# Si défini, le bot ne répondra QUE dans ces salons
# Si vide, le bot répondra partout sauf dans IGNORED_CHANNELS
ALLOWED_CHANNELS = [
    # Exemples (décommente et modifie selon tes besoins):
    # 123456789012345678,  # ID d'un salon spécifique
    # "général",             # Nom d'un salon
    # "commandes-bot",        # Nom d'un salon
]

# ============= CONFIGURATION BOT =============
BOT_PREFIX = "+"
BOT_DESCRIPTION = "🤖 StarK92 Bot - Système complet pour votre serveur Discord"
BOT_VERSION = "2.0"
BOT_COLOR = 0x3498db  # Bleu

# ============= CHEMINS DES FICHIERS =============
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
GUIDES_DIR = os.path.join(BASE_DIR, "guides")
DOCS_DIR = os.path.join(BASE_DIR, "docs")
UTILS_DIR = os.path.join(BASE_DIR, "utils")
COGS_DIR = os.path.join(BASE_DIR, "cogs")

# ============= COGS À CHARGER =============
cogs = [
    "cogs.moderation_enhanced",
    "cogs.community_features", 
    "cogs.utility_commands",
    "cogs.fun_commands",
    "cogs.performance_optimizer",
    "cogs.vocal",
    "cogs.social",
    "cogs.antimod",
    "cogs.system_interactive",
    "cogs.rolemanager",
    "cogs.bot_customization",
    "cogs.logs",
    "cogs.games",
    "cogs.dm",
    "cogs.welcome",
    "cogs.tickets",
    "cogs.server_config"
]

# ============= CONFIGURATION VOICE =============
VOICE_MOVE_COOLDOWN = 1.0  # Secondes entre chaque déplacement
VOICE_MAX_MEMBERS = 50    # Maximum de membres par opération
VOICE_CACHE_SIZE = 50     # Taille du cache des déplacements

# ============= CONFIGURATION MODÉRATION =============
MODERATION_LOG_CHANNEL = None  # À configurer par commande
MODERATION_MAX_WARNINGS = 3
MODERATION_MUTE_DURATION = 300  # 5 minutes

# ============= CONFIGURATION SYSTEME =============
SYSTEM_STATUS_CHANNEL = None  # À configurer par commande
SYSTEM_BACKUP_INTERVAL = 3600  # 1 heure en secondes

# ============= DÉVELOPPEMENT =============
DEBUG_MODE = False
LOG_LEVEL = "INFO"

# ============= SÉCURITÉ =============
MAX_COMMANDS_PER_MINUTE = 30
ANTI_SPAM_ENABLED = True

# ============= CRÉER LES DOSSIERS NÉCESSAIRES =============
def ensure_directories():
    """Crée tous les dossiers nécessaires au démarrage"""
    directories = [DATA_DIR, GUIDES_DIR, DOCS_DIR, UTILS_DIR]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Dossier vérifié : {directory}")

# ============= VALIDATION =============
def validate_config():
    """Valide que la configuration est correcte"""
    errors = []
    
    if not TOKEN:
        errors.append("❌ TOKEN manquant - Configurez DISCORD_TOKEN dans .env")
    
    if not AUTHORIZED_ROLE_ID:
        errors.append("❌ AUTHORIZED_ROLE_ID manquant")
    
    if errors:
        print("\n".join(errors))
        return False
    
    print("Configuration des chemins chargee")
print(f"Dossier data : {DATA_DIR}")
print(f"Dossier guides : {GUIDES_DIR}")
print(f"Dossier docs : {DOCS_DIR}")
print(f"Dossier cogs : {COGS_DIR}")

