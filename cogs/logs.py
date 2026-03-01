import nextcord
from nextcord.ext import commands
from datetime import datetime, timedelta
import os
import json
import asyncio

# ============================================================
# CONFIGURATION JSON PERSISTANTE
# ============================================================

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "logs_config.json")

LOG_CATEGORIES = [
    "warn",
    "commands",
    "moderation",
    "voice",
    "messages",
    "security",
    "admin",
    "server",
    "roles",
    "nicknames",
    "automod",
    "system"
]

DEFAULT_LOG_CHANNELS = {cat: None for cat in LOG_CATEGORIES}

def load_config():
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w") as f:
            json.dump(DEFAULT_LOG_CHANNELS, f, indent=4)
        return DEFAULT_LOG_CHANNELS

    try:
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"❌ Erreur load_config: {e}")
        return DEFAULT_LOG_CHANNELS

def save_config(config):
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"❌ Erreur save_config: {e}")

LOG_CHANNELS = load_config()

# ============================================================
# FONCTION DE LOG ULTRA DÉTAILLÉE (NIVEAU PREMIUM)
# ============================================================

CATEGORY_ICONS = {
    "warn": "⚠️",
    "commands": "📘",
    "moderation": "🛡️",
    "voice": "🎙️",
    "messages": "💬",
    "security": "🔒",
    "admin": "⚙️",
    "server": "🌐",
    "roles": "🏷️",
    "nicknames": "📝",
    "automod": "🤖",
    "system": "📊"
}

CATEGORY_COLORS = {
    "warn": 0xFFAA00,
    "commands": 0x3498db,
    "moderation": 0xE74C3C,
    "voice": 0x9B59B6,
    "messages": 0x2ECC71,
    "security": 0xC0392B,
    "admin": 0x95A5A6,
    "server": 0x1ABC9C,
    "roles": 0xF1C40F,
    "nicknames": 0xE67E22,
    "automod": 0x8E44AD,
    "system": 0x34495E
}

async def send_log(bot, category: str, title: str, fields: dict, ctx=None, audit_id=None):
    """
    Envoie un log ultra détaillé dans la catégorie choisie.
    fields = { "Auteur": "...", "Cible": "...", "Salon": "...", etc. }
    """

    channel_id = LOG_CHANNELS.get(category)
    if not channel_id:
        print(f"⚠️ Aucun canal configuré pour la catégorie '{category}'")
        return

    channel = bot.get_channel(channel_id)
    if not channel:
        print(f"❌ Canal {channel_id} introuvable pour '{category}'")
        return

    icon = CATEGORY_ICONS.get(category, "📄")
    color = CATEGORY_COLORS.get(category, 0x3498db)

    embed = nextcord.Embed(
        title=f"{icon} {title}",
        color=color,
        timestamp=datetime.utcnow()
    )

    # Ajout des champs détaillés
    for name, value in fields.items():
        embed.add_field(name=name, value=str(value), inline=False)

    # Ajout de l'Audit Log ID si disponible
    if audit_id:
        embed.add_field(name="🔍 Audit ID", value=str(audit_id), inline=False)

    embed.set_footer(text=f"Catégorie : {category}")

    try:
        await channel.send(embed=embed)
    except Exception as e:
        print(f"❌ Erreur envoi log: {e}")

# ============================================================
# AUDIT LOG HELPER (RÉCUPÈRE L'AUTEUR RÉEL DE L'ACTION)
# ============================================================

async def get_audit_entry(guild, action_type, target_id):
    """
    Récupère l'entrée d'audit log correspondant à une action.
    action_type = nextcord.AuditLogAction.<ACTION>
    target_id = ID de la cible
    """

    await asyncio.sleep(0.5)

    try:
        async for entry in guild.audit_logs(limit=5, action=action_type):
            if entry.target and entry.target.id == target_id:
                return entry
    except Exception as e:
        print(f"❌ Erreur get_audit_entry: {e}")

    return None

# ============================================================
# LOGS MODÉRATION — TIMEOUT / KICK / BAN / ROLES / NICKNAMES
# ============================================================

class LogsModeration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # TIMEOUT / UNTIMEOUT (détecté automatiquement)
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.timed_out == after.timed_out:
            return

        if after.timed_out:
            # TIMEOUT APPLIQUÉ
            entry = await get_audit_entry(after.guild, nextcord.AuditLogAction.member_update, after.id)
            await send_log(
                self.bot,
                "moderation",
                "TIMEOUT APPLIQUÉ",
                {
                    "Membre": f"{after} (ID: {after.id})",
                    "Durée": str(after.timed_out_until - datetime.utcnow()) if after.timed_out_until else "Indéfini",
                    "Modérateur": entry.user if entry else "Inconnu"
                },
                audit_id=entry.id if entry else None
            )
        else:
            # TIMEOUT RETIRÉ
            entry = await get_audit_entry(after.guild, nextcord.AuditLogAction.member_update, after.id)
            await send_log(
                self.bot,
                "moderation",
                "TIMEOUT RETIRÉ",
                {
                    "Membre": f"{after} (ID: {after.id})",
                    "Modérateur": entry.user if entry else "Inconnu"
                },
                audit_id=entry.id if entry else None
            )

    # KICK
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await asyncio.sleep(0.5)
        entry = await get_audit_entry(member.guild, nextcord.AuditLogAction.kick, member.id)
        if entry and entry.action == nextcord.AuditLogAction.kick:
            await send_log(
                self.bot,
                "moderation",
                "MEMBRE KICKÉ",
                {
                    "Membre": f"{member} (ID: {member.id})",
                    "Modérateur": entry.user,
                    "Raison": entry.reason or "Non spécifiée"
                },
                audit_id=entry.id
            )

    # BAN
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        entry = await get_audit_entry(guild, nextcord.AuditLogAction.ban, user.id)
        await send_log(
            self.bot,
            "moderation",
            "MEMBRE BANNI",
            {
                "Utilisateur": f"{user} (ID: {user.id})",
                "Modérateur": entry.user if entry else "Inconnu",
                "Raison": entry.reason if entry else "Non spécifiée"
            },
            audit_id=entry.id if entry else None
        )

    # UNBAN
    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        entry = await get_audit_entry(guild, nextcord.AuditLogAction.unban, user.id)
        await send_log(
            self.bot,
            "moderation",
            "MEMBRE DÉBANNI",
            {
                "Utilisateur": f"{user} (ID: {user.id})",
                "Modérateur": entry.user if entry else "Inconnu"
            },
            audit_id=entry.id if entry else None
        )

