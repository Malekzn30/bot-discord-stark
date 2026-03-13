import nextcord
from nextcord.ext import commands, tasks
import threading
from flask import Flask
import os
import time
import requests
import asyncio
from dotenv import load_dotenv
import gc
from cog_manager import setup_cog_manager
import config

# Charger les variables d'environnement
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# ============================
# FONCTIONS DE VÉRIFICATION DES SALONS
# ============================

def is_channel_allowed(channel):
    """Vérifie si le bot peut répondre dans ce salon"""
    if not channel:
        return False
    
    channel_id = channel.id
    channel_name = channel.name.lower()
    
    # Vérifier les salons ignorés (par ID ou par nom)
    for ignored in config.IGNORED_CHANNELS:
        if isinstance(ignored, int) and ignored == channel_id:
            return False
        elif isinstance(ignored, str) and ignored.lower() == channel_name:
            return False
    
    # Si ALLOWED_CHANNELS est défini, vérifier que le salon est autorisé
    if config.ALLOWED_CHANNELS:
        for allowed in config.ALLOWED_CHANNELS:
            if isinstance(allowed, int) and allowed == channel_id:
                return True
            elif isinstance(allowed, str) and allowed.lower() == channel_name:
                return True
        return False  # Salon pas dans la liste autorisée
    
    return True  # Salon autorisé par défaut

# ============================
# DISCORD BOT - OPTIMISÉ RENDER
# ============================

# Intents optimisés
intents = nextcord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.presences = False
intents.typing = False

bot = commands.Bot(
    command_prefix="+",
    intents=intents,
    help_command=None,
    chunk_guilds_at_startup=False
)

bot.start_time = time.time()

# ============================
# EVENTS
# ============================

@bot.event
async def on_ready():
    print(f"[READY] Bot connecté : {bot.user}")
    cleanup_aggressive.start()

@bot.event
async def on_message(message):
    """Vérifie si le bot peut répondre dans ce salon et gère les réactions automatiques"""
    # Ignorer les messages du bot lui-même
    if message.author == bot.user:
        return
    
    # Vérifier si le salon est autorisé
    if not is_channel_allowed(message.channel):
        return
    
    # Gérer les réactions automatiques
    await handle_auto_reactions(message)
    
    # Laisser le bot traiter les commandes normalement
    await bot.process_commands(message)

async def handle_auto_reactions(message):
    """Gère les réactions automatiques dans les salons configurés"""
    channel_id_str = str(message.channel.id)
    
    if channel_id_str in config.AUTO_REACT_CHANNELS:
        emojis = config.AUTO_REACT_CHANNELS[channel_id_str]
        
        for emoji in emojis:
            try:
                await message.add_reaction(emoji)
            except Exception as e:
                print(f"[AUTO_REACT] Erreur ajout réaction {emoji}: {e}")

@bot.event
async def on_command_error(ctx, error):
    print(f"[ERREUR COMMANDE] {error}")
    
    # Vérifier si le salon est autorisé avant d'envoyer un message d'erreur
    if not is_channel_allowed(ctx.channel):
        return
    
    # Gérer les erreurs spécifiques
    if isinstance(error, commands.CommandNotFound):
        # Ne rien afficher pour les commandes non trouvées dans les salons ignorés
        return
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Argument manquant: `{error.param}`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"❌ Argument invalide: {error}")
    else:
        # Pour les autres erreurs, afficher un message générique
        await ctx.send(f"❌ Une erreur est survenue: {str(error)[:100]}")

# ============================
# CLEANUP MEMOIRE
# ============================

@tasks.loop(minutes=10)
async def cleanup_aggressive():
    try:
        # Essayer d'importer depuis le cog games
        try:
            from cogs.games import cleanup_games
            cleanup_games()
        except ImportError:
            # Si le cog n'est pas chargé, ignorer
            pass
        
        gc.collect()
        print("[GC] Mémoire nettoyée")
    except Exception as e:
        print(f"[GC] Erreur: {e}")

# ============================
# CHARGEMENT DES COGS (OPTIMISÉ)
# ============================

# Initialiser le gestionnaire de cogs
cog_manager = None

async def load_cogs_async():
    global cog_manager
    
    # Initialiser le gestionnaire de cogs
    cog_manager = setup_cog_manager(bot)
    
    # Charger uniquement les cogs essentiels au démarrage
    await cog_manager.load_essential_cogs()
    
    # Lancer le chargement des cogs optionnels en arrière-plan
    asyncio.create_task(load_optional_cogs_delayed())

async def load_optional_cogs_delayed():
    """Charger les cogs optionnels après 30 secondes"""
    await asyncio.sleep(30)  # Attendre que le bot soit stable
    await cog_manager.load_optional_cogs()

def load_cogs():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(load_cogs_async())
    loop.close()

# ============================
# FLASK SERVER (RENDER)
# ============================

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Discord en ligne."

def run_flask():
    app.run(host="0.0.0.0", port=10000)

# ============================
# KEEP-ALIVE (ANTI-SLEEP)
# ============================

def keep_alive():
    while True:
        try:
            requests.get("https://bot-discord-stark.onrender.com")
        except:
            pass
        time.sleep(300)

# ============================
# LANCEMENT
# ============================

if __name__ == "__main__":
    print("[START] Démarrage du bot Stark...")

    # Lancer Flask
    threading.Thread(target=run_flask).start()

    # Lancer keep-alive
    threading.Thread(target=keep_alive).start()

    # Charger les cogs
    load_cogs()
    
    # Vérifier les commandes chargées
    print(f"[START] {len(bot.commands)} commandes chargées")
    for cmd in bot.commands:
        print(f"[CMD] {cmd.name}")

    # Lancer le bot Discord
    bot.run(TOKEN)
