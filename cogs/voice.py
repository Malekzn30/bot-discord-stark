import nextcord
from nextcord.ext import commands
import asyncio
import random
from config import AUTHORIZED_ROLE_ID

# Limiter cache EXTRÊMEMENT pour Render gratuit
MAX_CACHE_SIZE = 50  # Très petit
last_moves = {}  # {member_id: channel_id}
shuffle_tasks = {}

def cleanup_memory():
    """Nettoyage agressif."""
    global last_moves
    if len(last_moves) > MAX_CACHE_SIZE:
        # Garder seulement 25
        items = list(last_moves.items())[-25:]
        last_moves = dict(items)

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
    # 4) MOOVE PLUSIEURS PERSONNES → RANDOM CATÉGORIE
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
    # 6) MOOVE TOUTE LA VOCAL → RANDOM CATÉGORIE
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
        # Vérification de la commande
        if mode != "start":
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+shuffle start @user <ID_CAT>`", 0xff0000))

        if not member or not category_id:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+shuffle start @user <ID_CAT>`", 0xff0000))

        # Déjà en shuffle ?
        if member.id in shuffle_tasks:
            return await ctx.send(embed=embed_msg("⚠️ Déjà actif", "Ce membre est déjà en shuffle.", 0xffa500))

        # Récupération des salons
        cat = ctx.guild.get_channel(category_id)
        vcs = [c for c in cat.channels if isinstance(c, nextcord.VoiceChannel)]

        # Boucle du shuffle
        async def shuffle_loop():
            try:
                while True:
                    target = random.choice(vcs)
                    await member.move_to(target)
                    await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                return
            except:
                return

        # Lancement du shuffle
        task = asyncio.create_task(shuffle_loop())
        shuffle_tasks[member.id] = task

        await ctx.send(embed=embed_msg("🔄 Shuffle lancé", f"{member.mention} est maintenant en shuffle."))

    @commands.command(name="shufflestop")
    @has_role()
    async def shufflestop(self, ctx):
        # Aucun shuffle actif ?
        if not shuffle_tasks:
            return await ctx.send(embed=embed_msg("❌ Aucun shuffle", "Aucun shuffle n'est actif.", 0xff0000))

        # Annulation propre
        for mid, task in list(shuffle_tasks.items()):
            task.cancel()
            del shuffle_tasks[mid]

        await ctx.send(embed=embed_msg("🛑 Shuffle arrêté", "Tous les shuffles ont été stoppés."))

    # ============================================================
    # ROTATE USERS (faire tourner plusieurs personnes dans les salons)
    # ============================================================
    @commands.command(name="rotateusers")
    @has_role()
    async def rotateusers(self, ctx, *args):
        if len(args) < 2:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+rotateusers @u1 @u2 ... <ID_CAT>`", 0xff0000))

        try:
            cat_id = int(args[-1])
        except:
            return await ctx.send(embed=embed_msg("❌ Erreur", "Le dernier argument doit être un ID de catégorie.", 0xff0000))

        mentions = ctx.message.mentions
        if not mentions:
            return await ctx.send(embed=embed_msg("❌ Aucun membre", "Mentionne au moins 1 membre.", 0xff0000))

        cat = ctx.guild.get_channel(cat_id)
        vcs = [c for c in cat.channels if isinstance(c, nextcord.VoiceChannel)]

        if len(vcs) < 2:
            return await ctx.send(embed=embed_msg("❌ Impossible", "Il faut au moins 2 salons vocaux.", 0xff0000))

        for i, m in enumerate(mentions):
            if m.voice:
                target = vcs[i % len(vcs)]
                old = m.voice.channel
                await m.move_to(target)
                last_moves[m.id] = old.id

        await ctx.send(embed=embed_msg("🔄 Rotation effectuée", f"{len(mentions)} membres ont tourné dans les salons."))

    # ============================================================
    # ROTATE ALL (toute la vocal tourne dans les salons)
    # ============================================================
    @commands.command(name="rotateall")
    @has_role()
    async def rotateall(self, ctx, category_id: int = None):
        if not ctx.author.voice:
            return await ctx.send(embed=embed_msg("❌ Impossible", "Tu dois être en vocal.", 0xff0000))

        if not category_id:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+rotateall <ID_CAT>`", 0xff0000))

        cat = ctx.guild.get_channel(category_id)
        vcs = [c for c in cat.channels if isinstance(c, nextcord.VoiceChannel)]
        members = list(ctx.author.voice.channel.members)

        if len(vcs) < 2:
            return await ctx.send(embed=embed_msg("❌ Impossible", "Il faut au moins 2 salons vocaux.", 0xff0000))

        for i, m in enumerate(members):
            target = vcs[i % len(vcs)]
            old = m.voice.channel
            await m.move_to(target)
            last_moves[m.id] = old.id

        await ctx.send(embed=embed_msg("🔄 Rotation effectuée", f"{len(members)} membres ont tourné dans les salons."))

    # ============================================================
    # ROTATE RANDOM (rotation aléatoire)
    # ============================================================
    @commands.command(name="rotaterandom")
    @has_role()
    async def rotaterandom(self, ctx, category_id: int = None):
        if not ctx.author.voice:
            return await ctx.send(embed=embed_msg("❌ Impossible", "Tu dois être en vocal.", 0xff0000))

        if not category_id:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+rotaterandom <ID_CAT>`", 0xff0000))

        cat = ctx.guild.get_channel(category_id)
        vcs = [c for c in cat.channels if isinstance(c, nextcord.VoiceChannel)]
        members = list(ctx.author.voice.channel.members)

        random.shuffle(members)

        for m in members:
            target = random.choice(vcs)
            old = m.voice.channel
            await m.move_to(target)
            last_moves[m.id] = old.id

        await ctx.send(embed=embed_msg("🎲 Rotation aléatoire", f"{len(members)} membres déplacés aléatoirement."))

    # ============================================================
    # ROTATE GROUPS (faire tourner des groupes entiers)
    # ============================================================
    @commands.command(name="rotategroups")
    @has_role()
    async def rotategroups(self, ctx, category_id: int = None):
        if not ctx.author.voice:
            return await ctx.send(embed=embed_msg("❌ Impossible", "Tu dois être en vocal.", 0xff0000))

        if not category_id:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+rotategroups <ID_CAT>`", 0xff0000))

        cat = ctx.guild.get_channel(category_id)
        vcs = [c for c in cat.channels if isinstance(c, nextcord.VoiceChannel)]

        if len(vcs) < 2:
            return await ctx.send(embed=embed_msg("❌ Impossible", "Il faut au moins 2 salons vocaux.", 0xff0000))

        groups = {vc.id: list(vc.members) for vc in vcs}

        vc_ids = list(groups.keys())
        rotated = vc_ids[1:] + vc_ids[:1]

        for old_id, new_id in zip(vc_ids, rotated):
            for m in groups[old_id]:
                old = m.voice.channel
                await m.move_to(ctx.guild.get_channel(new_id))
                last_moves[m.id] = old.id

        await ctx.send(embed=embed_msg("🔁 Rotation des groupes", "Tous les salons ont tourné entre eux."))

    # ============================================================
    # RANDOM PAIR (créer des duos aléatoires)
    # ============================================================
    @commands.command(name="randompair")
    @has_role()
    async def randompair(self, ctx):
        if not ctx.author.voice:
            return await ctx.send(embed=embed_msg("❌ Impossible", "Tu dois être en vocal.", 0xff0000))

        members = list(ctx.author.voice.channel.members)
        random.shuffle(members)

        pairs = []
        for i in range(0, len(members), 2):
            if i + 1 < len(members):
                pairs.append((members[i], members[i+1]))
            else:
                pairs.append((members[i], None))

        desc = ""
        for a, b in pairs:
            if b:
                desc += f"👥 {a.mention} + {b.mention}\n"
            else:
                desc += f"👤 {a.mention} (solo)\n"

        await ctx.send(embed=embed_msg("🎲 Duos aléatoires", desc))

    # ============================================================
    # RANDOM TEAMS (créer X équipes aléatoires)
    # ============================================================
    @commands.command(name="randomteams")
    @has_role()
    async def randomteams(self, ctx, team_count: int = None):
        if not ctx.author.voice:
            return await ctx.send(embed=embed_msg("❌ Impossible", "Tu dois être en vocal.", 0xff0000))

        if not team_count or team_count < 2:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+randomteams <NOMBRE>`", 0xff0000))

        members = list(ctx.author.voice.channel.members)
        random.shuffle(members)

        teams = [[] for _ in range(team_count)]
        for i, m in enumerate(members):
            teams[i % team_count].append(m)

        desc = ""
        for i, t in enumerate(teams, 1):
            desc += f"**Équipe {i}** ({len(t)} membres):\n"
            for m in t:
                desc += f"• {m.mention}\n"
            desc += "\n"

        await ctx.send(embed=embed_msg("🎲 Équipes aléatoires", desc))

    # ============================================================
    # RANDOM SPLIT (séparer en 2 groupes)
    # ============================================================
    @commands.command(name="randomsplit")
    @has_role()
    async def randomsplit(self, ctx):
        if not ctx.author.voice:
            return await ctx.send(embed=embed_msg("❌ Impossible", "Tu dois être en vocal.", 0xff0000))

        members = list(ctx.author.voice.channel.members)
        random.shuffle(members)

        mid = len(members) // 2
        g1 = members[:mid]
        g2 = members[mid:]

        desc = "**Groupe 1 :**\n"
        for m in g1:
            desc += f"• {m.mention}\n"

        desc += "\n**Groupe 2 :**\n"
        for m in g2:
            desc += f"• {m.mention}\n"

        await ctx.send(embed=embed_msg("🎲 Split aléatoire", desc))

    # ============================================================
    # RANDOM ASSIGN (assigner chaque membre à un salon aléatoire)
    # ============================================================
    @commands.command(name="randomassign")
    @has_role()
    async def randomassign(self, ctx, category_id: int = None):
        if not ctx.author.voice:
            return await ctx.send(embed=embed_msg("❌ Impossible", "Tu dois être en vocal.", 0xff0000))

        if not category_id:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+randomassign <ID_CAT>`", 0xff0000))

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

        await ctx.send(embed=embed_msg("🎲 Assignation aléatoire", f"{moved} membres assignés aléatoirement."))
     # ============================================================
    # CLEARVOICE (vider un salon vocal)
    # ============================================================
    @commands.command(name="clearvoice")
    @has_role()
    async def clearvoice(self, ctx, channel: nextcord.VoiceChannel = None):
        if not channel:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+clearvoice #salon`", 0xff0000))

        moved = 0
        for m in channel.members:
            try:
                await m.move_to(None)
                moved += 1
            except:
                pass

        await ctx.send(embed=embed_msg("🧹 Salon vidé", f"{moved} membres expulsés du vocal."))

    # ============================================================
    # CLEARCATEGORY (vider une catégorie vocale)
    # ============================================================
    @commands.command(name="clearcategory")
    @has_role()
    async def clearcategory(self, ctx, category_id: int = None):
        if not category_id:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+clearcategory <ID_CAT>`", 0xff0000))

        cat = ctx.guild.get_channel(category_id)
        if not isinstance(cat, nextcord.CategoryChannel):
            return await ctx.send(embed=embed_msg("❌ Erreur", "Catégorie invalide.", 0xff0000))

        moved = 0
        for vc in cat.channels:
            if isinstance(vc, nextcord.VoiceChannel):
                for m in vc.members:
                    try:
                        await m.move_to(None)
                        moved += 1
                    except:
                        pass

        await ctx.send(embed=embed_msg("🧹 Catégorie vidée", f"{moved} membres expulsés."))

    # ============================================================
    # LOCKVOICE (verrouiller un salon vocal)
    # ============================================================
    @commands.command(name="lockvoice")
    @has_role()
    async def lockvoice(self, ctx, channel: nextcord.VoiceChannel = None):
        if not channel:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+lockvoice #salon`", 0xff0000))

        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.connect = False
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

        await ctx.send(embed=embed_msg("🔒 Salon verrouillé", f"{format_channel(channel)} est maintenant fermé."))

    # ============================================================
    # UNLOCKVOICE (déverrouiller un salon vocal)
    # ============================================================
    @commands.command(name="unlockvoice")
    @has_role()
    async def unlockvoice(self, ctx, channel: nextcord.VoiceChannel = None):
        if not channel:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+unlockvoice #salon`", 0xff0000))

        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.connect = True
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

        await ctx.send(embed=embed_msg("🔓 Salon déverrouillé", f"{format_channel(channel)} est maintenant ouvert."))

    # ============================================================
    # MUTEALL (mute tout le vocal)
    # ============================================================
    @commands.command(name="muteall")
    @has_role()
    async def muteall(self, ctx):
        if not ctx.author.voice:
            return await ctx.send(embed=embed_msg("❌ Impossible", "Tu dois être en vocal.", 0xff0000))

        count = 0
        for m in ctx.author.voice.channel.members:
            try:
                await m.edit(mute=True)
                count += 1
            except:
                pass

        await ctx.send(embed=embed_msg("🔇 Mute all", f"{count} membres mutés."))

    # ============================================================
    # UNMUTEALL (unmute tout le vocal)
    # ============================================================
    @commands.command(name="unmuteall")
    @has_role()
    async def unmuteall(self, ctx):
        if not ctx.author.voice:
            return await ctx.send(embed=embed_msg("❌ Impossible", "Tu dois être en vocal.", 0xff0000))

        count = 0
        for m in ctx.author.voice.channel.members:
            try:
                await m.edit(mute=False)
                count += 1
            except:
                pass

        await ctx.send(embed=embed_msg("🔊 Unmute all", f"{count} membres démutés."))

    # ============================================================
    # DEAFENALL (deafen tout le vocal)
    # ============================================================
    @commands.command(name="deafenall")
    @has_role()
    async def deafenall(self, ctx):
        if not ctx.author.voice:
            return await ctx.send(embed=embed_msg("❌ Impossible", "Tu dois être en vocal.", 0xff0000))

        count = 0
        for m in ctx.author.voice.channel.members:
            try:
                await m.edit(deafen=True)
                count += 1
            except:
                pass

        await ctx.send(embed=embed_msg("🔇 Deafen all", f"{count} membres deafened."))

    # ============================================================
    # UNDEAFENALL (undeafen tout le vocal)
    # ============================================================
    @commands.command(name="undeafenall")
    @has_role()
    async def undeafenall(self, ctx):
        if not ctx.author.voice:
            return await ctx.send(embed=embed_msg("❌ Impossible", "Tu dois être en vocal.", 0xff0000))

        count = 0
        for m in ctx.author.voice.channel.members:
            try:
                await m.edit(deafen=False)
                count += 1
            except:
                pass

        await ctx.send(embed=embed_msg("🔊 Undeafen all", f"{count} membres réactivés."))

    # ============================================================
    # SPIN (faire tourner un membre dans plusieurs salons)
    # ============================================================
    @commands.command(name="spin")
    @has_role()
    async def spin(self, ctx, member: nextcord.Member = None, category_id: int = None):
        if not member or not category_id:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+spin @user <ID_CAT>`", 0xff0000))

        cat = ctx.guild.get_channel(category_id)
        vcs = [c for c in cat.channels if isinstance(c, nextcord.VoiceChannel)]

        for _ in range(10):
            try:
                await member.move_to(random.choice(vcs))
                await asyncio.sleep(0.2)
            except:
                break

        await ctx.send(embed=embed_msg("🌀 Spin terminé", f"{member.mention} a tourné dans les salons."))

    # ============================================================
    # SPINALL (faire tourner toute la vocal)
    # ============================================================
    @commands.command(name="spinall")
    @has_role()
    async def spinall(self, ctx, category_id: int = None):
        if not ctx.author.voice:
            return await ctx.send(embed=embed_msg("❌ Impossible", "Tu dois être en vocal.", 0xff0000))

        if not category_id:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+spinall <ID_CAT>`", 0xff0000))

        cat = ctx.guild.get_channel(category_id)
        vcs = [c for c in cat.channels if isinstance(c, nextcord.VoiceChannel)]
        members = list(ctx.author.voice.channel.members)

        for _ in range(10):
            for m in members:
                try:
                    await m.move_to(random.choice(vcs))
                except:
                    pass
            await asyncio.sleep(0.2)

        await ctx.send(embed=embed_msg("🌀 Spin all terminé", f"{len(members)} membres ont tourné."))

    # ============================================================
    # RANDOMTP (téléporter un membre aléatoirement plusieurs fois)
    # ============================================================
    @commands.command(name="randomtp")
    @has_role()
    async def randomtp(self, ctx, member: nextcord.Member = None, category_id: int = None, count: int = 10):
        if not member or not category_id:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+randomtp @user <ID_CAT> [count]`", 0xff0000))

        cat = ctx.guild.get_channel(category_id)
        vcs = [c for c in cat.channels if isinstance(c, nextcord.VoiceChannel)]

        for _ in range(count):
            try:
                await member.move_to(random.choice(vcs))
                await asyncio.sleep(0.3)
            except:
                break

        await ctx.send(embed=embed_msg("🎲 Random TP terminé", f"{member.mention} a été téléporté {count} fois."))

    # ============================================================
    # RUSSIAN ROULETTE (1 membre sur 6 déplacé aléatoirement)
    # ============================================================
    @commands.command(name="russianroulette")
    @has_role()
    async def russianroulette(self, ctx, category_id: int = None):
        if not ctx.author.voice:
            return await ctx.send(embed=embed_msg("❌ Impossible", "Tu dois être en vocal.", 0xff0000))

        if not category_id:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+russianroulette <ID_CAT>`", 0xff0000))

        members = list(ctx.author.voice.channel.members)
        cat = ctx.guild.get_channel(category_id)
        vcs = [c for c in cat.channels if isinstance(c, nextcord.VoiceChannel)]

        chosen = random.choice(members)
        target = random.choice(vcs)

        old = chosen.voice.channel
        await chosen.move_to(target)
        last_moves[chosen.id] = old.id

        await ctx.send(embed=embed_msg("🔫 Roulette russe", f"{chosen.mention} a perdu..."))

    # ============================================================
    # RANDOMKICKVOICE (kick vocal aléatoire)
    # ============================================================
    @commands.command(name="randomkickvoice")
    @has_role()
    async def randomkickvoice(self, ctx):
        if not ctx.author.voice:
            return await ctx.send(embed=embed_msg("❌ Impossible", "Tu dois être en vocal.", 0xff0000))

        members = list(ctx.author.voice.channel.members)
        chosen = random.choice(members)

        try:
            await chosen.move_to(None)
        except:
            pass

        await ctx.send(embed=embed_msg("👢 Kick vocal aléatoire", f"{chosen.mention} a été expulsé du vocal."))
    # ============================================================
    # AUTOBALANCE (équilibrer automatiquement les salons)
    # ============================================================
    @commands.command(name="autobalance")
    @has_role()
    async def autobalance(self, ctx, category_id: int = None):
        if not category_id:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+autobalance <ID_CAT>`", 0xff0000))

        cat = ctx.guild.get_channel(category_id)
        vcs = [vc for vc in cat.channels if isinstance(vc, nextcord.VoiceChannel)]

        members = []
        for vc in vcs:
            members.extend(vc.members)

        random.shuffle(members)

        for i, m in enumerate(members):
            target = vcs[i % len(vcs)]
            old = m.voice.channel
            await m.move_to(target)
            last_moves[m.id] = old.id

        await ctx.send(embed=embed_msg("⚖️ Auto-balance", "Les membres ont été répartis équitablement."))

    # ============================================================
    # AUTOREGROUP (regrouper tout le monde dans un seul salon)
    # ============================================================
    @commands.command(name="autoregroup")
    @has_role()
    async def autoregroup(self, ctx, channel: nextcord.VoiceChannel = None):
        if not channel:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+autoregroup #salon`", 0xff0000))

        moved = 0
        for m in ctx.guild.members:
            if m.voice:
                old = m.voice.channel
                await m.move_to(channel)
                last_moves[m.id] = old.id
                moved += 1

        await ctx.send(embed=embed_msg("📥 Regroupement", f"{moved} membres regroupés dans {format_channel(channel)}"))

    # ============================================================
    # AUTOSPLIT (séparer automatiquement en X salons)
    # ============================================================
    @commands.command(name="autosplit")
    @has_role()
    async def autosplit(self, ctx, category_id: int = None, groups: int = None):
        if not category_id or not groups:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+autosplit <ID_CAT> <GROUPES>`", 0xff0000))

        cat = ctx.guild.get_channel(category_id)
        vcs = [vc for vc in cat.channels if isinstance(vc, nextcord.VoiceChannel)]

        if groups > len(vcs):
            return await ctx.send(embed=embed_msg("❌ Erreur", "Pas assez de salons vocaux.", 0xff0000))

        members = []
        for vc in vcs:
            members.extend(vc.members)

        random.shuffle(members)

        for i, m in enumerate(members):
            target = vcs[i % groups]
            old = m.voice.channel
            await m.move_to(target)
            last_moves[m.id] = old.id

        await ctx.send(embed=embed_msg("🪓 Auto-split", f"{len(members)} membres répartis en {groups} groupes."))

    # ============================================================
    # AUTOSORT (trier les membres par rôle dans les salons)
    # ============================================================
    @commands.command(name="autosort")
    @has_role()
    async def autosort(self, ctx, category_id: int = None):
        if not category_id:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+autosort <ID_CAT>`", 0xff0000))

        cat = ctx.guild.get_channel(category_id)
        vcs = [vc for vc in cat.channels if isinstance(vc, nextcord.VoiceChannel)]

        members = []
        for vc in vcs:
            members.extend(vc.members)

        members.sort(key=lambda m: len(m.roles), reverse=True)

        for i, m in enumerate(members):
            target = vcs[i % len(vcs)]
            old = m.voice.channel
            await m.move_to(target)
            last_moves[m.id] = old.id

        await ctx.send(embed=embed_msg("📚 Tri par rôle", "Les membres ont été triés selon leur hiérarchie."))

    # ============================================================
    # NUKEVOICE (vider un salon vocal)
    # ============================================================
    @commands.command(name="nukevoice")
    @has_role()
    async def nukevoice(self, ctx, channel: nextcord.VoiceChannel = None):
        if not channel:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+nukevoice #salon`", 0xff0000))

        moved = 0
        for m in channel.members:
            try:
                await m.move_to(None)
                moved += 1
            except:
                pass

        await ctx.send(embed=embed_msg("💣 Nuke vocal", f"{moved} membres expulsés du salon."))

    # ============================================================
    # NUKECATEGORY (vider une catégorie vocale)
    # ============================================================
    @commands.command(name="nukecategory")
    @has_role()
    async def nukecategory(self, ctx, category_id: int = None):
        if not category_id:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+nukecategory <ID_CAT>`", 0xff0000))

        cat = ctx.guild.get_channel(category_id)

        moved = 0
        for vc in cat.channels:
            if isinstance(vc, nextcord.VoiceChannel):
                for m in vc.members:
                    try:
                        await m.move_to(None)
                        moved += 1
                    except:
                        pass

        await ctx.send(embed=embed_msg("💣 Nuke catégorie", f"{moved} membres expulsés."))

    # ============================================================
    # NUKERANDOM (déplacer tout le monde dans des salons random)
    # ============================================================
    @commands.command(name="nukerandom")
    @has_role()
    async def nukerandom(self, ctx, category_id: int = None):
        if not category_id:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+nukerandom <ID_CAT>`", 0xff0000))

        cat = ctx.guild.get_channel(category_id)
        vcs = [vc for vc in cat.channels if isinstance(vc, nextcord.VoiceChannel)]

        members = []
        for vc in vcs:
            members.extend(vc.members)

        moved = 0
        for m in members:
            target = random.choice(vcs)
            old = m.voice.channel
            await m.move_to(target)
            last_moves[m.id] = old.id
            moved += 1

        await ctx.send(embed=embed_msg("💥 Nuke random", f"{moved} membres déplacés aléatoirement."))

    # ============================================================
    # NUKESHUFFLE (shuffle massif)
    # ============================================================
    @commands.command(name="nukeshuffle")
    @has_role()
    async def nukeshuffle(self, ctx, category_id: int = None, cycles: int = 10):
        if not category_id:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+nukeshuffle <ID_CAT> [cycles]`", 0xff0000))

        cat = ctx.guild.get_channel(category_id)
        vcs = [vc for vc in cat.channels if isinstance(vc, nextcord.VoiceChannel)]

        members = []
        for vc in vcs:
            members.extend(vc.members)

        for _ in range(cycles):
            for m in members:
                try:
                    await m.move_to(random.choice(vcs))
                except:
                    pass
            await asyncio.sleep(0.2)

        await ctx.send(embed=embed_msg("💥 Shuffle massif", f"{len(members)} membres mélangés {cycles} fois."))

    # ============================================================
    # VOICESTATS (statistiques vocales)
    # ============================================================
    @commands.command(name="voicestats")
    @has_role()
    async def voicestats(self, ctx):
        total = 0
        desc = ""

        for vc in ctx.guild.voice_channels:
            count = len(vc.members)
            total += count
            desc += f"{format_channel(vc)} : **{count}** membres\n"

        desc += f"\n👥 Total en vocal : **{total}**"

        await ctx.send(embed=embed_msg("📊 Statistiques vocales", desc))

    # ============================================================
    # MOVELOG (historique des déplacements)
    # ============================================================
    @commands.command(name="movelog")
    @has_role()
    async def movelog(self, ctx):
        if not last_moves:
            return await ctx.send(embed=embed_msg("📜 Log vide", "Aucun déplacement enregistré."))

        desc = ""
        for mid, old_id in last_moves.items():
            member = ctx.guild.get_member(mid)
            old_ch = ctx.guild.get_channel(old_id)
            if member and old_ch:
                desc += f"• {member.mention} ← {old_ch.name}\n"

        await ctx.send(embed=embed_msg("📜 Historique des déplacements", desc))

    # ============================================================
    # WHOISVOICE (voir où est un membre)
    # ============================================================
    @commands.command(name="whoisvoice")
    @has_role()
    async def whoisvoice(self, ctx, member: nextcord.Member = None):
        if not member:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+whoisvoice @user`", 0xff0000))

        if not member.voice:
            return await ctx.send(embed=embed_msg("🔍 Info", f"{member.mention} n'est dans aucun vocal."))

        await ctx.send(embed=embed_msg("🔍 Info vocal", f"{member.mention} est dans {format_channel(member.voice.channel)}"))

    # ============================================================
    # LISTVOICE (liste des salons vocaux + membres)
    # ============================================================
    @commands.command(name="listvoice")
    @has_role()
    async def listvoice(self, ctx):
        desc = ""

        for vc in ctx.guild.voice_channels:
            desc += f"{format_channel(vc)} ({len(vc.members)} membres)\n"
            for m in vc.members:
                desc += f"• {m.mention}\n"
            desc += "\n"

        await ctx.send(embed=embed_msg("📋 Liste des vocaux", desc))
    # ============================================================
    # JOINME → Le bot rejoint le salon de l'auteur
    # ============================================================
    @commands.command(name="joinme")
    @has_role()
    async def joinme(self, ctx):
        if ctx.author.voice is None:
            return await ctx.send(embed=embed_msg("❌ Erreur", "Tu dois être dans un salon vocal."))

        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(embed=embed_msg("✅ Vocal", f"J'ai rejoint **{channel.name}**."))

    # ============================================================
    # JOIN → Le bot rejoint un salon via son ID
    # ============================================================
    @commands.command(name="join")
    @has_role()
    async def join(self, ctx, channel_id: int = None):
        if channel_id is None:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+join <ID_SALON>`"))

        channel = ctx.guild.get_channel(channel_id)

        if channel is None or not isinstance(channel, nextcord.VoiceChannel):
            return await ctx.send(embed=embed_msg("❌ Erreur", "Salon vocal introuvable."))

        await channel.connect()
        await ctx.send(embed=embed_msg("✅ Vocal", f"J'ai rejoint **{channel.name}**."))

    # ============================================================
    # LEAVE → Le bot quitte le salon vocal
    # ============================================================
    @commands.command(name="leave")
    @has_role()
    async def leave(self, ctx):
        if ctx.voice_client is None:
            return await ctx.send(embed=embed_msg("❌ Erreur", "Je ne suis dans aucun salon vocal."))

        await ctx.voice_client.disconnect()
        await ctx.send(embed=embed_msg("👋 Déconnexion", "J'ai quitté le salon vocal."))

    # ============================================================
    # REBALANCE CATEGORY (rééquilibrer une catégorie)
    # ============================================================
    @commands.command(name="rebalance_category")
    @has_role()
    async def rebalance_category(self, ctx, category_id: int = None):
        if not category_id:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+rebalance_category <ID_CAT>`", 0xff0000))

        cat = ctx.guild.get_channel(category_id)
        if not isinstance(cat, nextcord.CategoryChannel):
            return await ctx.send(embed=embed_msg("❌ Erreur", "Catégorie invalide.", 0xff0000))

        # Récupérer tous les membres et les salons vocaux
        vcs = [c for c in cat.channels if isinstance(c, nextcord.VoiceChannel)]
        if len(vcs) < 2:
            return await ctx.send(embed=embed_msg("❌ Impossible", "Il faut au moins 2 salons vocaux.", 0xff0000))

        members = []
        for vc in vcs:
            members.extend(vc.members)
            if len(members) > 500:  # Limite pour Render
                break

        if not members:
            return await ctx.send(embed=embed_msg("⚠️ Aucun membre", "Aucun membre en vocal."))

        # Redistribuer rapidement
        random.shuffle(members)
        cleanup_memory()  # Nettoyer avant
        moved = 0
        for i, m in enumerate(members):
            target = vcs[i % len(vcs)]
            old = m.voice.channel
            await m.move_to(target)
            last_moves[m.id] = old.id
            moved += 1

        await ctx.send(embed=embed_msg("⚖️ Rééquilibrage effectué", f"{moved} membres répartis équitablement dans {len(vcs)} salons."))

    # ============================================================
    # MOVECAT REBALANCE (déplacer et rééquilibrer)
    # ============================================================
    @commands.command(name="movecat_rebalance")
    @has_role()
    async def movecat_rebalance(self, ctx, source_id: int = None, dest_id: int = None):
        if not source_id or not dest_id:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+movecat_rebalance <ID_CAT_SOURCE> <ID_CAT_DEST>`", 0xff0000))

        src_cat = ctx.guild.get_channel(source_id)
        dst_cat = ctx.guild.get_channel(dest_id)

        if not isinstance(src_cat, nextcord.CategoryChannel) or not isinstance(dst_cat, nextcord.CategoryChannel):
            return await ctx.send(embed=embed_msg("❌ Erreur", "Catégories invalides.", 0xff0000))

        # Récupérer tous les membres de la catégorie source
        members = []
        for vc in src_cat.channels:
            if isinstance(vc, nextcord.VoiceChannel):
                members.extend(vc.members)

        if not members:
            return await ctx.send(embed=embed_msg("⚠️ Aucun membre", "Aucun membre dans la catégorie source."))

        # Salons vocaux de la destination
        dst_vcs = [c for c in dst_cat.channels if isinstance(c, nextcord.VoiceChannel)]
        if not dst_vcs:
            return await ctx.send(embed=embed_msg("❌ Erreur", "Aucun salon vocal dans la catégorie destination.", 0xff0000))

        # Redistribuer dans la destination
        random.shuffle(members)
        moved = 0
        for i, m in enumerate(members):
            target = dst_vcs[i % len(dst_vcs)]
            old = m.voice.channel
            await m.move_to(target)
            last_moves[m.id] = old.id
            moved += 1

        await ctx.send(embed=embed_msg("🚚 Déplacement + rééquilibrage", f"{moved} membres déplacés et répartis dans {len(dst_vcs)} salons."))

    # ============================================================
    # MOVEALL CATEGORY (déplacer toute une catégorie → 1 salon)
    # ============================================================
    @commands.command(name="moveall_category")
    @has_role()
    async def moveall_category(self, ctx, category_id: int = None, target_channel: nextcord.VoiceChannel = None):
        if not category_id or not target_channel:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+moveall_category <ID_CAT> #salon_cible`", 0xff0000))

        cat = ctx.guild.get_channel(category_id)
        if not isinstance(cat, nextcord.CategoryChannel):
            return await ctx.send(embed=embed_msg("❌ Erreur", "Catégorie invalide.", 0xff0000))

        members = []
        for vc in cat.channels:
            if isinstance(vc, nextcord.VoiceChannel):
                members.extend(vc.members)

        if not members:
            return await ctx.send(embed=embed_msg("⚠️ Aucun membre", "Aucun membre dans cette catégorie."))

        moved = 0
        for m in members:
            old = m.voice.channel
            await m.move_to(target_channel)
            last_moves[m.id] = old.id
            moved += 1

        await ctx.send(embed=embed_msg("📥 Catégorie déplacée", f"{moved} membres → {format_channel(target_channel)}"))

    # ============================================================
    # SMART BALANCE (équilibre intelligent par rôle/niveau)
    # ============================================================
    @commands.command(name="smartbalance")
    @has_role()
    async def smartbalance(self, ctx, category_id: int = None):
        if not category_id:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+smartbalance <ID_CAT>`", 0xff0000))

        cat = ctx.guild.get_channel(category_id)
        if not isinstance(cat, nextcord.CategoryChannel):
            return await ctx.send(embed=embed_msg("❌ Erreur", "Catégorie invalide.", 0xff0000))

        vcs = [c for c in cat.channels if isinstance(c, nextcord.VoiceChannel)]
        if len(vcs) < 2:
            return await ctx.send(embed=embed_msg("❌ Impossible", "Il faut au moins 2 salons vocaux.", 0xff0000))

        members = []
        for vc in vcs:
            members.extend(vc.members)

        if not members:
            return await ctx.send(embed=embed_msg("⚠️ Aucun membre", "Aucun membre en vocal."))

        # Trier par nombre de rôles (+ de rôles = + de poids)
        members.sort(key=lambda m: len(m.roles), reverse=True)

        # Répartir en round-robin
        moved = 0
        for i, m in enumerate(members):
            target = vcs[i % len(vcs)]
            old = m.voice.channel
            await m.move_to(target)
            last_moves[m.id] = old.id
            moved += 1

        await ctx.send(embed=embed_msg("🧠 Smart Balance", f"{moved} membres répartis par rôle dans {len(vcs)} salons."))

    # ============================================================
    # MOVESERVER + REBALANCE (tout le serveur)
    # ============================================================
    @commands.command(name="moveserver_rebalance")
    @has_role()
    async def moveserver_rebalance(self, ctx, category_id: int = None):
        if not category_id:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+moveserver_rebalance <ID_CAT>`", 0xff0000))

        cat = ctx.guild.get_channel(category_id)
        if not isinstance(cat, nextcord.CategoryChannel):
            return await ctx.send(embed=embed_msg("❌ Erreur", "Catégorie invalide.", 0xff0000))

        # Récupérer tous les membres en vocal du serveur
        members = []
        for m in ctx.guild.members:
            if m.voice and m.voice.channel:
                members.append(m)

        if not members:
            return await ctx.send(embed=embed_msg("⚠️ Aucun membre", "Aucun membre en vocal."))

        # Salons vocaux de la catégorie
        vcs = [c for c in cat.channels if isinstance(c, nextcord.VoiceChannel)]
        if not vcs:
            return await ctx.send(embed=embed_msg("❌ Erreur", "Aucun salon vocal dans cette catégorie.", 0xff0000))

        random.shuffle(members)
        moved = 0
        for i, m in enumerate(members):
            target = vcs[i % len(vcs)]
            old = m.voice.channel
            await m.move_to(target)
            last_moves[m.id] = old.id
            moved += 1

        await ctx.send(embed=embed_msg("🌐 Serveur rééquilibré", f"{moved} membres du serveur répartis dans {len(vcs)} salons."))

    @commands.command(name="rebalanceserver")
    @has_role()
    async def rebalanceserver(self, ctx):
        """Rééquilibre automatiquement tout le serveur dans TOUTES les catégories vocales."""
        
        # Récupérer toutes les catégories vocales
        categories = [c for c in ctx.guild.categories if any(isinstance(ch, nextcord.VoiceChannel) for ch in c.channels)]
        if not categories:
            return await ctx.send(embed=embed_msg("❌ Erreur", "Aucune catégorie vocale trouvée.", 0xff0000))

        # Récupérer tous les membres en vocal
        all_members = []
        for m in ctx.guild.members:
            if m.voice and m.voice.channel:
                all_members.append(m)

        if not all_members:
            return await ctx.send(embed=embed_msg("⚠️ Aucun membre", "Aucun membre en vocal."))

        # Mélanger et répartir entre toutes les catégories
        random.shuffle(all_members)
        
        total_vcs = sum(len([c for c in cat.channels if isinstance(c, nextcord.VoiceChannel)]) for cat in categories)
        all_vcs = []
        for cat in categories:
            all_vcs.extend([c for c in cat.channels if isinstance(c, nextcord.VoiceChannel)])

        if not all_vcs:
            return await ctx.send(embed=embed_msg("❌ Erreur", "Aucun salon vocal trouvé.", 0xff0000))

        moved = 0
        for i, m in enumerate(all_members):
            target = all_vcs[i % len(all_vcs)]
            old = m.voice.channel
            await m.move_to(target)
            last_moves[m.id] = old.id
            moved += 1

        await ctx.send(embed=embed_msg("🌍 Rééquilibrage serveur complet", f"{moved} membres répartis dans {len(all_vcs)} salons vocaux."))

    @commands.command(name="moveserver_single")
    @has_role()
    async def moveserver_single(self, ctx, target_channel: nextcord.VoiceChannel = None):
        if not target_channel:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+moveserver_single #salon`", 0xff0000))

        members = []
        for m in ctx.guild.members:
            if m.voice and m.voice.channel:
                members.append(m)

        if not members:
            return await ctx.send(embed=embed_msg("⚠️ Aucun membre", "Aucun membre en vocal."))

        moved = 0
        for m in members:
            old = m.voice.channel
            await m.move_to(target_channel)
            last_moves[m.id] = old.id
            moved += 1

        await ctx.send(embed=embed_msg("📥 Serveur centralisé", f"{moved} membres → {format_channel(target_channel)}"))

    @commands.command(name="voicekick")
    @has_role()
    async def voicekick(self, ctx, member: nextcord.Member = None):
        if not member:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+voicekick @user`", 0xff0000))
        if not member.voice:
            return await ctx.send(embed=embed_msg("❌ Erreur", f"{member.mention} n'est pas en vocal.", 0xff0000))
        
        try:
            await member.move_to(None)
            await ctx.send(embed=embed_msg("👢 Vocal kick", f"{member.mention} expulsé du vocal."))
        except Exception as e:
            await ctx.send(embed=embed_msg("❌ Erreur", f"Impossible d'expulser : {str(e)}", 0xff0000))

    @commands.command(name="voiceinfo")
    @has_role()
    async def voiceinfo(self, ctx, channel: nextcord.VoiceChannel = None):
        if not channel:
            if not ctx.author.voice:
                return await ctx.send(embed=embed_msg("❌ Erreur", "Tu dois être en vocal ou spécifier un salon.", 0xff0000))
            channel = ctx.author.voice.channel
        
        desc = f"**Salon :** {channel.name}\n"
        desc += f"**Membres :** {len(channel.members)}\n"
        desc += f"**Limite :** {channel.user_limit if channel.user_limit > 0 else 'Illimitée'}\n"
        desc += f"**Bitrate :** {channel.bitrate // 1000}kbps\n"
        desc += f"**Région :** {channel.region or 'Auto'}\n"
        desc += f"\n**Membres :\n"
        for m in channel.members[:10]:
            desc += f"• {m.mention}\n"
        if len(channel.members) > 10:
            desc += f"... et {len(channel.members) - 10} autres"
        
        await ctx.send(embed=embed_msg(f"🔊 Info vocal", desc))

    @commands.command(name="voice_limit")
    @has_role()
    async def voice_limit(self, ctx, channel: nextcord.VoiceChannel, limit: int):
        if limit < 0 or limit > 99:
            return await ctx.send(embed=embed_msg("❌ Erreur", "La limite doit être entre 0 et 99.", 0xff0000))
        
        await channel.edit(user_limit=limit)
        await ctx.send(embed=embed_msg("⚙️ Limite modifiée", f"{channel.mention} → limite: {limit if limit > 0 else 'Illimitée'}"))

    @commands.command(name="voice_bitrate")
    @has_role()
    async def voice_bitrate(self, ctx, channel: nextcord.VoiceChannel, bitrate: int):
        if bitrate < 8 or bitrate > 384:
            return await ctx.send(embed=embed_msg("❌ Erreur", "Bitrate entre 8 et 384 kbps.", 0xff0000))
        
        await channel.edit(bitrate=bitrate * 1000)
        await ctx.send(embed=embed_msg("🎧 Bitrate modifié", f"{channel.mention} → {bitrate}kbps"))

    @commands.command(name="voice_mute_all_server")
    @has_role()
    async def voice_mute_all_server(self, ctx):
        count = 0
        for m in ctx.guild.members:
            if m.voice:
                try:
                    await m.edit(mute=True)
                    count += 1
                except:
                    pass
        await ctx.send(embed=embed_msg("🔇 Mute serveur", f"{count} membres mutés."))

    @commands.command(name="voice_unmute_all_server")
    @has_role()
    async def voice_unmute_all_server(self, ctx):
        count = 0
        for m in ctx.guild.members:
            if m.voice:
                try:
                    await m.edit(mute=False)
                    count += 1
                except:
                    pass
        await ctx.send(embed=embed_msg("🔊 Unmute serveur", f"{count} membres démutés."))

    @commands.command(name="voice_deafen_all_server")
    @has_role()
    async def voice_deafen_all_server(self, ctx):
        count = 0
        for m in ctx.guild.members:
            if m.voice:
                try:
                    await m.edit(deafen=True)
                    count += 1
                except:
                    pass
        await ctx.send(embed=embed_msg("👂 Deafen serveur", f"{count} membres deafened."))

    @commands.command(name="move_category_to_category")
    @has_role()
    async def move_category_to_category(self, ctx, source_cat_id: int, dest_cat_id: int):
        """Déplacer tous les membres d'une catégorie à une autre (sans rééquilibrage)."""
        src = ctx.guild.get_channel(source_cat_id)
        dst = ctx.guild.get_channel(dest_cat_id)
        
        if not isinstance(src, nextcord.CategoryChannel) or not isinstance(dst, nextcord.CategoryChannel):
            return await ctx.send(embed=embed_msg("❌ Erreur", "Catégories invalides.", 0xff0000))
        
        members = []
        for vc in src.channels:
            if isinstance(vc, nextcord.VoiceChannel):
                members.extend(vc.members)
        
        if not members:
            return await ctx.send(embed=embed_msg("⚠️ Aucun membre", "Aucun membre dans la source."))
        
        # Prendre le premier salon de destination
        dst_vcs = [c for c in dst.channels if isinstance(c, nextcord.VoiceChannel)]
        if not dst_vcs:
            return await ctx.send(embed=embed_msg("❌ Erreur", "Aucun salon vocal en destination.", 0xff0000))
        
        moved = 0
        for m in members:
            old = m.voice.channel
            await m.move_to(dst_vcs[0])
            last_moves[m.id] = old.id
            moved += 1
        
        await ctx.send(embed=embed_msg("🚚 Catégorie déplacée", f"{moved} membres déplacés."))

    @commands.command(name="solo_channels")
    @has_role()
    async def solo_channels(self, ctx, category_id: int):
        """Créer des salons 1v1 et y assigner les gens."""
        cat = ctx.guild.get_channel(category_id)
        if not isinstance(cat, nextcord.CategoryChannel):
            return await ctx.send(embed=embed_msg("❌ Erreur", "Catégorie invalide.", 0xff0000))
        
        members = []
        for vc in cat.channels:
            if isinstance(vc, nextcord.VoiceChannel):
                members.extend(vc.members)
        
        if not members:
            return await ctx.send(embed=embed_msg("⚠️ Aucun membre", "Aucun membre à traiter."))
        
        # Créer des 1v1
        for i in range(0, len(members), 2):
            m1 = members[i]
            m2 = members[i+1] if i+1 < len(members) else None
            
            name = f"1v1-{i//2+1}"
            try:
                vc = await ctx.guild.create_voice_channel(name, category=cat, user_limit=2)
                await m1.move_to(vc)
                if m2:
                    await m2.move_to(vc)
            except:
                pass
        
        await ctx.send(embed=embed_msg("👥 1v1 créés", f"Environ {len(members)//2} duos créés."))


def setup(bot):
    bot.add_cog(Voice(bot))
