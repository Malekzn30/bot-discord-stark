import logging
import os
from datetime import datetime

# Créer le dossier logs s'il n'existe pas
LOGS_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

# Configuration du logging
def setup_logging():
    """Configurer le système de logs"""
    
    # Nom du fichier avec la date du jour
    log_filename = f"bot_{datetime.now().strftime('%Y%m%d')}.log"
    log_filepath = os.path.join(LOGS_DIR, log_filename)
    
    # Configuration du logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filepath, encoding='utf-8'),
            logging.StreamHandler()  # Aussi dans la console
        ]
    )
    
    # Créer un logger spécifique pour le bot
    logger = logging.getLogger('BotStark')
    
    return logger

# Fonction pour logger les événements de bienvenue
def log_welcome(member, action, details=""):
    """Logger les événements de bienvenue"""
    logger = logging.getLogger('BotStark')
    
    if action == "join":
        logger.info(f"JOIN - {member.name} (ID: {member.id}) a rejoint {member.guild.name}")
    elif action == "public_sent":
        logger.info(f"WELCOME_PUBLIC - Message envoyé dans {details}")
    elif action == "public_error":
        logger.error(f"WELCOME_PUBLIC_ERROR - {details}")
    elif action == "dm_attempt":
        logger.info(f"WELCOME_DM - Tentative DM à {member.name}")
    elif action == "dm_sent":
        logger.info(f"WELCOME_DM - DM envoyé à {member.name}")
    elif action == "dm_blocked":
        logger.warning(f"WELCOME_DM_BLOCKED - DM bloqué pour {member.name} - {details}")
    elif action == "dm_error":
        logger.error(f"WELCOME_DM_ERROR - {member.name} - {details}")

# Fonction pour logger les commandes
def log_command(ctx, command_name, details=""):
    """Logger les commandes utilisées"""
    logger = logging.getLogger('BotStark')
    
    logger.info(f"COMMAND - {ctx.author.name} a utilisé +{command_name} dans #{ctx.channel.name} - {details}")

# Fonction pour logger les erreurs
def log_error(error_type, details):
    """Logger les erreurs"""
    logger = logging.getLogger('BotStark')
    
    logger.error(f"ERROR - {error_type} - {details}")

# Fonction pour logger les événements vocaux
def log_voice(action, details=""):
    """Logger les événements vocaux"""
    logger = logging.getLogger('BotStark')
    
    logger.info(f"VOICE - {action} - {details}")
