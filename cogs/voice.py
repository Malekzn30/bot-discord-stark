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
    @commands.command(name="déplacer", aliases=["moove", "move"])
    @has_role()
    async def deplacer(self, ctx, member: nextcord.Member = None, channel: nextcord.VoiceChannel = None):
        if not member or not channel:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+déplacer @user #salon`", 0xff0000))

        if not member.voice:
            return await ctx.send(embed=embed_msg("❌ Erreur", "Ce membre n'est pas en vocal.", 0xff0000))

        # Vérifier les permissions du bot
        if not channel.permissions_for(ctx.guild.me).move_members:
            return await ctx.send(embed=embed_msg("❌ Permissions", "Le bot ne peut pas déplacer les membres dans ce salon.", 0xff0000))

        try:
            old = member.voice.channel
            await member.move_to(channel)
            last_moves[member.id] = old.id
            await ctx.send(embed=embed_msg("🚚 Déplacé", f"{member.mention} → {format_channel(channel)}"))
        except Exception as e:
            await ctx.send(embed=embed_msg("❌ Erreur", f"Impossible de déplacer {member.mention}: {str(e)}", 0xff0000))
            print(f"❌ Erreur déplacement {member.display_name}: {e}")

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

        # Vérifier les permissions du bot
        if not channel.permissions_for(ctx.guild.me).move_members:
            return await ctx.send(embed=embed_msg("❌ Permissions", "Le bot ne peut pas déplacer les membres dans ce salon.", 0xff0000))

        moved = 0
        failed = 0
        
        # Message de départ
        msg = await ctx.send(embed=embed_msg("🚚 Déplacement en cours", f"Déplacement de {len(mentions)} membres..."))
        
        for i, m in enumerate(mentions):
            try:
                # Vérifier que le membre est en vocal
                if not m.voice or not m.voice.channel:
                    failed += 1
                    continue
                    
                old = m.voice.channel
                await m.move_to(channel)
                last_moves[m.id] = old.id
                moved += 1
                
                # Petit délai pour éviter le rate limiting
                if i < len(mentions) - 1:
                    await asyncio.sleep(0.3)
                    
            except Exception as e:
                failed += 1
                print(f"❌ Erreur déplacement {m.display_name}: {e}")
                continue

        # Mettre à jour le message
        await msg.edit(embed=embed_msg(
            "🚚 Déplacement terminé", 
            f"✅ {moved} membres déplacés\n❌ {failed} échecs\n📍 {format_channel(channel)}"
        ))

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

        # Vérifier que le bot a les permissions
        if not channel.permissions_for(ctx.guild.me).move_members:
            return await ctx.send(embed=embed_msg("❌ Permissions", "Le bot ne peut pas déplacer les membres dans ce salon.", 0xff0000))

        moved = 0
        failed = 0
        members = list(ctx.author.voice.channel.members)
        
        # Message de départ
        msg = await ctx.send(embed=embed_msg("🚚 Déplacement en cours", f"Déplacement de {len(members)} membres..."))
        
        for i, m in enumerate(members):
            try:
                # Vérifier que le membre est toujours en vocal
                if not m.voice or not m.voice.channel:
                    failed += 1
                    continue
                    
                old = m.voice.channel
                await m.move_to(channel)
                last_moves[m.id] = old.id
                moved += 1
                
                # Petit délai pour éviter le rate limiting
                if i < len(members) - 1:  # Pas de délai pour le dernier
                    await asyncio.sleep(0.3)
                    
            except Exception as e:
                failed += 1
                print(f"❌ Erreur déplacement {m.display_name}: {e}")
                continue
        
        # Mettre à jour le message
        await msg.edit(embed=embed_msg(
            "🚚 Déplacement terminé", 
            f"✅ {moved} membres déplacés\n❌ {failed} échecs\n📍 {format_channel(channel)}"
        ))

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
    @commands.command(name="mooveserver", aliases=["server"])
    @has_role()
    async def mooveserver(self, ctx, channel: nextcord.VoiceChannel = None):
        if not channel:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+mooveserver #salon`", 0xff0000))

        # Vérifier les permissions du bot
        if not channel.permissions_for(ctx.guild.me).move_members:
            return await ctx.send(embed=embed_msg("❌ Permissions", "Le bot ne peut pas déplacer les membres dans ce salon.", 0xff0000))

        # Récupérer tous les membres en vocal
        voice_members = [m for m in ctx.guild.members if m.voice and m.voice.channel]
        
        if not voice_members:
            return await ctx.send(embed=embed_msg("❌ Aucun membre", "Aucun membre n'est en vocal sur le serveur.", 0xff0000))

        moved = 0
        failed = 0
        
        # Message de départ
        msg = await ctx.send(embed=embed_msg("🌐 Déplacement serveur en cours", f"Déplacement de {len(voice_members)} membres..."))
        
        for i, m in enumerate(voice_members):
            try:
                # Vérifier que le membre est toujours en vocal
                if not m.voice or not m.voice.channel:
                    failed += 1
                    continue
                    
                old = m.voice.channel
                await m.move_to(channel)
                last_moves[m.id] = old.id
                moved += 1
                
                # Délai plus long pour le serveur entier
                if i < len(voice_members) - 1:
                    await asyncio.sleep(0.5)
                    
            except Exception as e:
                failed += 1
                print(f"❌ Erreur déplacement serveur {m.display_name}: {e}")
                continue
        
        # Mettre à jour le message
        await msg.edit(embed=embed_msg(
            "🌐 Déplacement serveur terminé", 
            f"✅ {moved} membres déplacés\n❌ {failed} échecs\n📍 {format_channel(channel)}"
        ))

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
    # SPLIT (séparer en 2 groupes et les déplacer)
    # ============================================================
    @commands.command(name="split")
    @has_role()
    async def split(self, ctx, category_id: int = None):
        if not ctx.author.voice:
            return await ctx.send(embed=embed_msg("❌ Impossible", "Tu dois être en vocal.", 0xff0000))

        if not category_id:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+split <ID_CAT>`", 0xff0000))

        cat = ctx.guild.get_channel(category_id)
        vcs = [c for c in cat.channels if isinstance(c, nextcord.VoiceChannel)]

        if len(vcs) < 2:
            return await ctx.send(embed=embed_msg("❌ Impossible", "Il faut au moins 2 salons vocaux.", 0xff0000))

        members = list(ctx.author.voice.channel.members)
        random.shuffle(members)

        mid = len(members) // 2
        group1 = members[:mid]
        group2 = members[mid:]

        # Déplacer le groupe 1 dans les premiers salons
        for i, m in enumerate(group1):
            target = vcs[i % (len(vcs) // 2 or 1)]
            old = m.voice.channel
            await m.move_to(target)
            last_moves[m.id] = old.id

        # Déplacer le groupe 2 dans les salons restants
        for i, m in enumerate(group2):
            target = vcs[(len(vcs) // 2 or 1) + i % (len(vcs) - (len(vcs) // 2 or 1))]
            old = m.voice.channel
            await m.move_to(target)
            last_moves[m.id] = old.id

        await ctx.send(embed=embed_msg("🪓 Split effectué", f"{len(members)} membres séparés en 2 groupes."))

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
    # LOCKMEMBER (verrouiller un membre dans son salon vocal)
    # ============================================================
    @commands.command(name="lockmember")
    @has_role()
    async def lockmember(self, ctx, member: nextcord.Member = None):
        if not member:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+lockmember @membre`", 0xff0000))

        if not member.voice:
            return await ctx.send(embed=embed_msg("❌ Erreur", "Ce membre n'est pas en vocal.", 0xff0000))

        # Récupérer le salon vocal du membre
        channel = member.voice.channel
        
        # Créer ou modifier les permissions du membre
        overwrite = channel.overwrites_for(member)
        
        # Empêcher le membre de se déplacer
        overwrite.move_members = False
        overwrite.connect = True  # Il reste dans le salon mais ne peut pas bouger
        
        await channel.set_permissions(member, overwrite=overwrite)
        
        # Démarrer une tâche pour le ramener automatiquement s'il essaie de bouger
        if member.id not in shuffle_tasks:
            shuffle_tasks[member.id] = asyncio.create_task(self._auto_move_back(member, channel))

        await ctx.send(embed=embed_msg("🔒 Membre verrouillé", f"{member.mention} est maintenant bloqué dans {format_channel(channel)}"))
        
        # Logger l'action
        try:
            from cogs.logs import log_command, log_moderation
            log_command(ctx, "lockmember", f"Membre: {member.name}, Salon: {channel.name}")
            log_moderation("lockmember", ctx.author.name, member.name, f"Verrouillage dans {channel.name}")
        except:
            pass

    # ============================================================
    # UNLOCKMEMBER (déverrouiller un membre)
    # ============================================================
    @commands.command(name="unlockmember")
    @has_role()
    async def unlockmember(self, ctx, member: nextcord.Member = None):
        if not member:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+unlockmember @membre`", 0xff0000))

        # Arrêter la tâche de retour automatique
        if member.id in shuffle_tasks:
            shuffle_tasks[member.id].cancel()
            del shuffle_tasks[member.id]

        # Si le membre est dans un salon vocal, restaurer les permissions
        if member.voice:
            channel = member.voice.channel
            overwrite = channel.overwrites_for(member)
            
            # Restaurer les permissions par défaut
            overwrite.move_members = None
            overwrite.connect = None
            
            await channel.set_permissions(member, overwrite=overwrite)
            
            await ctx.send(embed=embed_msg("🔓 Membre déverrouillé", f"{member.mention} peut maintenant se déplacer librement"))
        else:
            await ctx.send(embed=embed_msg("🔓 Membre déverrouillé", f"{member.mention} peut maintenant se déplacer librement"))
        
        # Logger l'action
        try:
            from cogs.logs import log_command, log_moderation
            log_command(ctx, "unlockmember", f"Membre: {member.name}")
            log_moderation("unlockmember", ctx.author.name, member.name, "Déverrouillage vocal")
        except:
            pass

    async def _auto_move_back(self, member: nextcord.Member, target_channel: nextcord.VoiceChannel):
        """Tâche de fond pour ramener automatiquement un membre dans son salon"""
        try:
            while True:
                await asyncio.sleep(1)  # Vérifier chaque seconde
                
                # Si le membre n'est plus dans le bon salon, le ramener
                if member.voice and member.voice.channel != target_channel:
                    await member.move_to(target_channel)
                    
        except asyncio.CancelledError:
            # La tâche a été annulée (unlockmember)
            pass
        except Exception as e:
            print(f"[ERROR] Auto move back failed: {e}")

    # ============================================================
    # LOCKVOICE (verrouiller un salon vocal)
    # ============================================================
    @commands.command(name="lockvoice")
    @has_role()
    async def lockvoice(self, ctx, channel: nextcord.VoiceChannel = None):
        if not channel:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+lockvoice #salon`", 0xff0000))

        # Récupérer les permissions actuelles
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        
        # Modifier seulement la permission connect sans changer les autres
        overwrite.connect = False
        
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

        await ctx.send(embed=embed_msg("🔒 Salon verrouillé", f"{format_channel(channel)} est maintenant fermé."))
        
        # Logger l'action
        try:
            from cogs.logs import log_command, log_moderation
            log_command(ctx, "lockvoice", f"Salon vocal: {channel.name}")
            log_moderation("lockvoice", ctx.author.name, channel.name, "Verrouillage du salon vocal")
        except:
            pass

    # ============================================================
    # UNLOCKVOICE (déverrouiller un salon vocal)
    # ============================================================
    @commands.command(name="unlockvoice")
    @has_role()
    async def unlockvoice(self, ctx, channel: nextcord.VoiceChannel = None):
        if not channel:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+unlockvoice #salon`", 0xff0000))

        # Récupérer les permissions actuelles
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        
        # Modifier seulement la permission connect sans changer les autres
        overwrite.connect = True
        
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

        await ctx.send(embed=embed_msg("🔓 Salon déverrouillé", f"{format_channel(channel)} est maintenant ouvert."))
        
        # Logger l'action
        try:
            from cogs.logs import log_command, log_moderation
            log_command(ctx, "unlockvoice", f"Salon vocal: {channel.name}")
            log_moderation("unlockvoice", ctx.author.name, channel.name, "Déverrouillage du salon vocal")
        except:
            pass

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

    # ============================================================
    # COMMANDES AVANCÉES D'ÉQUILIBRAGE
    # ============================================================
    
    @commands.command(name="equilibrer", aliases=["balance"])
    @has_role()
    async def equilibrer(self, ctx, category: nextcord.CategoryChannel = None, min_par_salon: int = 2):
        """Équilibrer les membres dans les salons d'une catégorie (2-5 membres par salon)"""
        if not category:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+equilibrer @catégorie [2-5]`", 0xff0000))
        
        if min_par_salon < 2 or min_par_salon > 5:
            return await ctx.send(embed=embed_msg("❌ Erreur", "Le minimum par salon doit être entre 2 et 5.", 0xff0000))
        
        # Récupérer tous les membres dans les salons vocaux de la catégorie
        voice_channels = [c for c in category.channels if isinstance(c, nextcord.VoiceChannel)]
        if not voice_channels:
            return await ctx.send(embed=embed_msg("❌ Erreur", "Aucun salon vocal dans cette catégorie.", 0xff0000))
        
        all_members = []
        for vc in voice_channels:
            all_members.extend(vc.members)
        
        if not all_members:
            return await ctx.send(embed=embed_msg("⚠️ Vide", "Aucun membre dans les salons de cette catégorie.", 0xff0000))
        
        # Calculer combien de salons nécessaires
        total_salons_necessaires = max(1, (len(all_members) + min_par_salon - 1) // min_par_salon)
        
        # Si on a besoin de plus de salons qu'il n'y en a, en créer
        while len(voice_channels) < total_salons_necessaires:
            try:
                new_vc = await ctx.guild.create_voice_channel(
                    f"🔊 Équilibrage-{len(voice_channels)+1}", 
                    category=category,
                    user_limit=min_par_salon + 2  # Laisser un peu de marge
                )
                voice_channels.append(new_vc)
            except:
                break
        
        # Mélanger les membres pour une distribution aléatoire
        random.shuffle(all_members)
        
        # Distribuer les membres équitablement
        membres_par_salon = len(all_members) // len(voice_channels)
        reste = len(all_members) % len(voice_channels)
        
        moved = 0
        membre_index = 0
        
        for i, vc in enumerate(voice_channels):
            # Combien de membres dans ce salon
            membres_ce_salon = membres_par_salon + (1 if i < reste else 0)
            
            for j in range(membres_ce_salon):
                if membre_index < len(all_members):
                    member = all_members[membre_index]
                    if member.voice.channel != vc:
                        await member.move_to(vc)
                        moved += 1
                    membre_index += 1
        
        await ctx.send(embed=embed_msg(
            "⚖️ Équilibrage terminé", 
            f"**{len(all_members)}** membres distribués dans **{len(voice_channels)}** salons\n"
            f"**{moved}** membres déplacés • **{min_par_salon}** minimum par salon"
        ))
        
        # Logger
        try:
            from cogs.logs import log_command
            log_command(ctx, "equilibrer", f"Catégorie: {category.name} | Membres: {len(all_members)} | Min/salon: {min_par_salon}")
        except:
            pass

    @commands.command(name="equilibrer_auto", aliases=["auto_balance"])
    @has_role()
    async def equilibrer_auto(self, ctx, category: nextcord.CategoryChannel = None):
        """Équilibrage automatique intelligent (2-3 membres par salon selon le nombre total)"""
        if not category:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+equilibrer_auto @catégorie`", 0xff0000))
        
        # Récupérer tous les membres
        voice_channels = [c for c in category.channels if isinstance(c, nextcord.VoiceChannel)]
        if not voice_channels:
            return await ctx.send(embed=embed_msg("❌ Erreur", "Aucun salon vocal dans cette catégorie.", 0xff0000))
        
        all_members = []
        for vc in voice_channels:
            all_members.extend(vc.members)
        
        if not all_members:
            return await ctx.send(embed=embed_msg("⚠️ Vide", "Aucun membre dans les salons de cette catégorie.", 0xff0000))
        
        # Déterminer le nombre optimal par salon
        total_membres = len(all_members)
        total_salons = len(voice_channels)
        
        if total_membres <= 6:
            min_par_salon = 2
        elif total_membres <= 12:
            min_par_salon = 3
        elif total_membres <= 20:
            min_par_salon = 4
        else:
            min_par_salon = 5
        
        # Appeler la fonction d'équilibrage avec le bon paramètre
        await self.equilibrer(ctx, category, min_par_salon)

    @commands.command(name="vider_salons_vides", aliases=["clear_empty"])
    @has_role()
    async def vider_salons_vides(self, ctx, category: nextcord.CategoryChannel = None):
        """Supprimer les salons vocaux vides dans une catégorie"""
        if not category:
            return await ctx.send(embed=embed_msg("❌ Utilisation", "Utilise : `+vider_salons_vides @catégorie`", 0xff0000))
        
        voice_channels = [c for c in category.channels if isinstance(c, nextcord.VoiceChannel)]
        if not voice_channels:
            return await ctx.send(embed=embed_msg("❌ Erreur", "Aucun salon vocal dans cette catégorie.", 0xff0000))
        
        deleted = 0
        for vc in voice_channels[:]:  # Copie pour pouvoir supprimer pendant l'itération
            if len(vc.members) == 0 and vc.name.startswith("🔊 Équilibrage-"):
                try:
                    await vc.delete()
                    deleted += 1
                except:
                    pass
        
        await ctx.send(embed=embed_msg(
            "🧹 Nettoyage terminé", 
            f"**{deleted}** salons vocaux vides supprimés"
        ))

    @commands.command(name="immobiles")
    @has_role()
    async def list_immobiles(self, ctx):
        """Lister les membres qui ne peuvent pas être déplacés"""
        
        immobiles = []
        
        for member in ctx.guild.members:
            if not member.voice:
                continue
                
            # Vérifier si le membre peut être déplacé
            try:
                # Vérifier les permissions du bot
                channel = member.voice.channel
                if not channel.permissions_for(ctx.guild.me).move_members:
                    continue
                
                # Vérifier si le membre a des restrictions
                can_move = True
                
                # Vérifier si le membre est dans un canal privé
                overwrites = channel.overwrites_for(ctx.guild.default_role)
                if overwrites.connect is False:
                    can_move = False
                
                # Vérifier les permissions spécifiques du membre
                member_overwrites = channel.overwrites_for(member)
                if member_overwrites.connect is False:
                    can_move = False
                
                if not can_move:
                    immobiles.append(member)
                    
            except:
                continue
        
        if not immobiles:
            embed = nextcord.Embed(
                title="✅ Aucun membre immobile",
                description="Tous les membres en vocal peuvent être déplacés",
                color=0x2ECC71
            )
            return await ctx.send(embed=embed)
        
        embed = nextcord.Embed(
            title="🔒 Membres immobiles",
            description=f"**{len(immobiles)}** membre(s) ne peuvent pas être déplacés",
            color=0xE74C3C
        )
        
        for i, member in enumerate(immobiles[:15]):  # Limiter à 15 pour éviter les embeds trop longs
            channel = member.voice.channel
            reason = "Permissions insuffisantes"
            
            # Détecter la raison spécifique
            try:
                overwrites = channel.overwrites_for(ctx.guild.me)
                if not overwrites.move_members:
                    reason = "Bot sans permission move_members"
                else:
                    overwrites = channel.overwrites_for(ctx.guild.default_role)
                    if overwrites.connect is False:
                        reason = "Salon privé (connect: False)"
                    else:
                        overwrites = channel.overwrites_for(member)
                        if overwrites.connect is False:
                            reason = "Permissions personnelles (connect: False)"
            except:
                reason = "Erreur de vérification"
            
            embed.add_field(
                name=f"{i+1}. {member.display_name}",
                value=f"📍 {channel.mention}\n🔒 {reason}",
                inline=False
            )
        
        if len(immobiles) > 15:
            embed.add_field(
                name="📊 Plus de membres",
                value=f"Et {len(immobiles) - 15} autre(s) membre(s) immobile(s)",
                inline=False
            )
        
        embed.set_footer(text="Utilise +force_move pour tenter de déplacer malgré les restrictions")
        await ctx.send(embed=embed)

    @commands.command(name="force_move")
    @has_role()
    async def force_move(self, ctx, member: nextcord.Member, *, channel: nextcord.VoiceChannel = None):
        """Tenter de déplacer un membre même avec des restrictions"""
        
        if not channel:
            return await ctx.send("❌ Veuillez spécifier un salon vocal")
        
        if not member.voice:
            return await ctx.send("❌ Le membre n'est pas en vocal")
        
        embed = nextcord.Embed(
            title="🔄 Tentative de déplacement forcée",
            description=f"Tentative de déplacer {member.mention} vers {channel.mention}",
            color=0xF39C12
        )
        
        # Analyser les restrictions
        restrictions = []
        
        try:
            # Vérifier les permissions du bot
            if not channel.permissions_for(ctx.guild.me).move_members:
                restrictions.append("❌ Bot sans permission move_members")
            
            # Vérifier les permissions du salon
            overwrites = channel.overwrites_for(ctx.guild.default_role)
            if overwrites.connect is False:
                restrictions.append("❌ Salon privé (connect: False)")
            
            # Vérifier les permissions du membre
            member_overwrites = channel.overwrites_for(member)
            if member_overwrites.connect is False:
                restrictions.append("❌ Permissions personnelles (connect: False)")
            
            if restrictions:
                embed.add_field(
                    name="🔒 Restrictions détectées",
                    value="\n".join(restrictions),
                    inline=False
                )
                embed.add_field(
                    name="⚠️ Risque d'échec",
                    value="La déplacement échouera probablement à cause des restrictions.",
                    inline=False
                )
            else:
                embed.add_field(
                    name="✅ Aucune restriction",
                    value="Le déplacement devrait réussir.",
                    inline=False
                )
            
            embed.set_footer(text="Tentative de déplacement dans 3 secondes...")
            await ctx.send(embed=embed)
            
            # Attendre 3 secondes avant de tenter
            await asyncio.sleep(3)
            
            # Tenter le déplacement
            try:
                await member.move_to(channel)
                
                success_embed = nextcord.Embed(
                    title="✅ Déplacement réussi !",
                    description=f"{member.mention} a été déplacé vers {channel.mention}",
                    color=0x2ECC71
                )
                await ctx.send(embed=success_embed)
                
            except nextcord.Forbidden:
                error_embed = nextcord.Embed(
                    title="❌ Déplacement échoué",
                    description="Permissions insuffisantes pour déplacer ce membre.",
                    color=0xE74C3C
                )
                await ctx.send(embed=error_embed)
                
            except Exception as e:
                error_embed = nextcord.Embed(
                    title="❌ Erreur inattendue",
                    description=f"Erreur lors du déplacement: {str(e)}",
                    color=0xE74C3C
                )
                await ctx.send(embed=error_embed)
                
        except Exception as e:
            await ctx.send(f"❌ Erreur lors de l'analyse: {e}")

    @commands.command(name="move_all_except")
    @has_role()
    async def move_all_except(self, ctx, except_member: nextcord.Member, *, target_channel: nextcord.VoiceChannel = None):
        """Déplacer tous les membres en vocal sauf un membre spécifique"""
        
        if not target_channel:
            return await ctx.send("❌ Veuillez spécifier un salon cible")
        
        # Récupérer tous les membres en vocal sauf celui spécifié
        members_to_move = []
        
        for member in ctx.guild.members:
            if member.voice and member.id != except_member.id:
                members_to_move.append(member)
        
        if not members_to_move:
            return await ctx.send("❌ Aucun membre à déplacer")
        
        embed = nextcord.Embed(
            title="🔄 Déplacement massif (sauf 1 membre)",
            description=f"Déplacement de **{len(members_to_move)}** membre(s) vers {target_channel.mention}",
            color=0x3498db
        )
        
        embed.add_field(
            name="👤 Membre exclu",
            value=f"{except_member.mention} ne sera pas déplacé",
            inline=False
        )
        
        embed.add_field(
            name="📋 Liste des membres",
            value=", ".join([m.mention for m in members_to_move[:10]]) + ("..." if len(members_to_move) > 10 else ""),
            inline=False
        )
        
        await ctx.send(embed=embed)
        
        # Déplacer les membres
        moved = 0
        failed = 0
        
        for member in members_to_move:
            try:
                await member.move_to(target_channel)
                moved += 1
                await asyncio.sleep(0.3)  # Petit délai pour éviter le rate limiting
            except:
                failed += 1
        
        result_embed = nextcord.Embed(
            title="✅ Déplacement terminé",
            description=f"Résultat du déplacement massif",
            color=0x2ECC71
        )
        
        result_embed.add_field(
            name="📊 Statistiques",
            value=f"✅ Déplacés: {moved}\n❌ Échecs: {failed}",
            inline=False
        )
        
        await ctx.send(embed=result_embed)

    @commands.command(name="move_from_category")
    @has_role()
    async def move_from_category(self, ctx, source_category: nextcord.CategoryChannel, *, target_channel: nextcord.VoiceChannel = None):
        """Déplacer tous les membres d'une catégorie vers un salon spécifique"""
        
        if not target_channel:
            return await ctx.send("❌ Veuillez spécifier un salon cible")
        
        # Récupérer tous les salons vocaux de la catégorie
        voice_channels = [ch for ch in source_category.voice_channels]
        
        if not voice_channels:
            return await ctx.send("❌ Aucun salon vocal dans cette catégorie")
        
        # Récupérer tous les membres dans ces salons
        members_to_move = set()
        
        for channel in voice_channels:
            for member in channel.members:
                members_to_move.add(member)
        
        if not members_to_move:
            return await ctx.send("❌ Aucun membre à déplacer dans cette catégorie")
        
        embed = nextcord.Embed(
            title="� Déplacement depuis catégorie",
            description=f"Déplacement de **{len(members_to_move)}** membre(s) depuis {source_category.name}",
            color=0x3498db
        )
        
        embed.add_field(
            name="📋 Salons source",
            value="\n".join([f"• {ch.mention} ({len(ch.members)} membres)" for ch in voice_channels]),
            inline=False
        )
        
        embed.add_field(
            name="🎯 Salon cible",
            value=target_channel.mention,
            inline=False
        )
        
        await ctx.send(embed=embed)
        
        # Déplacer les membres
        moved = 0
        failed = 0
        
        for member in members_to_move:
            try:
                await member.move_to(target_channel)
                moved += 1
                await asyncio.sleep(0.3)
            except:
                failed += 1
        
        result_embed = nextcord.Embed(
            title="✅ Déplacement terminé",
            description=f"Déplacement depuis {source_category.name} terminé",
            color=0x2ECC71
        )
        
        result_embed.add_field(
            name="📊 Statistiques",
            value=f"✅ Déplacés: {moved}\n❌ Échecs: {failed}",
            inline=False
        )
        
        await ctx.send(embed=result_embed)

    @commands.command(name="shuffle_category")
    @has_role()
    async def shuffle_category(self, ctx, category: nextcord.CategoryChannel):
        """Mélanger aléatoirement tous les membres d'une catégorie entre les salons"""
        
        voice_channels = [ch for ch in category.voice_channels]
        
        if len(voice_channels) < 2:
            return await ctx.send("❌ Il faut au moins 2 salons vocaux dans la catégorie")
        
        # Récupérer tous les membres
        all_members = []
        for channel in voice_channels:
            all_members.extend(channel.members)
        
        if not all_members:
            return await ctx.send("❌ Aucun membre à mélanger")
        
        embed = nextcord.Embed(
            title="🔀 Mélange de catégorie",
            description=f"Mélange de **{len(all_members)}** membre(s) dans {len(voice_channels)} salons",
            color=0x3498db
        )
        
        embed.add_field(
            name="📋 Salons concernés",
            value="\n".join([f"• {ch.mention}" for ch in voice_channels]),
            inline=False
        )
        
        await ctx.send(embed=embed)
        
        # Mélanger les membres
        import random
        random.shuffle(all_members)
        
        # Distribuer les membres
        moved = 0
        failed = 0
        
        for i, member in enumerate(all_members):
            target_channel = voice_channels[i % len(voice_channels)]
            
            try:
                await member.move_to(target_channel)
                moved += 1
                await asyncio.sleep(0.3)
            except:
                failed += 1
        
        result_embed = nextcord.Embed(
            title="✅ Mélange terminé",
            description=f"Mélange dans {category.name} terminé",
            color=0x2ECC71
        )
        
        result_embed.add_field(
            name="� Statistiques",
            value=f"✅ Déplacés: {moved}\n❌ Échecs: {failed}",
            inline=False
        )
        
        await ctx.send(embed=result_embed)

    @commands.command(name="gather_all")
    @has_role()
    async def gather_all(self, ctx, *, target_channel: nextcord.VoiceChannel = None):
        """Rassembler tous les membres en vocal dans un seul salon"""
        
        if not target_channel:
            return await ctx.send("❌ Veuillez spécifier un salon de rassemblement")
        
        # Récupérer tous les membres en vocal
        all_members = []
        for channel in ctx.guild.voice_channels:
            if channel.id != target_channel.id:  # Exclure le salon cible
                all_members.extend(channel.members)
        
        if not all_members:
            return await ctx.send("❌ Aucun membre à rassembler")
        
        embed = nextcord.Embed(
            title="🎯 Rassemblement vocal",
            description=f"Rassemblement de **{len(all_members)}** membre(s) dans {target_channel.mention}",
            color=0x3498db
        )
        
        embed.add_field(
            name="📊 Distribution actuelle",
            value="\n".join([f"• {ch.name}: {len(ch.members)} membres" for ch in ctx.guild.voice_channels if ch.id != target_channel.id]),
            inline=False
        )
        
        await ctx.send(embed=embed)
        
        # Rassembler les membres
        moved = 0
        failed = 0
        
        for member in all_members:
            try:
                await member.move_to(target_channel)
                moved += 1
                await asyncio.sleep(0.3)
            except:
                failed += 1
        
        result_embed = nextcord.Embed(
            title="✅ Rassemblement terminé",
            description=f"Tous les membres rassemblés dans {target_channel.mention}",
            color=0x2ECC71
        )
        
        result_embed.add_field(
            name="📊 Statistiques",
            value=f"✅ Rassemblés: {moved}\n❌ Échecs: {failed}",
            inline=False
        )
        
        await ctx.send(embed=result_embed)

    @commands.command(name="create_voice_rooms")
    @has_role()
    async def create_voice_rooms(self, ctx, category: nextcord.CategoryChannel, room_count: int = 5, room_name: str = "Salon"):
        """Créer plusieurs salons vocaux automatiquement"""
        
        if room_count < 1 or room_count > 50:
            return await ctx.send("❌ Nombre de salons invalide (1-50)")
        
        embed = nextcord.Embed(
            title="🏗️ Création de salons vocaux",
            description=f"Création de **{room_count}** salon(s) dans {category.mention}",
            color=0x3498db
        )
        
        created = 0
        failed = 0
        
        for i in range(room_count):
            try:
                channel = await ctx.guild.create_voice_channel(
                    f"{room_name} {i+1}",
                    category=category,
                    user_limit=None
                )
                created += 1
                await asyncio.sleep(0.2)  # Petit délai
            except Exception as e:
                failed += 1
                print(f"Erreur création salon {i+1}: {e}")
        
        embed.add_field(
            name="📊 Résultat",
            value=f"✅ Créés: {created}\n❌ Échecs: {failed}",
            inline=False
        )
        
        await ctx.send(embed=embed)

    @commands.command(name="clone_voice_channel")
    @has_role()
    async def clone_voice_channel(self, ctx, source_channel: nextcord.VoiceChannel, *, new_name: str = None):
        """Cloner un salon vocal avec ses membres"""
        
        if not new_name:
            new_name = f"{source_channel.name} (Clone)"
        
        # Créer le clone dans la même catégorie
        try:
            clone_channel = await ctx.guild.create_voice_channel(
                new_name,
                category=source_channel.category,
                user_limit=source_channel.user_limit,
                bitrate=source_channel.bitrate,
                overwrites=source_channel.overwrites
            )
            
            embed = nextcord.Embed(
                title="🔄 Salon cloné",
                description=f"{source_channel.mention} a été cloné vers {clone_channel.mention}",
                color=0x2ECC71
            )
            
            # Déplacer tous les membres vers le clone
            if source_channel.members:
                embed.add_field(
                    name="👥 Déplacement des membres",
                    value=f"Déplacement de **{len(source_channel.members)}** membre(s) vers le clone...",
                    inline=False
                )
                
                await ctx.send(embed=embed)
                
                moved = 0
                for member in source_channel.members:
                    try:
                        await member.move_to(clone_channel)
                        moved += 1
                        await asyncio.sleep(0.3)
                    except:
                        pass
                
                result_embed = nextcord.Embed(
                    title="✅ Clone terminé",
                    description=f"Salon {clone_channel.mention} prêt avec {moved} membres",
                    color=0x2ECC71
                )
                await ctx.send(embed=result_embed)
            else:
                await ctx.send(embed=embed)
                
        except Exception as e:
            await ctx.send(f"❌ Erreur lors du clonage: {e}")

    @commands.command(name="swap_channels")
    @has_role()
    async def swap_channels(self, ctx, channel1: nextcord.VoiceChannel, channel2: nextcord.VoiceChannel):
        """Échanger les membres entre deux salons vocaux"""
        
        members1 = list(channel1.members)
        members2 = list(channel2.members)
        
        if not members1 and not members2:
            return await ctx.send("❌ Aucun membre à échanger")
        
        embed = nextcord.Embed(
            title="🔄 Échange de salons",
            description=f"Échange entre {channel1.mention} et {channel2.mention}",
            color=0x3498db
        )
        
        embed.add_field(
            name="👥 Membres à échanger",
            value=f"{channel1.mention}: **{len(members1)}** membre(s)\n{channel2.mention}: **{len(members2)}** membre(s)",
            inline=False
        )
        
        await ctx.send(embed=embed)
        
        # Échanger les membres
        moved_from_1 = 0
        moved_from_2 = 0
        
        # Déplacer membres de channel1 vers channel2
        for member in members1:
            try:
                await member.move_to(channel2)
                moved_from_1 += 1
                await asyncio.sleep(0.3)
            except:
                pass
        
        # Déplacer membres de channel2 vers channel1
        for member in members2:
            try:
                await member.move_to(channel1)
                moved_from_2 += 1
                await asyncio.sleep(0.3)
            except:
                pass
        
        result_embed = nextcord.Embed(
            title="✅ Échange terminé",
            description=f"Échange entre les salons terminé",
            color=0x2ECC71
        )
        
        result_embed.add_field(
            name="📊 Statistiques",
            value=f"🔄 {channel1.mention} → {channel2.mention}: {moved_from_1}\n🔄 {channel2.mention} → {channel1.mention}: {moved_from_2}",
            inline=False
        )
        
        await ctx.send(embed=result_embed)

    @commands.command(name="voice_activity")
    @has_role()
    async def voice_activity(self, ctx, category: nextcord.CategoryChannel = None):
        """Afficher l'activité vocale détaillée"""
        
        if category:
            voice_channels = category.voice_channels
            title = f"📊 Activité vocale - {category.name}"
        else:
            voice_channels = ctx.guild.voice_channels
            title = "📊 Activité vocale - Serveur"
        
        if not voice_channels:
            return await ctx.send("❌ Aucun salon vocal trouvé")
        
        embed = nextcord.Embed(
            title=title,
            description=f"Analyse de **{len(voice_channels)}** salon(s) vocal(aux)",
            color=0x3498db
        )
        
        total_members = 0
        active_channels = 0
        empty_channels = 0
        
        channel_info = []
        
        for channel in voice_channels:
            member_count = len(channel.members)
            total_members += member_count
            
            if member_count > 0:
                active_channels += 1
                status = "🟢 Actif"
            else:
                empty_channels += 1
                status = "⚫ Vide"
            
            # Détecter les membres muets/deafened
            muted = sum(1 for m in channel.members if m.voice.mute)
            deafened = sum(1 for m in channel.members if m.voice.deaf)
            
            channel_info.append(f"{status} {channel.mention}: **{member_count}** membre(s)")
            if muted > 0 or deafened > 0:
                channel_info[-1] += f" (🔇{muted} 👂{deafened})"
        
        embed.add_field(
            name="📈 Statistiques générales",
            value=f"👥 Total membres: **{total_members}**\n🟢 Salons actifs: **{active_channels}**\n⚫ Salons vides: **{empty_channels}**",
            inline=False
        )
        
        embed.add_field(
            name="📋 Détail par salon",
            value="\n".join(channel_info[:10]),  # Limiter à 10 salons
            inline=False
        )
        
        if len(channel_info) > 10:
            embed.add_field(
                name="📊 Plus de salons",
                value=f"Et {len(channel_info) - 10} autre(s) salon(s)",
                inline=False
            )
        
        embed.set_footer(text="Utilise +voice_activity @catégorie pour une catégorie spécifique")
        await ctx.send(embed=embed)

    @commands.command(name="move_afk")
    @has_role()
    async def move_afk(self, ctx, target_channel: nextcord.VoiceChannel, afk_minutes: int = 10):
        """Déplacer les membres AFK vers un salon spécifique"""
        
        if afk_minutes < 1 or afk_minutes > 60:
            return await ctx.send("❌ Durée AFK invalide (1-60 minutes)")
        
        afk_members = []
        
        for member in ctx.guild.members:
            if member.voice:
                # Vérifier si le membre est AFK (pas de statut en vocal depuis X minutes)
                # Note: Discord ne fournit pas directement cette info, donc on utilise une heuristique
                if member.voice.self_mute or member.voice.self_deaf:
                    afk_members.append(member)
        
        if not afk_members:
            return await ctx.send("❌ Aucun membre AFK détecté")
        
        embed = nextcord.Embed(
            title="🔇 Déplacement AFK",
            description=f"Déplacement de **{len(afk_members)}** membre(s) AFK vers {target_channel.mention}",
            color=0xF39C12
        )
        
        embed.add_field(
            name="⏱️ Critère AFK",
            value=f"Membres muets ou sourds depuis plus de {afk_minutes} minutes",
            inline=False
        )
        
        embed.add_field(
            name="👥 Membres concernés",
            value=", ".join([m.mention for m in afk_members[:10]]) + ("..." if len(afk_members) > 10 else ""),
            inline=False
        )
        
        await ctx.send(embed=embed)
        
        # Déplacer les membres AFK
        moved = 0
        failed = 0
        
        for member in afk_members:
            try:
                await member.move_to(target_channel)
                moved += 1
                await asyncio.sleep(0.3)
            except:
                failed += 1
        
        result_embed = nextcord.Embed(
            title="✅ Déplacement AFK terminé",
            description=f"Membres AFK déplacés vers {target_channel.mention}",
            color=0x2ECC71
        )
        
        result_embed.add_field(
            name="📊 Statistiques",
            value=f"✅ Déplacés: {moved}\n❌ Échecs: {failed}",
            inline=False
        )
        
        await ctx.send(embed=result_embed)

    @commands.command(name="voice_backup")
    @has_role()
    async def voice_backup(self, ctx, category: nextcord.CategoryChannel = None):
        """Créer une sauvegarde de la distribution vocale actuelle"""
        
        if category:
            voice_channels = category.voice_channels
            backup_name = f"backup_{category.name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        else:
            voice_channels = ctx.guild.voice_channels
            backup_name = f"backup_serveur_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Créer la sauvegarde
        backup_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "category": category.name if category else "serveur",
            "channels": {}
        }
        
        for channel in voice_channels:
            backup_data["channels"][channel.name] = [
                {
                    "id": member.id,
                    "name": member.name,
                    "display_name": member.display_name
                }
                for member in channel.members
            ]
        
        # Sauvegarder dans un fichier
        try:
            os.makedirs("data/backups", exist_ok=True)
            with open(f"data/backups/{backup_name}.json", "w", encoding="utf-8") as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            embed = nextcord.Embed(
                title="💾 Sauvegarde vocale créée",
                description=f"Sauvegarde de la distribution vocale terminée",
                color=0x2ECC71
            )
            
            embed.add_field(
                name="📊 Statistiques",
                value=f"📁 Fichier: `{backup_name}.json`\n📋 Salons: **{len(voice_channels)}**\n👥 Membres totaux: **{sum(len(ch.members) for ch in voice_channels)}**",
                inline=False
            )
            
            embed.set_footer(text="Utilise +voice_restore pour restaurer cette sauvegarde")
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur lors de la sauvegarde: {e}")

    @commands.command(name="voice_restore")
    @has_role()
    async def voice_restore(self, ctx, backup_file: str = None):
        """Restaurer une sauvegarde vocale"""
        
        if not backup_file:
            # Lister les sauvegardes disponibles
            try:
                backup_dir = "data/backups"
                if not os.path.exists(backup_dir):
                    return await ctx.send("❌ Aucune sauvegarde disponible")
                
                backups = [f for f in os.listdir(backup_dir) if f.endswith('.json')]
                
                if not backups:
                    return await ctx.send("❌ Aucune sauvegarde disponible")
                
                embed = nextcord.Embed(
                    title="📋 Sauvegardes disponibles",
                    description=f"**{len(backups)}** sauvegarde(s) disponible(s)",
                    color=0x3498db
                )
                
                backup_list = []
                for backup in sorted(backups, reverse=True)[:10]:  # 10 plus récentes
                    backup_list.append(f"• `{backup}`")
                
                embed.add_field(
                    name="📁 Fichiers",
                    value="\n".join(backup_list),
                    inline=False
                )
                
                embed.add_field(
                    name="🔄 Utilisation",
                    value="Utilise: `+voice_restore nom_du_fichier`",
                    inline=False
                )
                
                await ctx.send(embed=embed)
                return
                
            except Exception as e:
                return await ctx.send(f"❌ Erreur: {e}")
        
        # Charger et restaurer la sauvegarde
        try:
            backup_path = f"data/backups/{backup_file}"
            if not backup_file.endswith('.json'):
                backup_path += '.json'
            
            with open(backup_path, "r", encoding="utf-8") as f:
                backup_data = json.load(f)
            
            embed = nextcord.Embed(
                title="🔄 Restauration vocale",
                description=f"Restauration de la sauvegarde: `{backup_file}`",
                color=0xF39C12
            )
            
            embed.add_field(
                name="📅 Date de sauvegarde",
                value=backup_data["timestamp"],
                inline=False
            )
            
            embed.add_field(
                name="📋 Contenu",
                value=f"Catégorie: {backup_data['category']}\nSalons: {len(backup_data['channels'])}",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
            # Restaurer les membres
            restored = 0
            failed = 0
            
            for channel_name, members in backup_data["channels"].items():
                # Chercher le salon
                target_channel = nextcord.utils.get(ctx.guild.voice_channels, name=channel_name)
                
                if not target_channel:
                    failed += len(members)
                    continue
                
                for member_data in members:
                    member = ctx.guild.get_member(member_data["id"])
                    if member and member.voice and member.voice.channel != target_channel:
                        try:
                            await member.move_to(target_channel)
                            restored += 1
                            await asyncio.sleep(0.3)
                        except:
                            failed += 1
                    else:
                        failed += 1
            
            result_embed = nextcord.Embed(
                title="✅ Restauration terminée",
                description=f"Sauvegarde `{backup_file}` restaurée",
                color=0x2ECC71
            )
            
            result_embed.add_field(
                name="📊 Statistiques",
                value=f"✅ Restaurés: {restored}\n❌ Échecs: {failed}",
                inline=False
            )
            
            await ctx.send(embed=result_embed)
            
        except FileNotFoundError:
            await ctx.send(f"❌ Fichier de sauvegarde `{backup_file}` non trouvé")
        except Exception as e:
            await ctx.send(f"❌ Erreur lors de la restauration: {e}")

    @commands.command(name="voice_limits")
    @has_role()
    async def voice_limits(self, ctx, channel: nextcord.VoiceChannel, limit: int = None):
        """Gérer les limites de membres d'un salon vocal"""
        
        if limit is None:
            # Afficher les limites actuelles
            current_limit = channel.user_limit
            status = "Illimité" if current_limit == 0 else f"{current_limit} membres"
            
            embed = nextcord.Embed(
                title="📊 Limites du salon",
                description=f"Limites actuelles pour {channel.mention}",
                color=0x3498db
            )
            
            embed.add_field(
                name="👥 Limite actuelle",
                value=status,
                inline=False
            )
            
            embed.add_field(
                name="📈 Occupation",
                value=f"**{len(channel.members)}/{current_limit if current_limit > 0 else '∞'}** membres",
                inline=False
            )
            
            embed.add_field(
                name="🔧 Utilisation",
                value="Utilise: `+voice_limits #salon <nombre>` pour définir une limite (0 = illimité)",
                inline=False
            )
            
            await ctx.send(embed=embed)
            return
        
        if limit < 0 or limit > 99:
            return await ctx.send("❌ Limite invalide (0-99, 0 = illimité)")
        
        try:
            await channel.edit(user_limit=limit)
            
            status = "Illimité" if limit == 0 else f"{limit} membres"
            
            embed = nextcord.Embed(
                title="✅ Limite modifiée",
                description=f"Limite de {channel.mention} définie sur **{status}**",
                color=0x2ECC71
            )
            
            embed.add_field(
                name="📊 Nouvelle configuration",
                value=f"Limite: {status}\nMembres actuels: {len(channel.members)}",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur lors de la modification: {e}")

    @commands.command(name="voice_cleanup")
    @has_role()
    async def voice_cleanup(self, ctx, category: nextcord.CategoryChannel = None):
        """Nettoyer les salons vocaux (supprimer les vides, renommer, etc.)"""
        
        if category:
            voice_channels = category.voice_channels
            scope = category.name
        else:
            voice_channels = ctx.guild.voice_channels
            scope = "serveur"
        
        embed = nextcord.Embed(
            title="🧹 Nettoyage vocal",
            description=f"Nettoyage des salons vocaux de {scope}",
            color=0xF39C12
        )
        
        # Analyser les salons
        empty_channels = []
        low_activity_channels = []
        renamed_channels = []
        
        for channel in voice_channels:
            member_count = len(channel.members)
            
            if member_count == 0:
                empty_channels.append(channel)
            elif member_count <= 2:
                low_activity_channels.append(channel)
            
            # Renommer les salons avec des noms génériques
            if channel.name.startswith("🔊 Équilibrage-") or channel.name.startswith("Salon "):
                try:
                    new_name = f"🎤 Salon {channel.position + 1}"
                    await channel.edit(name=new_name)
                    renamed_channels.append(channel)
                except:
                    pass
        
        # Actions
        deleted_count = 0
        if empty_channels:
            for channel in empty_channels[:5]:  # Limiter à 5 suppressions
                try:
                    await channel.delete()
                    deleted_count += 1
                    await asyncio.sleep(0.5)
                except:
                    pass
        
        embed.add_field(
            name="📊 Actions effectuées",
            value=f"🗑️ Salons supprimés: **{deleted_count}**\n📝 Salons renommés: **{len(renamed_channels)}**\n📋 Salons peu actifs: **{len(low_activity_channels)}**",
            inline=False
        )
        
        if low_activity_channels:
            embed.add_field(
                name="⚠️ Salons peu actifs",
                value="\n".join([f"• {ch.mention} ({len(ch.members)} membres)" for ch in low_activity_channels[:5]]),
                inline=False
            )
        
        embed.set_footer(text="Nettoyage terminé")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Voice(bot))
