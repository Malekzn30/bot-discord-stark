import nextcord
from nextcord.ext import commands, tasks
import threading
from flask import Flask
import os
import time
import requests
import asyncio
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(__file__))
from cogs.logs import setup_logging
from config import TOKEN

# ============================
# DISCORD BOT - ULTRA OPTIMISÉ
# ============================

# Configuration pour Render gratuit
os.environ["PYTHONUNBUFFERED"] = "1"  # Logs immédiats
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"  # Pas de .pyc

# Importations des optimisations
try:
    from utils.optimization import RenderOptimizer, RENDER_CONFIG, check_render_health
    OPTIMIZATION_ENABLED = True
except ImportError:
    OPTIMIZATION_ENABLED = False
    print("[WARNING] Module d'optimisation non trouvé")

# Intents optimisés pour le bot
intents = nextcord.Intents.default()
intents.message_content = True
intents.members = True   # Pour les commandes vocales
intents.guilds = True   # Pour les commandes serveur
intents.presences = False  # Pas de presences
intents.typing = False  # Pas de typing

bot = commands.Bot(
    command_prefix="+",
    intents=intents,
    help_command=None,
    chunk_guilds_at_startup=False  # ← Économiser la performance sur Render
)
bot.start_time = time.time()

@bot.event
async def on_ready():
    print(f"Bot prêt : {bot.user}")
    cleanup_aggressive.start()
    
    # Initialiser l'optimiseur si disponible
    if OPTIMIZATION_ENABLED:
        bot.optimizer = RenderOptimizer(bot)
        print("[OPTIMIZATION] Optimiseur Render activé")
    
    print("[START] Bot prêt et optimisé pour Render gratuit")

@bot.event
async def on_command_error(ctx, error):
    """Capturer les erreurs de commandes"""
    print(f"[ERREUR COMMANDE] {ctx.command} - {error}")
    
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Permissions manquantes ! Tu dois être administrateur pour utiliser cette commande.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Argument manquant : {error}")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"❌ Argument invalide : {error}")
    else:
        await ctx.send(f"❌ Erreur : {error}")

@tasks.loop(minutes=10)
async def cleanup_aggressive():
    """Nettoyage agressif de la mémoire toutes les 10 min."""
    try:
        from cogs.games import cleanup_games
        cleanup_games()

        # Forcer garbage collection
        import gc
        gc.collect()
        print("[GC] Mémoire nettoyée")
    except Exception as e:
        print(f"[GC] Erreur: {e}")

async def load_cogs_optimized():
    """Charger les cogs avec gestion d'erreur et optimisation"""
    cogs_to_load = ['moderation', 'system', 'voice', 'logs', 'games', 'welcome', 'dm', 'social', 'antimod', 'rolemanager']
    
    for cog in cogs_to_load:
        try:
            # Nettoyage mémoire avant chaque chargement
            if OPTIMIZATION_ENABLED:
                gc.collect()
            
            bot.load_extension(f"cogs.{cog}")
            print(f"[+] Cog chargé : {cog}")
            
            # Petite pause pour éviter le surchargement
            await asyncio.sleep(0.1)
            
        except Exception as e:
            print(f"[!] Erreur chargement {cog}: {e}")
            # Continuer malgré les erreurs pour ne pas bloquer le démarrage

def load_cogs():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(load_cogs_optimized())
    loop.close()

# ============================
# FAKE FLASK SERVER (pour Render)
# ============================

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Discord en ligne."

def run_flask():
    app.run(host="0.0.0.0", port=10000)

# ============================
# KEEP-ALIVE (ANTI-SLEEP RENDER)
# ============================

def keep_alive():
    while True:
        try:
            requests.get("https://bot-discord-stark.onrender.com")
        except:
            pass
        time.sleep(300)  # 5 minutes

# ============================
# LANCEMENT
# ============================

if __name__ == "__main__":
    # Initialiser le système de logs
    logger = setup_logging()
    logger.info("Démarrage du Bot Stark")
    
    # Lancer Flask dans un thread secondaire
    threading.Thread(target=run_flask).start()
    
    # Lancer le keep-alive dans un autre thread
    threading.Thread(target=keep_alive).start()
    
    # Lancer le bot Discord dans le thread principal
    load_cogs()
    bot.run(TOKEN)