"""
Bot Discord Ultra-Optimisé pour Render Gratuit
Un seul fichier avec toutes les fonctionnalités intégrées
"""

import nextcord
from nextcord.ext import commands, tasks
import threading
from flask import Flask
import os
import time
import requests
import asyncio
import json
import re
import datetime
import gc
from dotenv import load_dotenv
import sys
from functools import wraps

# Configuration pour Render
os.environ["PYTHONUNBUFFERED"] = "1"
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

# Configuration
TOKEN = os.getenv("DISCORD_TOKEN")
AUTHORIZED_ROLE_ID = 1469665367881420841
LIVE_ROLE_ID = 1469682659817951302

# Intents optimisés
intents = nextcord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.presences = False
intents.typing = False

# Bot ultra-optimisé
bot = commands.Bot(
    command_prefix="+",
    intents=intents,
    help_command=None,
    chunk_guilds_at_startup=False,
    max_messages=50  # Réduit pour économiser la mémoire
)

# Variables globales optimisées
authorized_roles = [str(AUTHORIZED_ROLE_ID)]
whitelist_domains = [
    "discord.com", "discord.gg", "twitch.tv", "youtube.com", "youtu.be",
    "twitter.com", "x.com", "tiktok.com", "instagram.com", "facebook.com",
    "reddit.com", "github.com", "openai.com", "spotify.com"
]
link_pattern = re.compile(r'(https?://)?(www\.)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(\/[^\s]*)?', re.IGNORECASE)

# Cache optimisé
cache = {
    'users': {},
    'messages': {},
    'last_cleanup': time.time()
}

# Flask pour Render
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Discord en ligne - Optimisé pour Render"

def keep_alive():
    while True:
        try:
            requests.get("https://bot-discord-stark.onrender.com")
        except:
            pass
        time.sleep(300)

# Système de permissions optimisé
def is_authorized(member):
    if not member.guild:
        return False
    
    # Cache lookup
    cache_key = f"auth_{member.guild.id}_{member.id}"
    if cache_key in cache['users']:
        return cache['users'][cache_key]
    
    # Vérification
    for role_id in authorized_roles:
        role = member.guild.get_role(int(role_id))
        if role and role in member.roles:
            cache['users'][cache_key] = True
            return True
    
    cache['users'][cache_key] = False
    return False

def has_role():
    def decorator(func):
        @wraps(func)
        async def wrapper(self, ctx, *args, **kwargs):
            if not is_authorized(ctx.author):
                embed = nextcord.Embed(
                    title="❌ Accès refusé",
                    description="Vous n'avez pas la permission d'utiliser cette commande.",
                    color=0xE74C3C
                )
                embed.add_field(name="💡 Solution", value="Contactez un administrateur pour obtenir les permissions nécessaires.", inline=False)
                try:
                    await ctx.send(embed=embed, delete_after=5)
                except:
                    pass
                return
            return await func(self, ctx, *args, **kwargs)
        return wrapper
    return decorator

# Nettoyage mémoire optimisé
@tasks.loop(minutes=5)
async def cleanup_memory():
    try:
        # Vider le cache vieux de 10 minutes
        current_time = time.time()
        cache['users'] = {k: v for k, v in cache['users'].items() if current_time - cache.get(f"time_{k}", 0) < 600}
        cache['messages'] = {k: v for k, v in cache['messages'].items() if current_time - cache.get(f"time_{k}", 0) < 600}
        
        # Forcer GC
        collected = gc.collect()
        print(f"[CLEANUP] Cache nettoyé, GC: {collected} objets")
        
    except Exception as e:
        print(f"[CLEANUP] Erreur: {e}")

