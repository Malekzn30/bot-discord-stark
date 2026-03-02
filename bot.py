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

# Charger les variables d'environnement
load_dotenv()
TOKEN = os.getenv("TOKEN")

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
async def on_command_error(ctx, error):
    print(f"[ERREUR COMMANDE] {error}")
    await ctx.send(f"❌ Erreur : {error}")

# ============================
# CLEANUP MEMOIRE
# ============================

@tasks.loop(minutes=10)
async def cleanup_aggressive():
    try:
        from cogs.games import cleanup_games
        cleanup_games()
        gc.collect()
        print("[GC] Mémoire nettoyée")
    except Exception as e:
        print(f"[GC] Erreur: {e}")

# ============================
# CHARGEMENT DES COGS
# ============================

COGS = ["moderation", "system", "voice", "logs", "games", "tickets"]

async def load_cogs_async():
    for cog in COGS:
        try:
            bot.load_extension(f"cogs.{cog}")
            print(f"[+] Cog chargé : {cog}")
            await asyncio.sleep(0.1)
        except Exception as e:
            print(f"[!] Erreur chargement {cog}: {e}")

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

    # Lancer le bot Discord
    bot.run(TOKEN)