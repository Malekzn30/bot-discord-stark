import nextcord
from nextcord.ext import commands
from datetime import timedelta
import sqlite3
import os
import json
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from cogs.logs import send_log   # ← AJOUT OBLIGATOIRE
from utils.embeds import create_embed, create_error_embed, create_warn_embed, create_success_embed
from cogs.logs import log_command, log_moderation

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
                reason TEXT,
                moderator_id INTEGER
            )
        """)
        # Ajouter la colonne moderator_id si elle n'existe pas (pour compatibilité)
        try:
            self.cursor.execute("ALTER TABLE warns ADD COLUMN moderator_id INTEGER DEFAULT NULL")
        except sqlite3.OperationalError:
            # La colonne existe déjà, pas d'erreur
            pass
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

    @commands.command(name="warnlist")
    async def warnlist(self, ctx, member: nextcord.Member = None):
        if not member:
            embed = create_error_embed("Erreur", "Utilise : `+warnlist @membre`", ctx.guild, self.bot)
            await ctx.send(embed=embed)
            return

        self.cursor.execute("SELECT reason, moderator_id FROM warns WHERE user_id = ?", (member.id,))
        rows = self.cursor.fetchall()

        if not rows:
            embed = create_success_embed("Aucun avertissement", f"{member.mention} n'a aucun avertissement enregistré.", ctx.guild, self.bot)
            embed.set_thumbnail(url=member.display_avatar.url)
            await ctx.send(embed=embed)
            return

        embed = create_warn_embed(f"Liste des avertissements - {member.display_name}", "", ctx.guild, self.bot)
        embed.set_thumbnail(url=member.display_avatar.url)
        
        for i, (reason, moderator_id) in enumerate(rows, 1):
            moderator = ctx.guild.get_member(moderator_id) if moderator_id else None
            moderator_name = moderator.display_name if moderator else "Modérateur inconnu"
            
            embed.add_field(
                name=f"Warn #{i}",
                value=f"📄 **Raison** : {reason}\n👮 **Par** : {moderator_name}",
                inline=False
            )
        
        embed.set_footer(text=f"Total : {len(rows)} avertissement{'s' if len(rows) > 1 else ''}")
        await ctx.send(embed=embed)

    @commands.command(name="unwarn")
    async def unwarn(self, ctx, member: nextcord.Member = None, index: int = None):
        if not member or index is None:
            embed = nextcord.Embed(
                title="❌ Erreur",
                description="Utilise : `+unwarn @membre <index>`",
                color=0xff6b6b
            )
            await ctx.send(embed=embed)
            return

        self.cursor.execute("SELECT rowid, reason FROM warns WHERE user_id = ?", (member.id,))
        rows = self.cursor.fetchall()

        if index < 1 or index > len(rows):
            embed = nextcord.Embed(
                title="❌ Index invalide",
                description=f"Index doit être entre 1 et {len(rows)}",
                color=0xff6b6b
            )
            await ctx.send(embed=embed)
            return

        rowid = rows[index - 1][0]
        reason = rows[index - 1][1]

        self.cursor.execute("DELETE FROM warns WHERE rowid = ?", (rowid,))
        self.db.commit()

        embed = nextcord.Embed(
            title="🧹 Avertissement retiré",
            color=0x2ecc71,
            timestamp=ctx.message.created_at
        )
        embed.add_field(name="👤 Membre", value=member.mention, inline=False)
        embed.add_field(name="📄 Raison du warn retiré", value=reason, inline=False)
        embed.add_field(name="👮 Retiré par", value=ctx.author.mention, inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Retiré par {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)

    @commands.command(name="clearwarns")
    async def clearwarns(self, ctx, member: nextcord.Member = None):
        if not member:
            embed = nextcord.Embed(
                title="❌ Erreur",
                description="Utilise : `+clearwarns @membre`",
                color=0xff6b6b
            )
            await ctx.send(embed=embed)
            return

        # Compter le nombre de warns avant suppression
        self.cursor.execute("SELECT COUNT(*) FROM warns WHERE user_id = ?", (member.id,))
        warn_count = self.cursor.fetchone()[0]

        self.cursor.execute("DELETE FROM warns WHERE user_id = ?", (member.id,))
        self.db.commit()

        embed = nextcord.Embed(
            title="🧼 Tous les warns supprimés",
            color=0x2ecc71,
            timestamp=ctx.message.created_at
        )
        embed.add_field(name="👤 Membre", value=member.mention, inline=False)
        embed.add_field(name="📊 Nombre supprimé", value=f"**{warn_count}** avertissement{'s' if warn_count > 1 else ''}", inline=False)
        embed.add_field(name="👮 Supprimé par", value=ctx.author.mention, inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Supprimé par {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)

    @commands.command(name="warn_leaderboard", aliases=["warnlb", "warnrank"])
    async def warn_leaderboard(self, ctx, limit: int = 10):
        """Affiche le classement des membres avec le plus d'avertissements"""
        # Récupérer tous les warns groupés par utilisateur
        self.cursor.execute("""
            SELECT user_id, COUNT(*) as warn_count 
            FROM warns 
            GROUP BY user_id 
            ORDER BY warn_count DESC 
            LIMIT ?
        """, (limit,))
        
        rows = self.cursor.fetchall()
        
        if not rows:
            return await ctx.send("✅ Aucun avertissement enregistré !")
        
        # Créer l'embed du leaderboard
        embed = nextcord.Embed(
            title="⚠️ Classement des Avertissements",
            description=f"Top {len(rows)} membres avec le plus de warns",
            color=0xff6b6b
        )
        
        # Ajouter chaque membre au classement
        for i, (user_id, warn_count) in enumerate(rows, 1):
            member = ctx.guild.get_member(user_id)
            if member:
                # Ajouter une médaille pour les 3 premiers
                medal = ""
                if i == 1:
                    medal = "🥇"
                elif i == 2:
                    medal = "🥈"
                elif i == 3:
                    medal = "🥉"
                else:
                    medal = f"#{i}"
                
                embed.add_field(
                    name=f"{medal} {member.display_name}",
                    value=f"**{warn_count}** avertissement{'s' if warn_count > 1 else ''}",
                    inline=False
                )
            else:
                # Si le membre n'est plus sur le serveur
                embed.add_field(
                    name=f"#{i} Utilisateur inconnu",
                    value=f"**{warn_count}** avertissement{'s' if warn_count > 1 else ''}",
                    inline=False
                )
        
        embed.set_footer(text=f"Total: {sum(row[1] for row in rows)} warns enregistrés")
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        
        await ctx.send(embed=embed)

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
            embed = nextcord.Embed(
                title="❌ Erreur",
                description="Utilise : `+warn_check @membre`",
                color=0xff6b6b
            )
            await ctx.send(embed=embed)
            return
            
        self.cursor.execute("SELECT COUNT(*) FROM warns WHERE user_id = ?", (member.id,))
        count = self.cursor.fetchone()[0]
        
        embed = nextcord.Embed(
            title="⚠️ Vérification des avertissements",
            color=0xff6b6b if count > 0 else 0x2ecc71,
            timestamp=ctx.message.created_at
        )
        embed.add_field(name="👤 Membre vérifié", value=member.mention, inline=False)
        embed.add_field(name="📊 Nombre de warns", value=f"**{count}** avertissement{'s' if count > 1 else ''}", inline=False)
        embed.add_field(name="📈 Statut", value="⚠️ Membre averti" if count > 0 else "✅ Membre clean", inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Vérifié par {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)

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