# ============================================================
# LOGS VOCAUX — MUTE / UNMUTE / MOVE / JOIN / LEAVE
# ============================================================

class LogsVoice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel != after.channel:
            if after.channel is None:
                await send_log(
                    self.bot,
                    "voice",
                    "MEMBRE A QUITTÉ LE VOCAL",
                    {
                        "Membre": f"{member} (ID: {member.id})",
                        "Salon": before.channel.name if before.channel else "Inconnu",
                        "Durée": "Voir logs Discord"
                    }
                )
            else:
                await send_log(
                    self.bot,
                    "voice",
                    "MEMBRE A REJOINT LE VOCAL",
                    {
                        "Membre": f"{member} (ID: {member.id})",
                        "Salon": after.channel.name
                    }
                )

# ============================================================
# LOGS MESSAGES — DELETE / EDIT (ULTRA PREMIUM)
# ============================================================

class LogsMessages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # MESSAGE SUPPRIMÉ
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return

        await send_log(
            self.bot,
            "messages",
            "MESSAGE SUPPRIMÉ",
            {
                "Auteur": f"{message.author} (ID: {message.author.id})",
                "Salon": f"{message.channel.mention}",
                "Contenu": message.content[:1024] or "(vide)",
                "Lien": f"[Voir le message](https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id})"
            }
        )

    # MESSAGE ÉDITÉ
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content:
            return

        await send_log(
            self.bot,
            "messages",
            "MESSAGE ÉDITÉ",
            {
                "Auteur": f"{before.author} (ID: {before.author.id})",
                "Salon": f"{before.channel.mention}",
                "Avant": before.content[:512] or "(vide)",
                "Après": after.content[:512] or "(vide)"
            }
        )

# ============================================================
# COMMANDES DE CONFIGURATION DES LOGS
# ============================================================

class LogsConfig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="logs_setup")
    @commands.has_permissions(administrator=True)
    async def logs_setup(self, ctx, category: str = None, channel: nextcord.TextChannel = None):
        
        if not category:
            valid = ", ".join(LOG_CATEGORIES)
            return await ctx.send(
                embed=nextcord.Embed(
                    title="📋 Utilisation : `+logs_setup <catégorie> <salon>`",
                    description=f"""
**Exemple :**
```
{ctx.author.mention} logs_setup warn #general
```
""",
                    color=0xE74C3C
                )
            )

        category = category.lower()

        if category not in LOG_CATEGORIES:
            valid = ", ".join(LOG_CATEGORIES)
            return await ctx.send(
                embed=nextcord.Embed(
                    title="❌ Catégorie invalide",
                    description=f"Catégories valides :\n```\n{valid}\n```",
                    color=0xE74C3C
                )
            )

        LOG_CHANNELS[category] = channel.id
        save_config(LOG_CHANNELS)

        await ctx.send(
            embed=nextcord.Embed(
                title="✅ Log configuré",
                description=f"La catégorie **{category}** enverra désormais ses logs dans {channel.mention}.",
                color=0x2ECC71
            )
        )

    # ------------------------------------------------------------
    # /logs reset <catégorie>
    # ------------------------------------------------------------
    @commands.command(name="logs_reset")
    async def logs_reset(self, ctx, category: str):

        category = category.lower()

        if category not in LOG_CATEGORIES:
            valid = ", ".join(LOG_CATEGORIES)
            return await ctx.send(
                embed=nextcord.Embed(
                    title="❌ Catégorie invalide",
                    description=f"Catégories valides :\n```\n{valid}\n```",
                    color=0xE74C3C
                )
            )

        LOG_CHANNELS[category] = None
        save_config(LOG_CHANNELS)

        await ctx.send(
            embed=nextcord.Embed(
                title="♻️ Log réinitialisé",
                description=f"La catégorie **{category}** n’a plus de salon assigné.",
                color=0xF1C40F
            )
        )

    # ------------------------------------------------------------
    # /logs status
    # ------------------------------------------------------------
    @commands.command(name="logs_status")
    async def logs_status(self, ctx):

        embed = nextcord.Embed(
            title="📊 État des logs",
            description="Voici la configuration actuelle des logs :",
            color=0x3498db
        )

        for cat in LOG_CATEGORIES:
            channel_id = LOG_CHANNELS.get(cat)
            channel = ctx.guild.get_channel(channel_id) if channel_id else None

            embed.add_field(
                name=f"{CATEGORY_ICONS.get(cat, '📄')} {cat}",
                value=channel.mention if channel else "❌ Aucun salon",
                inline=False
            )

        await ctx.send(embed=embed)
# ============================================================
# SETUP FINAL DU COG — ASSEMBLAGE COMPLET
# ============================================================

def setup(bot):
    bot.add_cog(LogsModeration(bot))
    bot.add_cog(LogsVoice(bot))
    bot.add_cog(LogsMessages(bot))
    bot.add_cog(LogsConfig(bot))
