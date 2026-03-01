import nextcord
from nextcord.ext import commands
from datetime import datetime, timedelta
import json
import os
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
        save_config(DEFAULT_LOG_CHANNELS)
        return DEFAULT_LOG_CHANNELS.copy()

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        # S'assurer que toutes les catégories existent
        for cat in LOG_CATEGORIES:
            if cat not in data:
                data[cat] = None

        return data

    except Exception:
        return DEFAULT_LOG_CHANNELS.copy()

def save_config(config):
    try:
        tmp = CONFIG_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        os.replace(tmp, CONFIG_PATH)
    except Exception:
        pass

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
        return

    channel = bot.get_channel(channel_id)
    if not channel:
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
        embed.add_field(name=f"• {name}", value=value, inline=False)

    # Ajout de l'Audit Log ID si disponible
    if audit_id:
        embed.add_field(name="• Audit Log ID", value=str(audit_id), inline=False)

    embed.set_footer(text=f"Catégorie : {category}")

    await channel.send(embed=embed)
# ============================================================
# AUDIT LOG HELPER (RÉCUPÈRE L'AUTEUR RÉEL DE L'ACTION)
# ============================================================

async def get_audit_entry(guild, action_type, target_id):
    """
    Récupère l'entrée d'audit log correspondant à une action.
    action_type = nextcord.AuditLogAction.<ACTION>
    target_id = ID de la cible
    """

    # Délai pour laisser Discord mettre à jour l'audit log
    await asyncio.sleep(0.5)

    try:
        async for entry in guild.audit_logs(limit=5, action=action_type):
            if entry.target and entry.target.id == target_id:
                return entry
    except Exception:
        return None

    return None
# ============================================================
# LOGS MODÉRATION — TIMEOUT / KICK / BAN / ROLES / NICKNAMES
# ============================================================

