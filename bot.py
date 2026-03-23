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
import random

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

# Fonction de retry avec backoff exponentiel
async def retry_with_backoff(func, max_retries=5, base_delay=1):
    """Réessaye une fonction avec backoff exponentiel en cas de rate limit"""
    for attempt in range(max_retries):
        try:
            return await func()
        except nextcord.HTTPException as e:
            if e.status == 429:  # Rate limit
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                print(f"[RATE LIMIT] Attente de {delay:.2f}s (tentative {attempt + 1}/{max_retries})")
                await asyncio.sleep(delay)
            else:
                raise
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(base_delay)
    
    raise Exception("Max retries exceeded")

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

@bot.command()
@commands.is_owner()
async def ignoredchannels(ctx):
    """Gérer les salons ignorés par le bot"""
    embed = nextcord.Embed(
        title="🔇 Salons Ignorés",
        description="Configuration des salons où le bot ne répondra pas",
        color=0x3498db
    )
    
    # Afficher les salons ignorés
    if config.IGNORED_CHANNELS:
        ignored_text = []
        for ignored in config.IGNORED_CHANNELS:
            if isinstance(ignored, int):
                ignored_text.append(f"ID: `{ignored}`")
            else:
                ignored_text.append(f"Nom: `{ignored}`")
        embed.add_field(name="🚫 Salons Ignorés", value="\n".join(ignored_text), inline=False)
    else:
        embed.add_field(name="🚫 Salons Ignorés", value="Aucun salon ignoré", inline=False)
    
    # Afficher les salons autorisés (si configuré)
    if config.ALLOWED_CHANNELS:
        allowed_text = []
        for allowed in config.ALLOWED_CHANNELS:
            if isinstance(allowed, int):
                allowed_text.append(f"ID: `{allowed}`")
            else:
                allowed_text.append(f"Nom: `{allowed}`")
        embed.add_field(name="✅ Salons Autorisés Uniquement", value="\n".join(allowed_text), inline=False)
    else:
        embed.add_field(name="✅ Mode", value="Tous les salons autorisés sauf ignorés", inline=False)
    
    embed.add_field(
        name="📝 Comment Modifier",
        value="Édite `config.py` et modifie les listes:\n- `IGNORED_CHANNELS` - Salons à ignorer\n- `ALLOWED_CHANNELS` - Salons autorisés uniquement",
        inline=False
    )

@bot.command()
@commands.is_owner()
async def reloadconfig(ctx):
    """Recharge la configuration du bot"""
    try:
        import importlib
        importlib.reload(config)
        
        await ctx.send("✅ Configuration rechargée avec succès!")
        
        # Afficher les nouvelles configurations
        embed = nextcord.Embed(
            title="⚙️ Configuration Rechargée",
            color=0x2ecc71
        )
        
        embed.add_field(name="🚫 Salons Ignorés", value=f"{len(config.IGNORED_CHANNELS)} salons", inline=True)
        embed.add_field(name="✅ Salons Autorisés", value=f"{len(config.ALLOWED_CHANNELS)} salons", inline=True)
        embed.add_field(name="🔄 Auto-Réactions", value=f"{len(config.AUTO_REACT_CHANNELS)} salons", inline=True)
        embed.add_field(name="🎯 Mode", value="Restreint" if config.ALLOWED_CHANNELS else "Ouvert", inline=True)
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Erreur lors du rechargement: {e}")

@bot.command()
@commands.is_owner()
async def testchannel(ctx):
    """Teste si le bot peut répondre dans le salon actuel"""
    if is_channel_allowed(ctx.channel):
        await ctx.send("✅ Ce salon est **autorisé** - Le bot peut répondre ici")
    else:
        await ctx.send("❌ Ce salon est **ignoré** - Le bot ne répondra pas ici")
        
        # Donner des informations sur pourquoi
        channel_id = ctx.channel.id
        channel_name = ctx.channel.name.lower()
        
        reasons = []
        for ignored in config.IGNORED_CHANNELS:
            if isinstance(ignored, int) and ignored == channel_id:
                reasons.append(f"ID `{ignored}` est dans la liste ignorée")
            elif isinstance(ignored, str) and ignored.lower() == channel_name:
                reasons.append(f"Nom `{ignored}` est dans la liste ignorée")
        
        if config.ALLOWED_CHANNELS:
            is_allowed = False
            for allowed in config.ALLOWED_CHANNELS:
                if isinstance(allowed, int) and allowed == channel_id:
                    is_allowed = True
                    break
                elif isinstance(allowed, str) and allowed.lower() == channel_name:
                    is_allowed = True
                    break
            if not is_allowed:
                reasons.append("Le salon n'est pas dans la liste autorisée")
        
        if reasons:
            await ctx.send(f"📝 **Raison(s):**\n" + "\n".join(reasons))

# ============================
# FLASK SERVER (RENDER) - PRODUCTION READY
# ============================

from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Discord en ligne."

def run_flask():
    # Configuration explicite pour Render - évite le scan de ports
    app.run(host="0.0.0.0", port=10000, debug=False, use_reloader=False)

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
    # Vérifier si le salon est autorisé
    if not is_channel_allowed(ctx.channel):
        return
    
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
    
    # Créer le menu déroulant avec plus de catégories
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
        await send_category_help(interaction, selected_category, 
                               [cmd for cmd in bot.commands 
                                if cmd.cog and cmd.cog.__class__.__name__.lower() == selected_category], 1)
    
    select.callback = select_callback
    
    view = nextcord.ui.View(timeout=180)
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
    
    embed.add_field(
        name="⚙️ Gestion",
        value="`+setactivity` • `+setstatus` • `+autoreact`\n`+ignoredchannels` • `+testchannel`",
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
        await send_main_help(interaction)
    
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
            await send_category_help(interaction, category_name, commands_list, page - 1)
        
        prev_button.callback = prev_callback
        view.add_item(prev_button)
    
    # Bouton page actuelle
    page_button = nextcord.ui.Button(
        label=f"📄 {page}/{total_pages}",
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
            await send_category_help(interaction, category_name, commands_list, page + 1)
        
        next_button.callback = next_callback
        view.add_item(next_button)
    
    # Envoyer ou modifier le message
    if hasattr(ctx, 'edit'):  # Si c'est une interaction (modification)
        await ctx.edit(embed=embed, view=view)
    else:  # Si c'est un Context normal (nouveau message)
        await ctx.send(embed=embed, view=view)

# ... (code après la section modifiée)

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

    # Lancer le bot Discord avec retry logic
    async def start_bot_with_retry():
        async def connect():
            return await bot.start(TOKEN)
        
        try:
            await retry_with_backoff(connect, max_retries=3, base_delay=5)
        except Exception as e:
            print(f"[FATAL] Impossible de démarrer le bot: {e}")
            # Continue anyway to keep Flask server running
    
    # Démarrer le bot
    asyncio.run(start_bot_with_retry())