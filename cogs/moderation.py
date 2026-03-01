import nextcord
from nextcord.ext import commands
from datetime import timedelta
import sqlite3
import os
import json

from cogs.logs import send_log   # ← AJOUT OBLIGATOIRE

# ----- gestion des permissions de commandes -----
COMMAND_ROLES_PATH = os.path.join(os.path.dirname(__file__), "command_roles.json")

def load_command_roles():
    if not os.path.exists(COMMAND_ROLES_PATH):
        with open(COMMAND_ROLES_PATH, "w") as f:
            json.dump({}, f, indent=4)
        return {}
    try:
        with open(COMMAND_ROLES_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def save_command_roles(cfg):
    try:
        with open(COMMAND_ROLES_PATH, "w") as f:
            json.dump(cfg, f, indent=4)
    except Exception as e:
        print(f"❌ Erreur save_command_roles: {e}")

COMMAND_ROLES = load_command_roles()

async def role_permission_check(ctx):
    # les admins peuvent tout faire
    if ctx.author.guild_permissions.administrator:
        return True
    allowed = COMMAND_ROLES.get(ctx.command.name)
    # si la commande n'est pas configurée, on laisse passer
    if allowed is None or allowed == []:
        return True
    return any(r.id in allowed for r in ctx.author.roles)

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = sqlite3.connect("warns.sqlite")
        self.cursor = self.db.cursor()
        # Optimiser SQLite pour moins de mémoire
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=NORMAL")
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS warns (
                user_id INTEGER,
                reason TEXT
            )
        """)
        # Créer un index sur user_id pour les requêtes rapides
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON warns(user_id)")
        self.db.commit()

    # ============================================================
    # SERVERINFO
    # ============================================================
    @commands.command(name="serverinfo")
    async def serverinfo(self, ctx):
        g = ctx.guild
        embed = nextcord.Embed(title=f"📌 Infos du serveur : {g.name}", color=0x2F3136)
        embed.add_field(name="👥 Membres", value=g.member_count)
        embed.add_field(name="💬 Textuels", value=len(g.text_channels))
        embed.add_field(name="🔊 Vocaux", value=len(g.voice_channels))
        embed.add_field(name="🚀 Boosts", value=g.premium_subscription_count)
        embed.set_thumbnail(url=g.icon.url if g.icon else None)
        await ctx.send(embed=embed)

    # ============================================================
    # USERINFO
    # ============================================================
    @commands.command(name="userinfo")
    async def userinfo(self, ctx, member: nextcord.Member = None):
        member = member or ctx.author
        embed = nextcord.Embed(title=f"👤 Infos : {member}", color=0x2F3136)
        embed.add_field(name="ID", value=member.id)
        embed.add_field(name="Compte créé", value=member.created_at.strftime("%d/%m/%Y"))
        embed.add_field(name="A rejoint", value=member.joined_at.strftime("%d/%m/%Y"))
        embed.add_field(name="Rôles", value=", ".join([r.mention for r in member.roles if r.name != '@everyone']) or "Aucun")
        embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
        await ctx.send(embed=embed)

    # ============================================================
    # CLEAR
    # ============================================================
    @commands.command(name="clear")
    async def clear(self, ctx, amount: int = None):
        if not amount:
            return await ctx.send("❌ Utilise : `+clear <nombre>`")
        await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"🧹 {amount} messages supprimés.", delete_after=3)

    @commands.command(name="clearuser")
    async def clearuser(self, ctx, member: nextcord.Member = None, amount: int = 100):
        if not member:
            return await ctx.send("❌ Utilise : `+clearuser @membre <nombre>`")
        deleted = await ctx.channel.purge(limit=amount, check=lambda m: m.author == member)
        await ctx.send(f"🧹 {len(deleted)} messages supprimés de {member.mention}.", delete_after=3)

    @commands.command(name="clearbots")
    async def clearbots(self, ctx, amount: int = 100):
        deleted = await ctx.channel.purge(limit=amount, check=lambda m: m.author.bot)
        await ctx.send(f"🤖 {len(deleted)} messages de bots supprimés.", delete_after=3)

    @commands.command(name="clearembeds")
    async def clearembeds(self, ctx, amount: int = 100):
        deleted = await ctx.channel.purge(limit=amount, check=lambda m: m.embeds)
        await ctx.send(f"🖼️ {len(deleted)} embeds supprimés.", delete_after=3)

    # ============================================================
    # KICK
    # ============================================================
    @commands.command(name="kick")
    async def kick(self, ctx, member: nextcord.Member = None, *, reason="Aucune raison"):
        if not member:
            return await ctx.send("❌ Utilise : `+kick @membre [raison]`")
        await member.kick(reason=reason)
        await ctx.send(f"👢 {member.mention} a été **kick**.\n📄 Raison : {reason}")

    # ============================================================
    # BAN / UNBAN / TEMPBAN / SOFTBAN
    # ============================================================
    @commands.command(name="ban")
    async def ban(self, ctx, member: nextcord.Member = None, *, reason="Aucune raison"):
        if not member:
            return await ctx.send("❌ Utilise : `+ban @membre [raison]`")
        await member.ban(reason=reason)
        await ctx.send(f"🔨 {member.mention} a été **banni**.\n📄 Raison : {reason}")

    @commands.command(name="unban")
    async def unban(self, ctx, *, user: str = None):
        if not user:
            return await ctx.send("❌ Utilise : `+unban nom#tag`")

        banned = await ctx.guild.bans()
        name, discrim = user.split("#")

        for ban_entry in banned:
            if ban_entry.user.name == name and ban_entry.user.discriminator == discrim:
                await ctx.guild.unban(ban_entry.user)
                return await ctx.send(f"✅ {user} a été **débanni**.")

        await ctx.send("❌ Utilisateur introuvable.")

    @commands.command(name="tempban")
    async def tempban(self, ctx, member: nextcord.Member = None, minutes: int = None, *, reason="Aucune raison"):
        if not member or not minutes:
            return await ctx.send("❌ Utilise : `+tempban @membre <minutes> [raison]`")

        await member.ban(reason=reason)
        await ctx.send(f"⏳ {member.mention} banni pour **{minutes} minutes**.")

        async def unban_later():
            await asyncio.sleep(minutes * 60)
            await ctx.guild.unban(member)

        self.bot.loop.create_task(unban_later())

    @commands.command(name="softban")
    async def softban(self, ctx, member: nextcord.Member = None, *, reason="Aucune raison"):
        if not member:
            return await ctx.send("❌ Utilise : `+softban @membre [raison]`")
        await member.ban(reason=reason)
        await ctx.guild.unban(member)
        await ctx.send(f"🧨 {member.mention} a été **softban**.")

    # ============================================================
    # MASSBAN / MASSKICK
    # ============================================================
    @commands.command(name="masskick")
    async def masskick(self, ctx, *members: nextcord.Member):
        if not members:
            return await ctx.send("❌ Utilise : `+masskick @u1 @u2 ...`")

        for m in members:
            try:
                await m.kick(reason="Masskick")
            except:
                pass

        await ctx.send(f"👢 {len(members)} membres kick.")

    @commands.command(name="massban")
    async def massban(self, ctx, *members: nextcord.Member):
        if not members:
            return await ctx.send("❌ Utilise : `+massban @u1 @u2 ...`")

        for m in members:
            try:
                await m.ban(reason="Massban")
            except:
                pass

        await ctx.send(f"🔨 {len(members)} membres bannis.")

    # ============================================================
    # MUTE / UNMUTE (ROLE)
    # ============================================================
    @commands.command(name="mute")
    async def mute(self, ctx, member: nextcord.Member = None, *, reason="Aucune raison"):
        if not member:
            return await ctx.send("❌ Utilise : `+mute @membre [raison]`")

        role = nextcord.utils.get(ctx.guild.roles, name="Muted")
        if not role:
            role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(role, speak=False, send_messages=False)

        await member.add_roles(role)
        await ctx.send(f"🔇 {member.mention} mute.\n📄 Raison : {reason}")

    @commands.command(name="unmute")
    async def unmute(self, ctx, member: nextcord.Member = None):
        if not member:
            return await ctx.send("❌ Utilise : `+unmute @membre`")

        role = nextcord.utils.get(ctx.guild.roles, name="Muted")
        if role in member.roles:
            await member.remove_roles(role)
            return await ctx.send(f"🔊 {member.mention} unmute.")

        await ctx.send("❌ Ce membre n'est pas mute.")

    # ============================================================
    # TIMEOUT / UNTIMEOUT
    # ============================================================
    @commands.command(name="timeout")
    async def timeout(self, ctx, member: nextcord.Member = None, minutes: int = None):
        if not member or not minutes:
            return await ctx.send("❌ Utilise : `+timeout @membre <minutes>`")

        duration = timedelta(minutes=minutes)
        await member.edit(timeout=nextcord.utils.utcnow() + duration)
        await ctx.send(f"⏳ Timeout de {member.mention} pour **{minutes} minutes**.")

    @commands.command(name="untimeout")
    async def untimeout(self, ctx, member: nextcord.Member = None):
        if not member:
            return await ctx.send("❌ Utilise : `+untimeout @membre`")

        await member.edit(timeout=None)
        await ctx.send(f"🔓 Timeout retiré pour {member.mention}.")

    # ============================================================
    # WARNS (SQLite)
    # ============================================================
    @commands.command(name="warn")
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx, member: nextcord.Member = None, *, reason="Aucune raison"):
        if not member:
            await ctx.send("❌ Veuillez mentionner un membre.")
            return

        if member == ctx.author:
            await ctx.send("❌ Vous ne pouvez pas vous warn vous-même.")
            return

        self.cursor.execute("INSERT INTO warns (user_id, reason) VALUES (?, ?)", (member.id, reason))
        self.db.commit()

        warn_count = self.cursor.execute(
            "SELECT COUNT(*) FROM warns WHERE user_id = ?", (member.id,)
        ).fetchone()[0]

        await ctx.send(
            f"⚠️ {member.mention} a reçu un **warn**.\n"
            f"📄 Raison : {reason}\n📊 Total : {warn_count}"
        )

        # attribution du rôle de warn
        role = ctx.guild.get_role(1477499178363129867)
        if role:
            try:
                await member.add_roles(role, reason="Warn automatique")
            except Exception:
                pass  # on ignore si ça échoue

        # envoi du log
        await send_log(
            self.bot,
            "warn",
            "WARN APPLIQUÉ",
            {
                "Auteur": f"{ctx.author} (ID: {ctx.author.id})",
                "Cible": f"{member} (ID: {member.id})",
                "Raison": reason,
                "Total warns": str(warn_count)
            }
        )

    @commands.command(name="warnlist")
    async def warnlist(self, ctx, member: nextcord.Member = None):
        if not member:
            return await ctx.send("❌ Utilise : `+warnlist @membre`")

        self.cursor.execute("SELECT reason FROM warns WHERE user_id = ?", (member.id,))
        rows = self.cursor.fetchall()

        if not rows:
            return await ctx.send("✔️ Aucun avertissement.")

        desc = "\n".join([f"{i+1}. {r[0]}" for i, r in enumerate(rows)])
        await ctx.send(f"⚠️ Warns de {member.mention} :\n{desc}")

    @commands.command(name="unwarn")
    async def unwarn(self, ctx, member: nextcord.Member = None, index: int = None):
        if not member or index is None:
            return await ctx.send("❌ Utilise : `+unwarn @membre <index>`")

        self.cursor.execute("SELECT rowid, reason FROM warns WHERE user_id = ?", (member.id,))
        rows = self.cursor.fetchall()

        if index < 1 or index > len(rows):
            return await ctx.send("❌ Index invalide.")

        rowid = rows[index - 1][0]

        self.cursor.execute("DELETE FROM warns WHERE rowid = ?", (rowid,))
        self.db.commit()

        await ctx.send(f"🧹 Warn retiré : {rows[index - 1][1]}")

    @commands.command(name="clearwarns")
    async def clearwarns(self, ctx, member: nextcord.Member = None):
        if not member:
            return await ctx.send("❌ Utilise : `+clearwarns @membre`")

        self.cursor.execute("DELETE FROM warns WHERE user_id = ?", (member.id,))
        self.db.commit()

        await ctx.send(f"🧼 Tous les warns de {member.mention} ont été supprimés.")


    # ============================================================
    # LOCK / UNLOCK
    # ============================================================
    @commands.command(name="lock")
    async def lock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send("🔒 Salon verrouillé.")

    @commands.command(name="unlock")
    async def unlock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await ctx.send("🔓 Salon déverrouillé.")

    # ============================================================
    # SLOWMODE
    # ============================================================
    @commands.command(name="slowmode")
    async def slowmode(self, ctx, seconds: int = None):
        if seconds is None:
            return await ctx.send("❌ Utilise : `+slowmode <secondes>`")
        await ctx.channel.edit(slowmode_delay=seconds)
        await ctx.send(f"🐌 Slowmode réglé sur **{seconds}s**.")

    @commands.command(name="slowmode_disable")
    async def slowmode_disable(self, ctx):
        await ctx.channel.edit(slowmode_delay=0)
        await ctx.send("🚀 Slowmode désactivé.")

    @commands.command(name="massunmute")
    async def massunmute(self, ctx):
        role = nextcord.utils.get(ctx.guild.roles, name="Muted")
        if not role:
            return await ctx.send("❌ Rôle 'Muted' introuvable.")
        count = 0
        for member in role.members:
            try:
                await member.remove_roles(role)
                count += 1
            except Exception:
                pass
        await ctx.send(f"🔊 {count} membres unmute.")

    @commands.command(name="warn_check")
    async def warn_check(self, ctx, member: nextcord.Member = None):
        if not member:
            return await ctx.send("❌ Utilise : `+warn_check @membre`")
        self.cursor.execute("SELECT COUNT(*) FROM warns WHERE user_id = ?", (member.id,))
        count = self.cursor.fetchone()[0]
        await ctx.send(f"⚠️ {member.mention} a **{count}** avertissements.")

    @commands.command(name="bulkdelete")
    async def bulkdelete(self, ctx, limit: int = 50):
        deleted = await ctx.channel.purge(limit=limit + 1)
        await ctx.send(f"🗑️ {len(deleted)-1} messages supprimés.", delete_after=3)

    # ============================================================
    # SETNICK / RESETNICK
    # ============================================================
    @commands.command(name="setnick")
    async def setnick(self, ctx, member: nextcord.Member = None, *, nickname=None):
        if not member or not nickname:
            return await ctx.send("❌ Utilise : `+setnick @membre <pseudo>`")
        await member.edit(nick=nickname)
        await ctx.send(f"✏️ Nouveau pseudo : **{nickname}**")

    @commands.command(name="resetnick")
    async def resetnick(self, ctx, member: nextcord.Member = None):
        if not member:
            return await ctx.send("❌ Utilise : `+resetnick @membre`")
        await member.edit(nick=None)
        await ctx.send("♻️ Pseudo réinitialisé.")

def setup(bot):
    bot.add_cog(Moderation(bot))
    bot.check(role_permission_check)