class LogsModeration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ------------------------------------------------------------
    # TIMEOUT / UNTIMEOUT (détecté automatiquement)
    # ------------------------------------------------------------
    @commands.Cog.listener()
    async def on_member_update(self, before, after):

        # TIMEOUT APPLIQUÉ
        if before.communication_disabled_until != after.communication_disabled_until:

            # Timeout appliqué
            if after.communication_disabled_until is not None:
                entry = await get_audit_entry(
                    after.guild,
                    nextcord.AuditLogAction.member_update,
                    after.id
                )

                actor = entry.user if entry else "Inconnu"
                reason = entry.reason if entry else "Non spécifiée"

                await send_log(
                    bot=self.bot,
                    category="moderation",
                    title="TIMEOUT APPLIQUÉ",
                    fields={
                        "Auteur": f"{actor} (ID: {actor.id})" if actor != "Inconnu" else "Inconnu",
                        "Cible": f"{after} (ID: {after.id})",
                        "Expire": str(after.communication_disabled_until),
                        "Raison": reason
                    },
                    audit_id=entry.id if entry else None
                )

            # Timeout retiré
            else:
                entry = await get_audit_entry(
                    after.guild,
                    nextcord.AuditLogAction.member_update,
                    after.id
                )

                actor = entry.user if entry else "Inconnu"
                reason = entry.reason if entry else "Non spécifiée"

                await send_log(
                    bot=self.bot,
                    category="moderation",
                    title="TIMEOUT RETIRÉ",
                    fields={
                        "Auteur": f"{actor} (ID: {actor.id})" if actor != "Inconnu" else "Inconnu",
                        "Cible": f"{after} (ID: {after.id})",
                        "Raison": reason
                    },
                    audit_id=entry.id if entry else None
                )

        # ------------------------------------------------------------
        # RÔLES AJOUTÉS / RETIRÉS
        # ------------------------------------------------------------
        if before.roles != after.roles:
            before_set = set(before.roles)
            after_set = set(after.roles)

            added = after_set - before_set
            removed = before_set - after_set

            # Rôle ajouté
            for role in added:
                entry = await get_audit_entry(
                    after.guild,
                    nextcord.AuditLogAction.member_role_update,
                    after.id
                )

                actor = entry.user if entry else "Inconnu"
                reason = entry.reason if entry else "Non spécifiée"

                await send_log(
                    bot=self.bot,
                    category="roles",
                    title="RÔLE AJOUTÉ",
                    fields={
                        "Auteur": f"{actor} (ID: {actor.id})" if actor != "Inconnu" else "Inconnu",
                        "Cible": f"{after} (ID: {after.id})",
                        "Rôle ajouté": f"{role.name} (ID: {role.id})",
                        "Raison": reason
                    },
                    audit_id=entry.id if entry else None
                )

            # Rôle retiré
            for role in removed:
                entry = await get_audit_entry(
                    after.guild,
                    nextcord.AuditLogAction.member_role_update,
                    after.id
                )

                actor = entry.user if entry else "Inconnu"
                reason = entry.reason if entry else "Non spécifiée"

                await send_log(
                    bot=self.bot,
                    category="roles",
                    title="RÔLE RETIRÉ",
                    fields={
                        "Auteur": f"{actor} (ID: {actor.id})" if actor != "Inconnu" else "Inconnu",
                        "Cible": f"{after} (ID: {after.id})",
                        "Rôle retiré": f"{role.name} (ID: {role.id})",
                        "Raison": reason
                    },
                    audit_id=entry.id if entry else None
                )

        # ------------------------------------------------------------
        # PSEUDO MODIFIÉ
        # ------------------------------------------------------------
        if before.nick != after.nick:
            entry = await get_audit_entry(
                after.guild,
                nextcord.AuditLogAction.member_update,
                after.id
            )

            actor = entry.user if entry else "Inconnu"
            reason = entry.reason if entry else "Non spécifiée"

            await send_log(
                bot=self.bot,
                category="nicknames",
                title="PSEUDO MODIFIÉ",
                fields={
                    "Auteur": f"{actor} (ID: {actor.id})" if actor != "Inconnu" else "Inconnu",
                    "Cible": f"{after} (ID: {after.id})",
                    "Avant": before.nick or "Aucun",
                    "Après": after.nick or "Aucun",
                    "Raison": reason
                },
                audit_id=entry.id if entry else None
            )

    # ------------------------------------------------------------
    # KICK
    # ------------------------------------------------------------
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        entry = await get_audit_entry(
            member.guild,
            nextcord.AuditLogAction.kick,
            member.id
        )

        if not entry:
            return

        await send_log(
            bot=self.bot,
            category="moderation",
            title="KICK",
            fields={
                "Auteur": f"{entry.user} (ID: {entry.user.id})",
                "Cible": f"{member} (ID: {member.id})",
                "Raison": entry.reason or "Non spécifiée"
            },
            audit_id=entry.id
        )

    # ------------------------------------------------------------
    # BAN
    # ------------------------------------------------------------
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        entry = await get_audit_entry(
            guild,
            nextcord.AuditLogAction.ban,
            user.id
        )

        await send_log(
            bot=self.bot,
            category="moderation",
            title="BAN",
            fields={
                "Auteur": f"{entry.user} (ID: {entry.user.id})" if entry else "Inconnu",
                "Cible": f"{user} (ID: {user.id})",
                "Raison": entry.reason if entry else "Non spécifiée"
            },
            audit_id=entry.id if entry else None
        )

    # ------------------------------------------------------------
    # UNBAN
    # ------------------------------------------------------------
    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        entry = await get_audit_entry(
            guild,
            nextcord.AuditLogAction.unban,
            user.id
        )

        await send_log(
            bot=self.bot,
            category="moderation",
            title="UNBAN",
            fields={
                "Auteur": f"{entry.user} (ID: {entry.user.id})" if entry else "Inconnu",
                "Cible": f"{user} (ID: {user.id})",
                "Raison": entry.reason if entry else "Non spécifiée"
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

        guild = member.guild

        # ------------------------------------------------------------
        # JOIN VOCAL
        # ------------------------------------------------------------
        if before.channel is None and after.channel is not None:
            await send_log(
                bot=self.bot,
                category="voice",
                title="CONNEXION VOCALE",
                fields={
                    "Utilisateur": f"{member} (ID: {member.id})",
                    "Salon": f"{after.channel.name} (ID: {after.channel.id})"
                }
            )

        # ------------------------------------------------------------
        # LEAVE VOCAL
        # ------------------------------------------------------------
        if before.channel is not None and after.channel is None:
            await send_log(
                bot=self.bot,
                category="voice",
                title="DÉCONNEXION VOCALE",
                fields={
                    "Utilisateur": f"{member} (ID: {member.id})",
                    "Salon": f"{before.channel.name} (ID: {before.channel.id})"
                }
            )

        # ------------------------------------------------------------
        # MOVE VOCAL
        # ------------------------------------------------------------
        if before.channel != after.channel and before.channel and after.channel:
            entry = await get_audit_entry(
                guild,
                nextcord.AuditLogAction.member_move,
                member.id
            )

            actor = entry.user if entry else "Inconnu"

            await send_log(
                bot=self.bot,
                category="voice",
                title="DÉPLACEMENT VOCAL",
                fields={
                    "Auteur": f"{actor} (ID: {actor.id})" if actor != "Inconnu" else "Inconnu",
                    "Cible": f"{member} (ID: {member.id})",
                    "De": f"{before.channel.name} (ID: {before.channel.id})",
                    "Vers": f"{after.channel.name} (ID: {after.channel.id})"
                },
                audit_id=entry.id if entry else None
            )

        # ------------------------------------------------------------
        # MUTE / UNMUTE
        # ------------------------------------------------------------
        if before.mute != after.mute:
            action = "MUTE" if after.mute else "UNMUTE"

            entry = await get_audit_entry(
                guild,
                nextcord.AuditLogAction.member_update,
                member.id
            )

            actor = entry.user if entry else "Inconnu"

            await send_log(
                bot=self.bot,
                category="voice",
                title=f"{action} VOCAL",
                fields={
                    "Auteur": f"{actor} (ID: {actor.id})" if actor != "Inconnu" else "Inconnu",
                    "Cible": f"{member} (ID: {member.id})",
                    "Salon": f"{after.channel.name} (ID: {after.channel.id})" if after.channel else "Aucun"
                },
                audit_id=entry.id if entry else None
            )

        # ------------------------------------------------------------
        # DEAF / UNDEAF
        # ------------------------------------------------------------
        if before.deaf != after.deaf:
            action = "DEAF" if after.deaf else "UNDEAF"

            entry = await get_audit_entry(
                guild,
                nextcord.AuditLogAction.member_update,
                member.id
            )

            actor = entry.user if entry else "Inconnu"

            await send_log(
                bot=self.bot,
                category="voice",
                title=f"{action} VOCAL",
                fields={
                    "Auteur": f"{actor} (ID: {actor.id})" if actor != "Inconnu" else "Inconnu",
                    "Cible": f"{member} (ID: {member.id})",
                    "Salon": f"{after.channel.name} (ID: {after.channel.id})" if after.channel else "Aucun"
                },
                audit_id=entry.id if entry else None
            )
# ============================================================
# LOGS MESSAGES — DELETE / EDIT (ULTRA PREMIUM)
# ============================================================

class LogsMessages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ------------------------------------------------------------
    # MESSAGE SUPPRIMÉ
    # ------------------------------------------------------------
    @commands.Cog.listener()
    async def on_message_delete(self, message):

        # Ignore les bots
        if message.author.bot:
            return

        await send_log(
            bot=self.bot,
            category="messages",
            title="MESSAGE SUPPRIMÉ",
            fields={
                "Auteur": f"{message.author} (ID: {message.author.id})",
                "Salon": f"{message.channel.name} (ID: {message.channel.id})",
                "Contenu": message.content if message.content else "*Aucun contenu*",
                "Message ID": message.id
            }
        )

    # ------------------------------------------------------------
    # MESSAGE ÉDITÉ
    # ------------------------------------------------------------
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):

        # Ignore les bots
        if before.author.bot:
            return

        # Ignore si aucun changement
        if before.content == after.content:
            return

        await send_log(
            bot=self.bot,
            category="messages",
            title="MESSAGE ÉDITÉ",
            fields={
                "Auteur": f"{before.author} (ID: {before.author.id})",
                "Salon": f"{before.channel.name} (ID: {before.channel.id})",
                "Avant": before.content if before.content else "*Aucun contenu*",
                "Après": after.content if after.content else "*Aucun contenu*",
                "Message ID": before.id
            }
        )
# ============================================================
# COMMANDES DE CONFIGURATION DES LOGS
# ============================================================

class LogsConfig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ------------------------------------------------------------
    # /logs setup <catégorie> <salon>
    # ------------------------------------------------------------
    @commands.command(name="logs_setup")
    async def logs_setup(self, ctx, category: str, channel: nextcord.TextChannel):

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
