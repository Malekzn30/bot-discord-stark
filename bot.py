import nextcord
from nextcord.ext import commands, tasks
import threading
from flask import Flask
import os
import time
import requests
from config import TOKEN

# ============================
# DISCORD BOT - ULTRA OPTIMISÉ
# ============================

# Intents MINIMAUX pour économiser la RAM
intents = nextcord.Intents.default()
intents.message_content = True
intents.members = True   # ← NÉCESSAIRE pour les tickets
intents.guilds = True   # ← NÉCESSAIRE pour les tickets
intents.presences = False  # ← Pas de presences
intents.typing = False  # ← Pas de typing

bot = commands.Bot(
    command_prefix="+",
    intents=intents,
    help_command=None,
    chunk_guilds_at_startup=False  # ← Pas de chunking au startup
)
bot.start_time = time.time()

@bot.event
async def on_ready():
    print(f"Bot prêt : {bot.user}")
    cleanup_aggressive.start()

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

def load_cogs():
    cogs_to_load = ['moderation', 'system', 'voice', 'logs', 'games', 'tickets']
    print(f"[DEBUG] Tentative de chargement des cogs: {cogs_to_load}")
    
    for cog in cogs_to_load:
        try:
            bot.load_extension(f"cogs.{cog}")
            print(f"[+] Cog chargé : {cog}")
        except Exception as e:
            print(f"[!] Erreur chargement {cog}: {e}")
            import traceback
            traceback.print_exc()

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
    # Lancer Flask dans un thread secondaire
    threading.Thread(target=run_flask).start()

    # Lancer le keep-alive dans un autre thread
    threading.Thread(target=keep_alive).start()

    # Lancer le bot Discord dans le thread principal
    load_cogs()
    bot.run(TOKEN)