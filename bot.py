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
async def help(ctx, category: str = None, page: int = 1):
    """Affiche l'aide du bot avec interface interactive"""
    if category:
        # Aide par catégorie avec pagination
        category_commands = []
        for cmd in bot.commands:
            if cmd.cog and cmd.cog.__class__.__name__.lower() == category.lower():
                category_commands.append(cmd)
        
        if not category_commands:
            return await ctx.send(f"❌ Catégorie `{category}` non trouvée")
        
        await send_category_help(ctx, category, category_commands, page)
    else:
        # Menu principal interactif
        await send_main_help(ctx)

async def send_main_help(ctx):
    """Envoie le menu principal d'aide avec sélecteur"""
    from collections import Counter
    
    # Regrouper par catégories
    categories = {}
    for cmd in bot.commands:
        cog_name = cmd.cog.__class__.__name__ if cmd.cog else "Inconnu"
        if cog_name not in categories:
            categories[cog_name] = []
        categories[cog_name].append(cmd)
    
    # Créer le menu déroulant
    options = []
    for cog_name, cmds in sorted(categories.items(), key=lambda x: len(x[1]), reverse=True):
        if cog_name != "Inconnu":  # Exclure les commandes système
            options.append(nextcord.SelectOption(
                label=f"{cog_name} ({len(cmds)} commandes)",
                description=f"Voir les {len(cmds)} commandes de {cog_name}",
                value=cog_name.lower()
            ))
    
    select = nextcord.ui.Select(
        placeholder="🔍 Choisis une catégorie...",
        options=options[:25],  # Limite Discord
        custom_id="help_category_select"
    )
    
    async def select_callback(interaction: nextcord.Interaction):
        selected_category = interaction.data['values'][0]
        await interaction.response.defer()
        await send_category_help(interaction.user, selected_category, 
                               [cmd for cmd in bot.commands 
                                if cmd.cog and cmd.cog.__class__.__name__.lower() == selected_category], 1)
    
    select.callback = select_callback
    
    view = nextcord.ui.View(timeout=180)  # 3 minutes timeout
    view.add_item(select)
    
    embed = nextcord.Embed(
        title="🤖 StarK92 Bot - Aide Interactive",
        description=f"**{len(bot.commands)} commandes disponibles**\n\n👇 **Sélectionne une catégorie ci-dessous**",
        color=0x3498db
    )
    
    embed.add_field(
        name="📊 Statistiques",
        value=f"• **{len(categories)} catégories**\n• **{len(bot.commands)} commandes totales**\n• **Système optimisé**",
        inline=False
    )
    
    embed.add_field(
        name="🎯 Commandes Populaires",
        value="`+devinelenombre` • `+helpmenu` • `+voice`\n`+cogstatus` • `+ping` • `+dice`",
        inline=False
    )
    
    embed.set_footer(text="Sélectionne une catégorie dans le menu déroulant")
    
    await ctx.send(embed=embed, view=view)

async def send_category_help(ctx, category_name, commands_list, page=1):
    """Envoie l'aide d'une catégorie avec boutons de navigation"""
    # Trier les commandes
    sorted_commands = sorted(commands_list, key=lambda x: x.name)
    
    # Calculer la pagination
    commands_per_page = 25
    total_pages = (len(sorted_commands) + commands_per_page - 1) // commands_per_page
    
    if page < 1 or page > total_pages:
        page = 1
    
    # Obtenir les commandes pour cette page
    start_idx = (page - 1) * commands_per_page
    end_idx = start_idx + commands_per_page
    page_commands = sorted_commands[start_idx:end_idx]
    
    embed = nextcord.Embed(
        title=f"📖 Aide: {category_name.title()}",
        description=f"**{len(commands_list)} commandes** - Page {page}/{total_pages}",
        color=0x3498db
    )
    
    for cmd in page_commands:
        help_text = cmd.help or "Aucune description"
        embed.add_field(name=f"+{cmd.name}", value=help_text[:100], inline=False)
    
    embed.set_footer(text=f"Page {page}/{total_pages} • Utilise les boutons pour naviguer")
    
    # Créer les boutons de navigation
    view = nextcord.ui.View(timeout=180)
    
    # Bouton Retour
    back_button = nextcord.ui.Button(
        label="🔙 Retour",
        style=nextcord.ButtonStyle.secondary,
        custom_id="help_back"
    )
    
    async def back_callback(interaction: nextcord.Interaction):
        await interaction.response.defer()
        await send_main_help(interaction.user)
    
    back_button.callback = back_callback
    view.add_item(back_button)
    
    # Boutons de navigation de page
    if page > 1:
        prev_button = nextcord.ui.Button(
            label="⬅️ Précédent",
            style=nextcord.ButtonStyle.primary,
            custom_id="help_prev"
        )
        
        async def prev_callback(interaction: nextcord.Interaction):
            await interaction.response.defer()
            await send_category_help(interaction.user, category_name, commands_list, page - 1)
        
        prev_button.callback = prev_callback
        view.add_item(prev_button)
    
    # Bouton page actuelle
    page_button = nextcord.ui.Button(
        label=f"� {page}/{total_pages}",
        style=nextcord.ButtonStyle.secondary,
        disabled=True
    )
    view.add_item(page_button)
    
    if page < total_pages:
        next_button = nextcord.ui.Button(
            label="➡️ Suivant",
            style=nextcord.ButtonStyle.primary,
            custom_id="help_next"
        )
        
        async def next_callback(interaction: nextcord.Interaction):
            await interaction.response.defer()
            await send_category_help(interaction.user, category_name, commands_list, page + 1)
        
        next_button.callback = next_callback
        view.add_item(next_button)
    
    # Envoyer le message
    if hasattr(ctx, 'send'):  # Si c'est un Context normal
        await ctx.send(embed=embed, view=view)
    else:  # Si c'est une Interaction
        await ctx.send(embed=embed, view=view)

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