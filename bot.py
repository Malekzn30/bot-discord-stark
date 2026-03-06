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

# Charger les variables d'environnement
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

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

# Commandes de gestion des cogs
@bot.command()
@commands.is_owner()
async def cogstatus(ctx):
    """Voir le statut des cogs"""
    if not cog_manager:
        return await ctx.send("❌ Gestionnaire de cogs non initialisé")
    
    status = cog_manager.get_cog_status()
    
    embed = nextcord.Embed(
        title="⚙️ Statut des Cogs",
        description=f"**Cogs chargés:** {status['total_loaded']}/{status['total_available']}",
        color=0x3498db
    )
    
    embed.add_field(name="🟢 Chargés", value=", ".join(status['loaded'])[:500], inline=False)
    embed.add_field(name="🔴 Désactivés", value=", ".join(status['disabled']) or "Aucun", inline=False)
    
    await ctx.send(embed=embed)

@bot.command()
@commands.is_owner()
async def loadcog(ctx, cog_name: str):
    """Charger un cog spécifique"""
    if not cog_manager:
        return await ctx.send("❌ Gestionnaire de cogs non initialisé")
    
    success = await cog_manager.load_cog_on_demand(cog_name)
    
    if success:
        await ctx.send(f"✅ Cog `{cog_name}` chargé avec succès")
    else:
        await ctx.send(f"❌ Impossible de charger le cog `{cog_name}`")

@bot.command()
@commands.is_owner()
async def unloadcog(ctx, cog_name: str):
    """Décharger un cog spécifique"""
    if not cog_manager:
        return await ctx.send("❌ Gestionnaire de cogs non initialisé")
    
    success = await cog_manager.unload_cog(cog_name)
    
    if success:
        await ctx.send(f"✅ Cog `{cog_name}` déchargé avec succès")
    else:
        await ctx.send(f"❌ Impossible de décharger le cog `{cog_name}`")

@bot.command()
@commands.is_owner()
async def reloadcog(ctx, cog_name: str):
    """Recharger un cog spécifique"""
    if not cog_manager:
        return await ctx.send("❌ Gestionnaire de cogs non initialisé")
    
    success = await cog_manager.reload_cog(cog_name)
    
    if success:
        await ctx.send(f"✅ Cog `{cog_name}` rechargé avec succès")
    else:
        await ctx.send(f"❌ Impossible de recharger le cog `{cog_name}`")

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

# Commande help par défaut
@bot.command()
async def help(ctx, command_name=None):
    """Affiche l'aide du bot"""
    if command_name:
        cmd = bot.get_command(command_name)
        if cmd:
            embed = nextcord.Embed(
                title=f"📖 Aide: {cmd.name}",
                description=cmd.help or "Aucune description disponible",
                color=0x3498db
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Commande introuvable")
    else:
        embed = nextcord.Embed(
            title="🤖 StarK92 Bot - Aide",
            description="Voici les commandes disponibles:",
            color=0x3498db
        )
        
        # Compter les commandes par catégorie
        voice_commands = [cmd for cmd in bot.commands if hasattr(cmd.cog, '__class__') and cmd.cog.__class__.__name__ == 'Voice']
        other_commands = [cmd for cmd in bot.commands if cmd not in voice_commands]
        
        embed.add_field(name="🎤 Vocal", value=f"{len(voice_commands)} commandes", inline=True)
        embed.add_field(name="🔧 Autres", value=f"{len(other_commands)} commandes", inline=True)
        embed.add_field(name="📊 Total", value=f"{len(bot.commands)} commandes", inline=True)
        embed.set_footer(text="Utilise +help <commande> pour plus d'infos")
        
        await ctx.send(embed=embed)

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