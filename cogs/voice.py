import nextcord
from nextcord.ext import commands
import asyncio
import random
from config import AUTHORIZED_ROLE_ID

last_moves = {}
shuffle_tasks = {}

def has_role():
    async def predicate(ctx):
        role = ctx.guild.get_role(AUTHORIZED_ROLE_ID)
        return role in ctx.author.roles
    return commands.check(predicate)

def embed_msg(title, desc, color=0x3498db):
    return nextcord.Embed(title=title, description=desc, color=color)

def format_channel(ch):
    return f"🔊 **{ch.name}**"


class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ============================================================
    # 1) MOOVE 1 PERSONNE → 1 SALON
    # ============================================================
    @commands.command(name="moove", aliases=["move"])
    @has_role()
    async def moove(self, ctx, member: nextcord.Member = None, channel: nextcord.VoiceChannel = None):
        if not member or not channel:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+moove @user #salon`", 0xff0000))

        if not member.voice:
            return await ctx.send(embed=embed_msg("❌ Erreur", "Ce membre n'est pas en vocal.", 0xff0000))

        old = member.voice.channel
        await member.move_to(channel)
        last_moves[member.id] = old.id

        await ctx.send(embed=embed_msg("🚚 Déplacé", f"{member.mention} → {format_channel(channel)}"))

    # ============================================================
    # 2) MOOVE PLUSIEURS PERSONNES → 1 SALON
    # ============================================================
    @commands.command(name="mooveusers")
    @has_role()
    async def mooveusers(self, ctx, *args):
        if len(args) < 2:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+mooveusers @u1 @u2 ... #salon`", 0xff0000))

        channel = ctx.message.channel_mentions[-1]
        mentions = ctx.message.mentions

        if not channel or not isinstance(channel, nextcord.VoiceChannel):
            return await ctx.send(embed=embed_msg("❌ Erreur", "Le dernier argument doit être un salon vocal.", 0xff0000))

        if not mentions:
            return await ctx.send(embed=embed_msg("❌ Aucun membre", "Mentionne au moins 1 membre.", 0xff0000))

        moved = 0
        for m in mentions:
            if m.voice:
                old = m.voice.channel
                await m.move_to(channel)
                last_moves[m.id] = old.id
                moved += 1

        await ctx.send(embed=embed_msg("🚚 Déplacement effectué", f"{moved} membres → {format_channel(channel)}"))

    # ============================================================
    # 3) MOOVE 1 PERSONNE → RANDOM CATÉGORIE
    # ============================================================
    @commands.command(name="mooverandom")
    @has_role()
    async def mooverandom(self, ctx, member: nextcord.Member = None, category_id: int = None):
        if not member or not category_id:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+mooverandom @user <ID_CAT>`", 0xff0000))

        if not member.voice:
            return await ctx.send(embed=embed_msg("❌ Erreur", "Ce membre n'est pas en vocal.", 0xff0000))

        cat = ctx.guild.get_channel(category_id)
        vcs = [c for c in cat.channels if isinstance(c, nextcord.VoiceChannel)]

        target = random.choice(vcs)
        old = member.voice.channel
        await member.move_to(target)
        last_moves[member.id] = old.id

        await ctx.send(embed=embed_msg("🎲 Déplacement aléatoire", f"{member.mention} → {format_channel(target)}"))

    # ============================================================
    # 4) MOOVE PLUSIEURS PERSONNES → RANDOM CATÉGORIE (NOUVEAU)
    # ============================================================
    @commands.command(name="mooverandomusers")
    @has_role()
    async def mooverandomusers(self, ctx, *args):
        if len(args) < 2:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+mooverandomusers @u1 @u2 ... <ID_CAT>`", 0xff0000))

        try:
            cat_id = int(args[-1])
        except:
            return await ctx.send(embed=embed_msg("❌ Erreur", "Le dernier argument doit être un ID de catégorie.", 0xff0000))

        mentions = ctx.message.mentions
        if not mentions:
            return await ctx.send(embed=embed_msg("❌ Aucun membre", "Mentionne au moins 1 membre.", 0xff0000))

        cat = ctx.guild.get_channel(cat_id)
        vcs = [c for c in cat.channels if isinstance(c, nextcord.VoiceChannel)]

        moved = 0
        for m in mentions:
            if m.voice:
                target = random.choice(vcs)
                old = m.voice.channel
                await m.move_to(target)
                last_moves[m.id] = old.id
                moved += 1

        await ctx.send(embed=embed_msg("🎲 Random effectué", f"{moved} membres déplacés aléatoirement."))

    # ============================================================
    # 5) MOOVE TOUTE LA VOCAL → 1 SALON
    # ============================================================
    @commands.command(name="mooveall")
    @has_role()
    async def mooveall(self, ctx, channel: nextcord.VoiceChannel = None):
        if not ctx.author.voice:
            return await ctx.send(embed=embed_msg("❌ Impossible", "Tu dois être en vocal.", 0xff0000))

        if not channel:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+mooveall #salon`", 0xff0000))

        moved = 0
        for m in ctx.author.voice.channel.members:
            old = m.voice.channel
            await m.move_to(channel)
            last_moves[m.id] = old.id
            moved += 1

        await ctx.send(embed=embed_msg("🚚 Déplacement effectué", f"{moved} membres → {format_channel(channel)}"))

    # ============================================================
    # 6) MOOVE TOUTE LA VOCAL → RANDOM CATÉGORIE (AMÉLIORÉ)
    # ============================================================
    @commands.command(name="mooveallrandom")
    @has_role()
    async def mooveallrandom(self, ctx, category_id: int = None):
        if not ctx.author.voice:
            return await ctx.send(embed=embed_msg("❌ Impossible", "Tu dois être en vocal.", 0xff0000))

        if not category_id:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+mooveallrandom <ID_CAT>`", 0xff0000))

        cat = ctx.guild.get_channel(category_id)
        vcs = [c for c in cat.channels if isinstance(c, nextcord.VoiceChannel)]

        members = list(ctx.author.voice.channel.members)
        moved = 0

        for m in members:
            target = random.choice(vcs)
            old = m.voice.channel
            await m.move_to(target)
            last_moves[m.id] = old.id
            moved += 1

        await ctx.send(embed=embed_msg("🎲 Random effectué", f"{moved} membres déplacés aléatoirement."))

    # ============================================================
    # 7) MOOVE TOUT LE SERVEUR → 1 SALON
    # ============================================================
    @commands.command(name="mooveserver")
    @has_role()
    async def mooveserver(self, ctx, channel: nextcord.VoiceChannel = None):
        if not channel:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+mooveserver #salon`", 0xff0000))

        moved = 0
        for m in ctx.guild.members:
            if m.voice and m.voice.channel:
                old = m.voice.channel
                await m.move_to(channel)
                last_moves[m.id] = old.id
                moved += 1

        await ctx.send(embed=embed_msg("🌐 Moove serveur", f"{moved} membres déplacés → {format_channel(channel)}"))

    # ============================================================
    # 8) BACK
    # ============================================================
    @commands.command(name="back")
    @has_role()
    async def back(self, ctx):
        if not last_moves:
            return await ctx.send(embed=embed_msg("❌ Aucun déplacement", "Aucun membre à renvoyer.", 0xff0000))

        count = 0
        for mid, old_id in list(last_moves.items()):
            member = ctx.guild.get_member(mid)
            old_ch = ctx.guild.get_channel(old_id)
            if member and member.voice:
                await member.move_to(old_ch)
                count += 1

        last_moves.clear()
        await ctx.send(embed=embed_msg("🔙 Retour effectué", f"{count} membres renvoyés."))

    # ============================================================
    # 9) SHUFFLE / STOP
    # ============================================================
    @commands.command(name="shuffle")
    @has_role()
    async def shuffle(self, ctx, mode=None, member: nextcord.Member = None, category_id: int = None):
        if mode != "start":
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+shuffle start @user <ID_CAT>`", 0xff0000))

        if not member or not category_id:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+shuffle start @user <ID_CAT>`", 0xff0000))

        if member.id in shuffle_tasks:
            return await ctx.send(embed=embed_msg("⚠️ Déjà actif", "Ce membre est déjà en shuffle.", 0xffa500))

        cat = ctx.guild.get_channel(category_id)
        vcs = [c for c in cat.channels if isinstance(c, nextcord.VoiceChannel)]

        async def shuffle_loop():
            while True:
                try:
                    target = random.choice(vcs)
                    await member.move_to(target)
                    await asyncio.sleep(0.1)
                except:
                    break

        task = asyncio.create_task(shuffle_loop())
        shuffle_tasks[member.id] = task

        await ctx.send(embed=embed_msg("🔄 Shuffle lancé", f"{member.mention} est maintenant en shuffle."))

    @commands.command(name="shufflestop")
    @has_role()
    async def shufflestop(self, ctx):
        if not shuffle_tasks:
            return await ctx.send(embed=embed_msg("❌ Aucun shuffle", "Aucun shuffle n'est actif.", 0xff0000))

        for mid, task in list(shuffle_tasks.items()):
            task.cancel()
            del shuffle_tasks[mid]

        await ctx.send(embed=embed_msg("🛑 Shuffle arrêté", "Tous les shuffles ont été stoppés."))


def setup(bot):
    bot.add_cog(Voice(bot))