# Cogs intégrés dans un seul fichier
class MainCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.muted_users = {}
    
    @commands.command(name="help")
    async def help(self, ctx, command: str = None):
        """Help optimisé"""
        if command is None:
            embed = nextcord.Embed(
                title="🤖 Commandes du Bot Stark",
                description="Bot ultra-optimisé pour Render gratuit",
                color=0x3498db
            )
            
            categories = {
                "🛡️ Modération": ["warn", "kick", "ban", "mute", "timeout", "clear", "lock", "unlock"],
                "🎤 Vocal": ["déplacer", "equilibrer", "equilibrer_auto", "stats_vocal"],
                "📬 Communication": ["dmall", "dmtest"],
                "📱 Social": ["live", "stoplive", "finduser", "find"],
                "🔒 Administration": ["whitelist", "roles", "checkperms", "logs_setup", "ping"]
            }
            
            for cat, cmds in categories.items():
                embed.add_field(name=cat, value="\n".join([f"• `+{cmd}`" for cmd in cmds]), inline=False)
            
            embed.set_footer(text="Utilise +help <commande> pour plus de détails")
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"Aide pour +{command}: Utilise +help pour voir la liste")

    @commands.command(name="ping")
    async def ping(self, ctx):
        """Ping optimisé"""
        start = time.time()
        msg = await ctx.send("🏓 Pong !")
        end = time.time()
        latency = (end - start) * 1000
        
        embed = nextcord.Embed(
            title="🏓 Pong !",
            description=f"Latence: **{latency:.2f}ms**\nAPI: **{bot.latency*1000:.2f}ms**",
            color=0x3498db
        )
        await msg.edit(embed=embed)

    @commands.command(name="live")
    @has_role()
    async def live(self, ctx, *, message: str = None):
        """Annoncer un live TikTok"""
        if not message:
            message = "🔴 **𝑳𝑨𝒁 est en LIVE sur TikTok !** 🔴\n\n🎥 Rejoignez le live maintenant !"
        
        embed = nextcord.Embed(
            title="🔴 LIVE TIKTOK 🔴",
            description=message,
            color=0xFF0000,
            timestamp=datetime.datetime.now()
        )
        
        embed.set_author(name="𝑳𝑨𝒁", icon_url=ctx.author.display_avatar.url)
        embed.add_field(name="🎥 Stream", value="📱 TikTok Live", inline=True)
        embed.add_field(name="⏰ Début", value=f"<t:{int(datetime.datetime.now().timestamp())}:t>", inline=True)
        embed.set_footer(text="🔴 LIVE EN COURS 🔴")
        
        # Ajouter le rôle live
        live_role = ctx.guild.get_role(LIVE_ROLE_ID)
        if live_role:
            await ctx.author.add_roles(live_role)
        
        await ctx.send(embed=embed)

    @commands.command(name="stoplive")
    @has_role()
    async def stoplive(self, ctx):
        """Arrêter le live"""
        live_role = ctx.guild.get_role(LIVE_ROLE_ID)
        if live_role and live_role in ctx.author.roles:
            await ctx.author.remove_roles(live_role)
            await ctx.send("✅ Live terminé !")

    @commands.command(name="dmall")
    @has_role()
    async def dmall(self, ctx, msg_type: str, *, content: str = None):
        """DM massif optimisé"""
        if msg_type not in ["texte", "embed"]:
            return await ctx.send("❌ Type invalide. Utilise: texte ou embed")
        
        if not content:
            return await ctx.send("❌ Contenu manquant")
        
        total = len(ctx.guild.members)
        await ctx.send(f"🚀 Envoi à {total} membres...")
        
        sent = 0
        failed = 0
        
        for member in ctx.guild.members:
            try:
                if msg_type == "texte":
                    await member.send(content)
                else:
                    embed = nextcord.Embed(
                        title=content.split('"')[1] if '"' in content else "Message",
                        description=content.split('"')[3] if '"' in content and len(content.split('"')) > 3 else content,
                        color=0x3498db
                    )
                    await member.send(embed=embed)
                sent += 1
                await asyncio.sleep(0.5)  # Rate limiting
            except:
                failed += 1
        
        await ctx.send(f"✅ Envoyé: {sent} | Échecs: {failed}")

    @commands.command(name="finduser")
    async def finduser(self, ctx, *, search: str):
        """Chercher des utilisateurs"""
        if len(search) < 2:
            return await ctx.send("❌ 2 caractères minimum")
        
        found = []
        search_lower = search.lower()
        
        for member in ctx.guild.members:
            if search_lower in member.display_name.lower() or search_lower in member.name.lower():
                found.append(member)
        
        if not found:
            return await ctx.send("❌ Aucun membre trouvé")
        
        embed = nextcord.Embed(
            title=f"🔍 Recherche: '{search}'",
            description=f"**{len(found)}** membre(s) trouvé(s)",
            color=0x3498db
        )
        
        # Limiter à 15 résultats
        for i, member in enumerate(found[:15]):
            status = {"online": "🟢", "idle": "🟡", "dnd": "🔴", "offline": "⚫"}.get(str(member.status), "⚪")
            voice = f" 🎤 {member.voice.channel.name}" if member.voice else ""
            embed.add_field(
                name=f"{i+1}. {status} {member.display_name}{voice}",
                value=f"ID: `{member.id}` | Rejoint: <t:{int(member.joined_at.timestamp())}:R>",
                inline=False
            )
        
        await ctx.send(embed=embed)

    @commands.command(name="whitelist")
    @has_role()
    async def whitelist(self, ctx, action: str = None, domain: str = None):
        """Gérer la whitelist"""
        global whitelist_domains
        
        if not action:
            embed = nextcord.Embed(
                title="🔒 Whitelist",
                description=f"**{len(whitelist_domains)}** domaine(s) autorisés",
                color=0x3498db
            )
            embed.add_field(name="Domaines", value="\n".join([f"• `{d}`" for d in whitelist_domains]), inline=False)
            embed.add_field(name="Commandes", value="• `+whitelist add <domaine>`\n• `+whitelist remove <domaine>`\n• `+whitelist list`", inline=False)
            return await ctx.send(embed=embed)
        
        action = action.lower()
        
        if action == "list":
            await self.whitelist(ctx, "list")
        elif action == "add" and domain:
            if domain.lower() not in whitelist_domains:
                whitelist_domains.append(domain.lower())
                await ctx.send(f"✅ `{domain}` ajouté à la whitelist")
            else:
                await ctx.send(f"⚠️ `{domain}` déjà dans la whitelist")
        elif action == "remove" and domain:
            if domain.lower() in whitelist_domains:
                whitelist_domains.remove(domain.lower())
                await ctx.send(f"✅ `{domain}` retiré de la whitelist")
            else:
                await ctx.send(f"❌ `{domain}` pas dans la whitelist")
        else:
            await ctx.send("❌ Utilisation: +whitelist <add|remove|list> [domaine]")

    @commands.command(name="roles")
    @has_role()
    async def roles(self, ctx, action: str = None, *, role: nextcord.Role = None):
        """Gérer les rôles autorisés"""
        global authorized_roles
        
        if not action:
            embed = nextcord.Embed(
                title="🔐 Rôles Autorisés",
                description=f"**{len(authorized_roles)}** rôle(s)",
                color=0x3498db
            )
            
            for role_id in authorized_roles:
                r = ctx.guild.get_role(int(role_id))
                if r:
                    count = len([m for m in ctx.guild.members if r in m.roles])
                    embed.add_field(name=r.name, value=f"ID: `{r.id}` | **{count}** membres", inline=False)
            
            await ctx.send(embed=embed)
            return
        
        action = action.lower()
        
        if action == "add" and role:
            if str(role.id) not in authorized_roles:
                authorized_roles.append(str(role.id))
                await ctx.send(f"✅ {role.mention} ajouté")
            else:
                await ctx.send(f"⚠️ {role.mention} déjà autorisé")
        elif action == "remove" and role:
            if str(role.id) == str(AUTHORIZED_ROLE_ID):
                return await ctx.send("❌ Impossible de retirer le rôle principal")
            if str(role.id) in authorized_roles:
                authorized_roles.remove(str(role.id))
                await ctx.send(f"✅ {role.mention} retiré")
            else:
                await ctx.send(f"❌ {role.mention} pas autorisé")
        else:
            await ctx.send("❌ Utilisation: +roles <add|remove> <@rôle>")

    @commands.command(name="checkperms")
    async def checkperms(self, ctx, member: nextcord.Member = None):
        """Vérifier les permissions"""
        if member is None:
            member = ctx.author
        
        has_auth = is_authorized(member)
        
        embed = nextcord.Embed(
            title="✅ Accès autorisé" if has_auth else "❌ Accès refusé",
            description=f"{member.mention} {'**peut**' if has_auth else '**ne peut pas**'} utiliser les commandes",
            color=0x2ECC71 if has_auth else 0xE74C3C
        )
        
        if has_auth:
            user_roles = [r for r in member.roles if str(r.id) in authorized_roles]
            if user_roles:
                embed.add_field(name="🔐 Rôles", value="\n".join([r.mention for r in user_roles]), inline=False)
        
        await ctx.send(embed=embed)

    @commands.command(name="clear")
    @has_role()
    async def clear(self, ctx, amount: int):
        """Supprimer des messages"""
        if amount < 1 or amount > 100:
            return await ctx.send("❌ Entre 1 et 100 messages")
        
        deleted = await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"✅ {deleted - 1} messages supprimés", delete_after=3)

    @commands.command(name="lock")
    @has_role()
    async def lock(self, ctx):
        """Verrouiller le salon"""
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send("🔒 Salon verrouillé")

    @commands.command(name="unlock")
    @has_role()
    async def unlock(self, ctx):
        """Déverrouiller le salon"""
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await ctx.send("🔓 Salon déverrouillé")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Anti-liens optimisé"""
        if message.author.bot or not message.guild:
            return
        
        if is_authorized(message.author):
            return  # Les autorisés peuvent envoyer des liens
        
        # Détecter les liens
        links = link_pattern.findall(message.content)
        if not links:
            return
        
        # Vérifier si whitelist
        for link in links:
            domain = link[2].lower().rstrip('.')
            if not any(allowed in domain for allowed in whitelist_domains):
                try:
                    await message.delete()
                    
                    # Mute 5 secondes
                    muted_role = nextcord.utils.get(message.guild.roles, name="Muted")
                    if not muted_role:
                        muted_role = await message.guild.create_role(name="Muted", color=nextcord.Color.dark_grey())
                        for ch in message.guild.channels:
                            await ch.set_permissions(muted_role, send_messages=False, speak=False)
                    
                    await message.author.add_roles(muted_role)
                    
                    # Unmute automatique
                    self.bot.loop.create_task(self.unmute_after(message.author, muted_role, 5))
                    
                    # Message d'avertissement
                    embed = nextcord.Embed(
                        title="🔒 Lien non autorisé",
                        description=f"{message.author.mention} a envoyé un lien non autorisé",
                        color=0xE74C3C
                    )
                    embed.add_field(name="🚫 Lien supprimé", value=f"Domaine: `{domain}`", inline=False)
                    embed.add_field(name="⏰ Sanction", value="Mute de 5 secondes", inline=False)
                    
                    msg = await message.channel.send(embed=embed)
                    await asyncio.sleep(10)
                    await msg.delete()
                    
                except:
                    pass
                break

    async def unmute_after(self, member, role, seconds):
        await asyncio.sleep(seconds)
        try:
            await member.remove_roles(role)
        except:
            pass

    @commands.command(name="déplacer")
    @has_role()
    async def move_member(self, ctx, member: nextcord.Member, *, channel: nextcord.VoiceChannel = None):
        """Déplacer un membre"""
        if not channel:
            return await ctx.send("❌ Mentionne un salon vocal")
        
        if not member.voice:
            return await ctx.send("❌ Le membre n'est pas en vocal")
        
        try:
            await member.move_to(channel)
            await ctx.send(f"✅ {member.mention} déplacé vers {channel.mention}")
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")

# Événements optimisés
@bot.event
async def on_ready():
    print(f"✅ Bot prêt: {bot.user}")
    print(f"📊 Serveurs: {len(bot.guilds)}")
    print(f"👥 Membres: {sum(g.member_count for g in bot.guilds)}")
    cleanup_memory.start()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Permissions manquantes")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Argument manquant: {error}")
    else:
        await ctx.send(f"❌ Erreur: {error}")

# Lancement optimisé
if __name__ == "__main__":
    print("🚀 Démarrage bot ultra-optimisé...")
    
    # Flask thread
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=10000), daemon=True).start()
    
    # Keep-alive thread
    threading.Thread(target=keep_alive, daemon=True).start()
    
    # Ajouter le cog principal
    bot.add_cog(MainCog(bot))
    
    # Démarrer le bot
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)
