import nextcord
from nextcord.ext import commands
import asyncio
import datetime
import random
import aiohttp
import io
import json
import os
from utils.config_manager import config_manager

class ExtendedCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.todo_lists = {}
        self.reminder_data = {}
        self.poll_data = {}
        self.starboard_data = {}
        self.level_data = {}
        self.economy_data = {}
        self.music_data = {}
        self.weather_cache = {}
        
    # ============= SYSTÈME DE TODO =============
    @commands.command(name="todo")
    async def todo_command(self, ctx, action: str = None, *, task: str = None):
        """Gestionnaire de todo"""
        user_id = ctx.author.id
        
        if user_id not in self.todo_lists:
            self.todo_lists[user_id] = []
        
        if action == "add" and task:
            self.todo_lists[user_id].append({
                "task": task,
                "created": datetime.datetime.now().isoformat(),
                "completed": False
            })
            await ctx.send(f"✅ Tâche ajoutée: **{task}**")
            
        elif action == "list":
            if not self.todo_lists[user_id]:
                return await ctx.send("📝 Aucune tâche en cours.")
            
            embed = nextcord.Embed(
                title="📝 Liste des Tâches",
                color=0x3498db
            )
            
            for i, todo in enumerate(self.todo_lists[user_id], 1):
                status = "✅" if todo["completed"] else "⏳"
                embed.add_field(
                    name=f"{status} Tâche #{i}",
                    value=todo["task"],
                    inline=False
                )
            
            await ctx.send(embed=embed)
            
        elif action == "complete" and task:
            for todo in self.todo_lists[user_id]:
                if todo["task"].lower() == task.lower() and not todo["completed"]:
                    todo["completed"] = True
                    todo["completed_at"] = datetime.datetime.now().isoformat()
                    await ctx.send(f"✅ Tâche complétée: **{task}**")
                    break
            else:
                await ctx.send("❌ Tâche non trouvée ou déjà complétée.")
                
        elif action == "remove" and task:
            self.todo_lists[user_id] = [
                todo for todo in self.todo_lists[user_id] 
                if todo["task"].lower() != task.lower()
            ]
            await ctx.send(f"🗑️ Tâche supprimée: **{task}**")
            
        else:
            embed = nextcord.Embed(
                title="📝 Gestionnaire de Todo",
                description="Utilisez `+todo <action> [tâche]`",
                color=0x3498db
            )
            
            embed.add_field(
                name="Actions disponibles",
                value="`add <tâche>` - Ajouter une tâche\n"
                       "`list` - Voir les tâches\n"
                       "`complete <tâche>` - Marquer comme complétée\n"
                       "`remove <tâche>` - Supprimer une tâche",
                inline=False
            )
            
            await ctx.send(embed=embed)
    
    # ============= SYSTÈME DE NIVEAUX =============
    @commands.command(name="rank")
    async def rank(self, ctx, member: nextcord.Member = None):
        """Voir le rang d'un membre"""
        target = member or ctx.author
        
        if ctx.guild.id not in self.level_data:
            self.level_data[ctx.guild.id] = {}
        
        if target.id not in self.level_data[ctx.guild.id]:
            self.level_data[ctx.guild.id][target.id] = {
                "xp": 0,
                "level": 1,
                "messages": 0
            }
        
        user_data = self.level_data[ctx.guild.id][target.id]
        level = user_data["level"]
        xp = user_data["xp"]
        messages = user_data["messages"]
        
        # Calculer XP pour le niveau suivant
        xp_needed = level * 100
        xp_progress = (xp % 100)
        
        embed = nextcord.Embed(
            title=f"🏆 Rang de {target.display_name}",
            color=target.color,
            timestamp=datetime.datetime.now()
        )
        
        embed.set_thumbnail(url=target.display_avatar.url)
        
        embed.add_field(
            name="📊 Niveau",
            value=f"**Niveau {level}** ({xp}/100 XP)",
            inline=True
        )
        
        embed.add_field(
            name="💬 Messages",
            value=f"**{messages}** messages",
            inline=True
        )
        
        embed.add_field(
            name="⭐ XP Total",
            value=f"**{xp}** XP",
            inline=True
        )
        
        # Barre de progression
        progress_bar = "█" * (xp_progress // 10) + "░" * (10 - xp_progress // 10)
        embed.add_field(
            name="📈 Prochain niveau",
            value=f"{progress_bar} {xp_progress}/100 XP",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="leaderboard")
    async def leaderboard(self, ctx):
        """Afficher le classement du serveur"""
        if ctx.guild.id not in self.level_data:
            return await ctx.send("❌ Aucune donnée de niveau disponible.")
        
        # Trier par XP
        sorted_users = sorted(
            self.level_data[ctx.guild.id].items(),
            key=lambda x: x[1]["xp"],
            reverse=True
        )[:10]  # Top 10
        
        embed = nextcord.Embed(
            title="🏆 Classement du Serveur",
            description="Top 10 des membres avec le plus d'XP",
            color=0xFFD700,
            timestamp=datetime.datetime.now()
        )
        
        for i, (user_id, data) in enumerate(sorted_users, 1):
            member = ctx.guild.get_member(user_id)
            if member:
                embed.add_field(
                    name=f"#{i} {member.display_name}",
                    value=f"Niveau {data['level']} - {data['xp']} XP",
                    inline=False
                )
        
        await ctx.send(embed=embed)
    
    # ============= SYSTÈME ÉCONOMIQUE =============
    @commands.command(name="balance")
    async def balance(self, ctx, member: nextcord.Member = None):
        """Voir le solde d'un membre"""
        target = member or ctx.author
        
        if ctx.guild.id not in self.economy_data:
            self.economy_data[ctx.guild.id] = {}
        
        if target.id not in self.economy_data[ctx.guild.id]:
            self.economy_data[ctx.guild.id][target.id] = {
                "coins": 1000,  # Solde de départ
                "bank": 0,
                "last_daily": None
            }
        
        user_economy = self.economy_data[ctx.guild.id][target.id]
        
        embed = nextcord.Embed(
            title="💰 Solde Bancaire",
            description=f"Solde de {target.mention}",
            color=0xF39C12
        )
        
        embed.add_field(
            name="💵 Portefeuille",
            value=f"**{user_economy['coins']}** coins",
            inline=True
        )
        
        embed.add_field(
            name="🏦 Banque",
            value=f"**{user_economy['bank']}** coins",
            inline=True
        )
        
        embed.add_field(
            name="💎 Total",
            value=f"**{user_economy['coins'] + user_economy['bank']}** coins",
            inline=True
        )
        
        embed.set_thumbnail(url=target.display_avatar.url)
        await ctx.send(embed=embed)
    
    @commands.command(name="daily")
    async def daily(self, ctx):
        """Récompense quotidienne"""
        if ctx.guild.id not in self.economy_data:
            self.economy_data[ctx.guild.id] = {}
        
        if ctx.author.id not in self.economy_data[ctx.guild.id]:
            self.economy_data[ctx.guild.id][ctx.author.id] = {
                "coins": 1000,
                "bank": 0,
                "last_daily": None
            }
        
        user_economy = self.economy_data[ctx.guild.id][ctx.author.id]
        now = datetime.datetime.now()
        
        # Vérifier si le daily a déjà été pris
        if user_economy["last_daily"]:
            last_daily = datetime.datetime.fromisoformat(user_economy["last_daily"])
            if (now - last_daily).days < 1:
                return await ctx.send("❌ Tu as déjà pris ta récompense quotidienne ! Reviens demain.")
        
        # Donner la récompense
        reward = random.randint(100, 500)
        user_economy["coins"] += reward
        user_economy["last_daily"] = now.isoformat()
        
        embed = nextcord.Embed(
            title="🎁 Récompense Quotidienne",
            description=f"Tu as reçu **{reward}** coins !",
            color=0x2ECC71
        )
        
        embed.add_field(
            name="💰 Nouveau solde",
            value=f"**{user_economy['coins']}** coins",
            inline=False
        )
        
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)
    
    @commands.command(name="work")
    async def work(self, ctx):
        """Travailler pour gagner des coins"""
        if ctx.guild.id not in self.economy_data:
            self.economy_data[ctx.guild.id] = {}
        
        if ctx.author.id not in self.economy_data[ctx.guild.id]:
            self.economy_data[ctx.guild.id][ctx.author.id] = {
                "coins": 1000,
                "bank": 0,
                "last_daily": None
            }
        
        user_economy = self.economy_data[ctx.guild.id][ctx.author.id]
        
        # Cooldown de 30 minutes
        if hasattr(self, 'work_cooldown'):
            if ctx.author.id in self.work_cooldown:
                if (datetime.datetime.now() - self.work_cooldown[ctx.author.id]).seconds < 1800:
                    remaining = 1800 - (datetime.datetime.now() - self.work_cooldown[ctx.author.id]).seconds
                    return await ctx.send(f"⏰ Attends encore {remaining//60} minutes et {remaining%60} secondes avant de retravailler.")
        
        if not hasattr(self, 'work_cooldown'):
            self.work_cooldown = {}
        
        self.work_cooldown[ctx.author.id] = datetime.datetime.now()
        
        # Gains aléatoires
        earnings = random.randint(50, 200)
        user_economy["coins"] += earnings
        
        jobs = [
            "Développeur Python", "Artiste digital", "Musicien", 
            "Streammer", "Youtuber", "Chef cuisinier",
            "Guide touristique", "Vendeur", "Consultant"
        ]
        job = random.choice(jobs)
        
        embed = nextcord.Embed(
            title="💼 Travail Terminé",
            description=f"Tu as travaillé comme **{job}**",
            color=0x2ECC71
        )
        
        embed.add_field(
            name="💰 Gains",
            value=f"+{earnings} coins",
            inline=True
        )
        
        embed.add_field(
            name="💰 Solde actuel",
            value=f"{user_economy['coins']} coins",
            inline=True
        )
        
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)
    
    # ============= SYSTÈME DE MUSIQUE =============
    @commands.command(name="play")
    async def play(self, ctx, *, query: str):
        """Jouer de la musique"""
        if not ctx.author.voice:
            return await ctx.send("❌ Tu dois être dans un salon vocal !")
        
        # Vérifier si le bot est dans un salon vocal
        if not ctx.voice_client:
            try:
                await ctx.author.voice.channel.connect()
            except:
                return await ctx.send("❌ Je ne peux pas rejoindre ton salon vocal.")
        
        # Simulation de lecture (à remplacer avec un vrai bot musical)
        embed = nextcord.Embed(
            title="🎵 Musique",
            description=f"Recherche de: **{query}**",
            color=0x1ABC9C
        )
        
        embed.add_field(
            name="🎧 En cours de lecture",
            value="*Simulation - Intégrer avec un vrai bot musical*",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="skip")
    async def skip(self, ctx):
        """Passer à la musique suivante"""
        if not ctx.voice_client:
            return await ctx.send("❌ Je ne suis pas dans un salon vocal.")
        
        await ctx.send("⏭ Musique passée !")
    
    @commands.command(name="queue")
    async def queue(self, ctx):
        """Voir la file d'attente"""
        embed = nextcord.Embed(
            title="📋 File d'Attente",
            description="*Simulation - Intégrer avec un vrai bot musical*",
            color=0x1ABC9C
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="volume")
    async def volume(self, ctx, volume: int = None):
        """Régler le volume"""
        if volume is None:
            return await ctx.send("🔊 Volume actuel: 50%")
        
        if volume < 0 or volume > 100:
            return await ctx.send("❌ Le volume doit être entre 0 et 100.")
        
        await ctx.send(f"🔊 Volume réglé sur {volume}%")
    
    # ============= SYSTÈME DE STARBOARD =============
    @commands.command(name="starboard")
    async def starboard(self, ctx):
        """Afficher la starboard du serveur"""
        if ctx.guild.id not in self.starboard_data:
            self.starboard_data[ctx.guild.id] = []
        
        if not self.starboard_data[ctx.guild.id]:
            return await ctx.send("❌ Aucun message étoilé.")
        
        # Trier par nombre d'étoiles
        starred_messages = sorted(
            self.starboard_data[ctx.guild.id],
            key=lambda x: x["stars"],
            reverse=True
        )[:5]  # Top 5
        
        embed = nextcord.Embed(
            title="⭐ Starboard",
            description="Top 5 des messages les plus étoilés",
            color=0xFFD700
        )
        
        for i, msg_data in enumerate(starred_messages, 1):
            embed.add_field(
                name=f"⭐ {msg_data['stars']} étoiles",
                value=f"**{msg_data['author']}**: {msg_data['content'][:50]}...",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Détecter les réactions avec étoile"""
        if str(payload.emoji) == "⭐":
            if payload.guild_id not in self.starboard_data:
                self.starboard_data[payload.guild_id] = []
            
            # Vérifier si le message est déjà dans la starboard
            for msg_data in self.starboard_data[payload.guild_id]:
                if msg_data["message_id"] == payload.message_id:
                    msg_data["stars"] += 1
                    return
            
            # Ajouter le message à la starboard
            channel = self.bot.get_channel(payload.channel_id)
            if channel:
                try:
                    message = await channel.fetch_message(payload.message_id)
                    self.starboard_data[payload.guild.id].append({
                        "message_id": message.id,
                        "author": message.author.display_name,
                        "content": message.content,
                        "stars": 1,
                        "timestamp": message.created_at.isoformat()
                    })
                except:
                    pass
    
    # ============= SYSTÈME DE MÉTÉO =============
    @commands.command(name="weather")
    async def weather(self, ctx, *, city: str):
        """Météo d'une ville"""
        # Vérifier le cache
        if city.lower() in self.weather_cache:
            cached = self.weather_cache[city.lower()]
            if (datetime.datetime.now() - cached["timestamp"]).seconds < 1800:  # 30 minutes
                embed = nextcord.Embed(
                    title="🌤️ Météo",
                    description=f"Météo de **{city.title()}**",
                    color=0x3498db
                )
                
                embed.add_field(
                    name="🌡️ Température",
                    value=f"{cached['temp']}°C",
                    inline=True
                )
                
                embed.add_field(
                    name="💧 Humidité",
                    value=f"{cached['humidity']}%",
                    inline=True
                )
                
                embed.add_field(
                    name="🌬 Description",
                    value=cached['description'],
                    inline=False
                )
                
                embed.set_thumbnail(url=cached['icon'])
                return await ctx.send(embed=embed)
        
        # Simulation de données météo (à remplacer avec une vraie API)
        weather_data = {
            "temp": random.randint(10, 30),
            "humidity": random.randint(30, 80),
            "description": random.choice(["Ensoleillé", "Nuageux", "Pluvieux", "Orageux"]),
            "icon": f"https://openweathermap.org/img/wn/{random.choice(['01d', '02d', '03d', '04d', '09d', '10d', '11d', '13d'])}@2x.png"
        }
        
        # Mettre en cache
        self.weather_cache[city.lower()] = {
            **weather_data,
            "timestamp": datetime.datetime.now()
        }
        
        embed = nextcord.Embed(
            title="🌤️ Météo",
            description=f"Météo de **{city.title()}**",
            color=0x3498db
        )
        
        embed.add_field(
            name="🌡️ Température",
            value=f"{weather_data['temp']}°C",
            inline=True
        )
        
        embed.add_field(
            name="💧 Humidité",
            value=f"{weather_data['humidity']}%",
            inline=True
        )
        
        embed.add_field(
            name="🌬 Description",
            value=weather_data['description'],
            inline=False
        )
        
        embed.set_thumbnail(url=weather_data['icon'])
        embed.set_footer(text="Données mises à jour toutes les 30 minutes")
        
        await ctx.send(embed=embed)
    
    # ============= SYSTÈME DE RAPPELS AVANCÉ =============
    @commands.command(name="remindme")
    async def remindme(self, ctx, time: str, *, message: str):
        """Rappel personnel"""
        try:
            if time.endswith('h'):
                seconds = int(time[:-1]) * 3600
            elif time.endswith('m'):
                seconds = int(time[:-1]) * 60
            elif time.endswith('d'):
                seconds = int(time[:-1]) * 86400
            else:
                return await ctx.send("❌ Format invalide. Utilise: 1h, 30m, 1d")
        except:
            return await ctx.send("❌ Temps invalide.")
        
        if seconds < 60:
            return await ctx.send("❌ Durée minimale: 1 minute.")
        
        if seconds > 2592000:  # 30 jours
            return await ctx.send("❌ Durée maximale: 30 jours.")
        
        await ctx.send(f"⏰ Rappel programmé pour dans {time}!")
        
        await asyncio.sleep(seconds)
        
        embed = nextcord.Embed(
            title="⏰ RAPPEL",
            description=f"**Message:** {message}\n**Programmé il y a:** {time}",
            color=0x3498db
        )
        
        embed.set_author(
            name=ctx.author.name,
            icon_url=ctx.author.display_avatar.url
        )
        
        await ctx.author.send(embed=embed)
    
    # ============= SYSTÈME DE SONDAGES AVANCÉ =============
    @commands.command(name="poll")
    async def poll(self, ctx, question: str, *options):
        """Créer un sondage avancé"""
        if len(options) < 2:
            return await ctx.send("❌ Il faut au moins 2 options.")
        
        if len(options) > 10:
            return await ctx.send("❌ Maximum 10 options autorisées.")
        
        embed = nextcord.Embed(
            title="📊 Sondage",
            description=question,
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        
        reactions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        
        for i, option in enumerate(options[:10]):
            embed.add_field(name=f"Option {i+1}", value=option, inline=False)
        
        message = await ctx.send(embed=embed)
        
        for i in range(len(options)):
            await message.add_reaction(reactions[i])
        
        # Sauvegarder les données du sondage
        self.poll_data[message.id] = {
            "question": question,
            "options": options,
            "author": ctx.author.id,
            "created_at": datetime.datetime.now().isoformat()
        }
    
    # ============= SYSTÈME DE BACKUP =============
    @commands.command(name="backup")
    @commands.has_permissions(administrator=True)
    async def backup(self, ctx):
        """Créer une sauvegarde complète du serveur"""
        embed = nextcord.Embed(
            title="💾 Sauvegarde du Serveur",
            description="Création d'une sauvegarde complète...",
            color=0xF39C12
        )
        
        msg = await ctx.send(embed=embed)
        
        backup_data = {
            "server_info": {
                "name": ctx.guild.name,
                "id": ctx.guild.id,
                "owner": ctx.guild.owner_id,
                "created_at": ctx.guild.created_at.isoformat(),
                "member_count": len(ctx.guild.members),
                "role_count": len(ctx.guild.roles),
                "channel_count": len(ctx.guild.channels),
                "emoji_count": len(ctx.guild.emojis)
            },
            "roles": [],
            "channels": [],
            "members": [],
            "bans": [],
            "created_at": datetime.datetime.now().isoformat()
        }
        
        # Sauvegarder les rôles
        for role in ctx.guild.roles:
            backup_data["roles"].append({
                "id": role.id,
                "name": role.name,
                "color": str(role.color),
                "permissions": role.permissions.value,
                "position": role.position,
                "mentionable": role.mentionable,
                "hoist": role.hoist,
                "managed": role.managed
            })
        
        # Sauvegarder les salons
        for channel in ctx.guild.channels:
            channel_data = {
                "id": channel.id,
                "name": channel.name,
                "type": str(channel.type),
                "position": channel.position,
                "nsfw": channel.is_nsfw() if hasattr(channel, 'is_nsfw') else False,
                "topic": channel.topic if hasattr(channel, 'topic') else None
            }
            
            if hasattr(channel, 'overwrites'):
                channel_data["overwrites"] = [
                    {
                        "target_id": ow.target.id,
                        "target_type": "role" if isinstance(ow.target, nextcord.Role) else "member",
                        "allow": ow.allow.value,
                        "deny": ow.deny.value
                    }
                    for ow in channel.overwrites
                ]
            
            backup_data["channels"].append(channel_data)
        
        # Sauvegarder les membres (limité pour éviter trop de données)
        for member in ctx.guild.members[:100]:  # Limite à 100 membres
            backup_data["members"].append({
                "id": member.id,
                "name": member.name,
                "display_name": member.display_name,
                "nick": member.nick,
                "joined_at": member.joined_at.isoformat(),
                "roles": [role.id for role in member.roles],
                "status": str(member.status),
                "bot": member.bot
            })
        
        # Sauvegarder le fichier
        os.makedirs("data/backups", exist_ok=True)
        backup_filename = f"data/backups/backup_{ctx.guild.id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(backup_filename, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        embed = nextcord.Embed(
            title="✅ Sauvegarde Terminée",
            description=f"Sauvegarde créée: `{backup_filename}`",
            color=0x2ECC71
        )
        
        embed.add_field(
            name="📊 Statistiques",
            value=f"Rôles: {len(backup_data['roles'])}\n"
                   f"Salons: {len(backup_data['channels'])}\n"
                   f"Membres: {len(backup_data['members'])}",
            inline=False
        )
        
        await msg.edit(embed=embed)
    
    # ============= SYSTÈME DE STATISTIQUES SERVEUR =============
    @commands.command(name="serverstats")
    async def server_stats_extended(self, ctx):
        """Statistiques détaillées du serveur"""
        guild = ctx.guild
        
        embed = nextcord.Embed(
            title="📊 Statistiques Détaillées",
            description=f"Statistiques de **{guild.name}**",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        
        # Informations générales
        total_members = len(guild.members)
        online_members = len([m for m in guild.members if m.status != nextcord.Status.offline])
        bots = len([m for m in guild.members if m.bot])
        humans = total_members - bots
        
        embed.add_field(
            name="👥 Membres",
            value=f"Total: {total_members}\nHumains: {humans}\nBots: {bots}\nEn ligne: {online_members}",
            inline=True
        )
        
        # Salons
        text_channels = len([c for c in guild.channels if isinstance(c, nextcord.TextChannel)])
        voice_channels = len([c for c in guild.channels if isinstance(c, nextcord.VoiceChannel)])
        categories = len(guild.categories)
        
        embed.add_field(
            name="📝 Salons",
            value=f"Texte: {text_channels}\nVocal: {voice_channels}\nCatégories: {categories}",
            inline=True
        )
        
        # Rôles et permissions
        roles = len(guild.roles)
        admin_roles = len([r for r in guild.roles if r.permissions.administrator])
        mod_roles = len([r for r in guild.roles if r.permissions.manage_messages])
        
        embed.add_field(
            name="🎭 Rôles",
            value=f"Total: {roles}\nAdmin: {admin_roles}\nModo: {mod_roles}",
            inline=True
        )
        
        # Émojis et autres
        emojis = len(guild.emojis)
        stickers = len(guild.stickers) if hasattr(guild, 'stickers') else 0
        boosts = guild.premium_subscription_count
        
        embed.add_field(
            name="🎨 Autres",
            value=f"Émojis: {emojis}/{guild.emoji_limit}\nStickers: {stickers}\nBoosts: {boosts}",
            inline=True
        )
        
        # Activité récente
        embed.add_field(
            name="📈 Activité",
            value=f"Créé le: {guild.created_at.strftime('%d/%m/%Y')}\n"
                   f"Boost Level: {guild.premium_tier}\n"
                   f"Features: {len(guild.features) if guild.features else 0}",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    # ============= COMMANDES D'UTILITAIRES =============
    @commands.command(name="timer")
    async def timer(self, ctx, seconds: int):
        """Minuteur de temps"""
        if seconds < 1 or seconds > 3600:
            return await ctx.send("❌ Le timer doit être entre 1 et 3600 secondes.")
        
        embed = nextcord.Embed(
            title="⏱️ Minuteur",
            description=f"Minuteur de **{seconds}** secondes démarré !",
            color=0x3498db
        )
        
        msg = await ctx.send(embed=embed)
        
        await asyncio.sleep(seconds)
        
        embed = nextcord.Embed(
            title="⏰ Temps écoulé !",
            description=f"Les **{seconds}** secondes sont terminées !",
            color=0x2ECC71
        )
        
        await msg.edit(embed=embed)
    
    @commands.command(name="choose")
    async def choose(self, ctx, *options):
        """Choisir aléatoirement parmi des options"""
        if len(options) < 2:
            return await ctx.send("❌ Il faut au moins 2 options.")
        
        choice = random.choice(options)
        
        embed = nextcord.Embed(
            title="🎲 Choix Aléatoire",
            description=f"J'ai choisi: **{choice}**",
            color=0x3498db
        )
        
        embed.add_field(
            name="📋 Options disponibles",
            value="\n".join([f"• {opt}" for opt in options]),
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="countdown")
    async def countdown(self, ctx, seconds: int):
        """Compte à rebours"""
        if seconds < 1 or seconds > 60:
            return await ctx.send("❌ Le countdown doit être entre 1 et 60 secondes.")
        
        embed = nextcord.Embed(
            title="⏰ Compte à Rebours",
            description=f"Décompte de **{seconds}** secondes",
            color=0xE74C3C
        )
        
        msg = await ctx.send(embed=embed)
        
        for i in range(seconds, 0, -1):
            await asyncio.sleep(1)
            embed.description = f"Décompte: **{i}** secondes restantes"
            await msg.edit(embed=embed)
        
        embed.description = "⏰ Temps écoulé !"
        embed.color = 0x2ECC71
        await msg.edit(embed=embed)
    
    @commands.command(name="roll")
    async def roll(self, ctx, max_number: int = 100):
        """Lancer un nombre aléatoire"""
        if max_number < 1 or max_number > 1000000:
            return await ctx.send("❌ Le nombre doit être entre 1 et 1000000.")
        
        result = random.randint(1, max_number)
        
        embed = nextcord.Embed(
            title="🎲 Lancer de Dé",
            description=f"Nombre aléatoire entre 1 et {max_number}: **{result}**",
            color=0x3498db
        )
        
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(ExtendedCommands(bot))
