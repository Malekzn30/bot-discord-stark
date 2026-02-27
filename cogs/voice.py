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

    # ============================
    # MOOVE ALL RANDOM
    # ============================
    @commands.command(name="mooveallrandom")
    @has_role()
    async def mooveallrandom(self, ctx, category_id: int = None):
        if not ctx.author.voice:
            return await ctx.send(embed=embed_msg("❌ Impossible", "Tu dois être en vocal.", 0xff0000))

        if not category_id:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+mooveallrandom <ID_CAT>`", 0xff0000))

        cat = ctx.guild.get_channel(category_id)
        if not isinstance(cat, nextcord.CategoryChannel):
            return await ctx.send(embed=embed_msg("❌ Catégorie invalide", "L’ID fourni n’est pas une catégorie.", 0xff0000))

        vcs = [c for c in cat.channels if isinstance(c, nextcord.VoiceChannel)]
        members = list(ctx.author.voice.channel.members)
        random.shuffle(members)

        for m, ch in zip(members, vcs):
            old = m.voice.channel
            await m.move_to(ch)
            last_moves[m.id] = old.id

        await ctx.send(embed=embed_msg("🎲 Répartition effectuée", "Tous les membres ont été déplacés."))

    # ============================
    # JOINME
    # ============================
    @commands.command(name="joinme")
    @has_role()
    async def joinme(self, ctx):
        if not ctx.author.voice:
            return await ctx.send(embed=embed_msg("❌ Impossible", "Tu dois être en vocal.", 0xff0000))

        channel = ctx.author.voice.channel
        await ctx.send(embed=embed_msg("🎧 Connexion", f"Connexion au salon `{channel.id}`"))
        await channel.connect()

    # ============================
    # MOOVE USERS
    # ============================
    @commands.command(name="mooveusers")
    @has_role()
    async def mooveusers(self, ctx, *args):
        if len(args) < 2:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+mooveusers @u1 @u2 <ID_CAT>`", 0xff0000))

        try:
            cat_id = int(args[-1])
        except:
            return await ctx.send(embed=embed_msg("❌ Erreur", "Le dernier argument doit être un ID de catégorie.", 0xff0000))

        mentions = ctx.message.mentions
        if not mentions:
            return await ctx.send(embed=embed_msg("❌ Aucun membre", "Mentionne au moins 1 membre.", 0xff0000))

        cat = ctx.guild.get_channel(cat_id)
        vcs = [c for c in cat.channels if isinstance(c, nextcord.VoiceChannel)]
        random.shuffle(mentions)

        for m, ch in zip(mentions, vcs):
            old = m.voice.channel
            await m.move_to(ch)
            last_moves[m.id] = old.id

        await ctx.send(embed=embed_msg("🎲 Répartition effectuée", "Les membres ont été déplacés."))

    # ============================
    # MOOVE ALL
    # ============================
    @commands.command(name="mooveall")
    @has_role()
    async def mooveall(self, ctx, channel: nextcord.VoiceChannel = None):
        if not ctx.author.voice:
            return await ctx.send(embed=embed_msg("❌ Impossible", "Tu dois être en vocal.", 0xff0000))

        if not channel:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+mooveall #salon`", 0xff0000))

        for m in ctx.author.voice.channel.members:
            old = m.voice.channel
            await m.move_to(channel)
            last_moves[m.id] = old.id

        await ctx.send(embed=embed_msg("🚚 Déplacement effectué", f"Tous les membres → {format_channel(channel)}"))

        # ============================
    # MOOVE (avec alias MOVE)
    # ============================
    @commands.command(name="moove", aliases=["move"])
    @has_role()
    async def moove(self, ctx, member: nextcord.Member = None, channel: nextcord.VoiceChannel = None):
        if not member or not channel:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+moove @user #salon`", 0xff0000))

        old = member.voice.channel
        await member.move_to(channel)
        last_moves[member.id] = old.id

        await ctx.send(embed=embed_msg("🚚 Déplacé", f"{member.mention} → {format_channel(channel)}"))


    # ============================
    # MOOVE RANDOM
    # ============================
    @commands.command(name="mooverandom")
    @has_role()
    async def mooverandom(self, ctx, member: nextcord.Member = None, category_id: int = None):
        if not member or not category_id:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+mooverandom @user <ID_CAT>`", 0xff0000))

        cat = ctx.guild.get_channel(category_id)
        vcs = [c for c in cat.channels if isinstance(c, nextcord.VoiceChannel)]

        target = random.choice(vcs)
        old = member.voice.channel
        await member.move_to(target)
        last_moves[member.id] = old.id

        await ctx.send(embed=embed_msg("🎲 Déplacement aléatoire", f"{member.mention} → {format_channel(target)}"))

    # ============================
    # SHUFFLE START
    # ============================
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
                    await asyncio.sleep(0.1)  # 10 moves/sec
                except:
                    break

        task = asyncio.create_task(shuffle_loop())
        shuffle_tasks[member.id] = task

        await ctx.send(embed=embed_msg("🔄 Shuffle lancé", f"{member.mention} est maintenant en shuffle."))

    # ============================
    # SHUFFLE STOP
    # ============================
    @commands.command(name="shufflestop")
    @has_role()
    async def shufflestop(self, ctx):
        if not shuffle_tasks:
            return await ctx.send(embed=embed_msg("❌ Aucun shuffle", "Aucun shuffle n'est actif.", 0xff0000))

        for mid, task in list(shuffle_tasks.items()):
            task.cancel()
            del shuffle_tasks[mid]

        await ctx.send(embed=embed_msg("🛑 Shuffle arrêté", "Tous les shuffles ont été stoppés."))

    # ============================
    # BACK
    # ============================
    @commands.command(name="back")
    @has_role()
    async def back(self, ctx):
        if not last_moves:
            return await ctx.send(embed=embed_msg("❌ Aucun déplacement", "Aucun membre à renvoyer.", 0xff0000))

        for mid, old_id in list(last_moves.items()):
            member = ctx.guild.get_member(mid)
            old_ch = ctx.guild.get_channel(old_id)
            if member and member.voice:
                await member.move_to(old_ch)

        last_moves.clear()
        await ctx.send(embed=embed_msg("🔙 Retour effectué", "Tous les membres ont été renvoyés."))

    # ============================
    # MOOVE SERVER
    # ============================
    @commands.command(name="mooveserver")
    @has_role()
    async def mooveserver(self, ctx, channel: nextcord.VoiceChannel = None):
        if not channel:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+mooveserver #salon`", 0xff0000))

        count = 0
        for m in ctx.guild.members:
            if m.voice and m.voice.channel:
                old = m.voice.channel
                await m.move_to(channel)
                last_moves[m.id] = old.id
                count += 1

        await ctx.send(embed=embed_msg("🌐 Moove serveur", f"{count} membres déplacés → {format_channel(channel)}"))

    # ============================
    # JOIN (ID)
    # ============================
    @commands.command(name="join")
    @has_role()
    async def join(self, ctx, channel_id: int = None):
        if not channel_id:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+join <ID>`", 0xff0000))

        channel = ctx.guild.get_channel(channel_id)
        if not channel or not isinstance(channel, nextcord.VoiceChannel):
            return await ctx.send(embed=embed_msg("❌ Salon invalide", "Aucun salon vocal trouvé.", 0xff0000))

        await ctx.send(embed=embed_msg("🎧 Connexion", f"Connexion au salon `{channel.id}`"))
        await channel.connect()

    # ============================
    # LEAVE
    # ============================
    @commands.command(name="leave")
    @has_role()
    async def leave(self, ctx):
        voice_client = ctx.guild.voice_client

        if not voice_client:
            return await ctx.send(embed=embed_msg("❌ Impossible", "Le bot n'est dans aucun vocal.", 0xff0000))

        cid = voice_client.channel.id
        await ctx.send(embed=embed_msg("👋 Déconnexion", f"Le bot quitte `{cid}`"))

        await voice_client.disconnect(force=True)
        voice_client.cleanup()

def setup(bot):
    bot.add_cog(Voice(bot))

