import nextcord
from nextcord.ext import commands
import asyncio
import random
import datetime
import json
import os
from utils.config_manager import config_manager

class CommunityFeatures(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.giveaway_data = {}
        self.poll_data = {}
        self.suggestions_data = {}
        self.reaction_roles = {}
        
    # ============= SUGGESTIONS =============
    @commands.command(name="suggest")
    async def suggest(self, ctx, *, suggestion: str):
        """Faire une suggestion pour le serveur"""
        if len(suggestion) < 10:
            return await ctx.send("❌ La suggestion doit faire au moins 10 caractères.")
        
        # Récupérer le salon des suggestions
        suggestion_channel_id = config_manager.get("server_specific.suggestion_channel")
        if not suggestion_channel_id:
            return await ctx.send("❌ Aucun salon de suggestions configuré.")
        
        suggestion_channel = ctx.guild.get_channel(suggestion_channel_id)
        if not suggestion_channel:
            return await ctx.send("❌ Salon de suggestions introuvable.")
        
        embed = nextcord.Embed(
            title="💡 Nouvelle Suggestion",
            description=suggestion,
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        embed.set_footer(text=f"ID: {ctx.author.id}")
        
        message = await suggestion_channel.send(embed=embed)
        await message.add_reaction("👍")
        await message.add_reaction("👎")
        
        await ctx.send("✅ Suggestion envoyée avec succès !")
        await ctx.author.send(f"✅ Ta suggestion a été envoyée dans {suggestion_channel.mention}")
    
    @commands.command(name="setsuggestions")
    @commands.has_permissions(administrator=True)
    async def set_suggestions(self, ctx, channel: nextcord.TextChannel):
        """Définir le salon des suggestions"""
        config_manager.set("server_specific.suggestion_channel", channel.id)
        await ctx.send(f"✅ Salon des suggestions défini sur {channel.mention}")
    
    # ============= SONDAGES =============
    @commands.command(name="poll")
    @commands.has_permissions(manage_messages=True)
    async def poll(self, ctx, question: str, *options):
        """Créer un sondage"""
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
        
        self.poll_data[message.id] = {
            "question": question,
            "options": options,
            "author": ctx.author.id,
            "created_at": datetime.datetime.now()
        }
    
    # ============= GIVEAWAYS =============
    @commands.command(name="giveaway")
    @commands.has_permissions(manage_messages=True)
    async def giveaway(self, ctx, duration: str, *, prize: str):
        """Lancer un giveaway (format: 1h, 30m, 1d)"""
        try:
            if duration.endswith('h'):
                seconds = int(duration[:-1]) * 3600
            elif duration.endswith('m'):
                seconds = int(duration[:-1]) * 60
            elif duration.endswith('d'):
                seconds = int(duration[:-1]) * 86400
            else:
                return await ctx.send("❌ Format invalide. Utilise: 1h, 30m, 1d")
        except:
            return await ctx.send("❌ Durée invalide.")
        
        if seconds < 60:
            return await ctx.send("❌ Durée minimale: 1 minute.")
        
        if seconds > 604800:  # 7 jours
            return await ctx.send("❌ Durée maximale: 7 jours.")
        
        embed = nextcord.Embed(
            title="🎉 GIVEAWAY 🎉",
            description=f"**Prix:** {prize}\n\n**Durée:** {duration}\n\nRéagissez avec 🎉 pour participer !",
            color=0xFFD700,
            timestamp=datetime.datetime.now()
        )
        
        embed.set_footer(text=f"Se termine dans {duration}")
        
        message = await ctx.send(embed=embed)
        await message.add_reaction("🎉")
        
        self.giveaway_data[message.id] = {
            "prize": prize,
            "end_time": datetime.datetime.now() + datetime.timedelta(seconds=seconds),
            "participants": [],
            "channel": ctx.channel.id,
            "message_id": message.id
        }
        
        # Démarrer le timer
        self.bot.loop.create_task(self.end_giveaway(message.id, seconds))
    
    async def end_giveaway(self, message_id, delay):
        await asyncio.sleep(delay)
        
        if message_id not in self.giveaway_data:
            return
        
        giveaway = self.giveaway_data[message_id]
        channel = self.bot.get_channel(giveaway["channel"])
        
        if not channel:
            return
        
        try:
            message = await channel.fetch_message(message_id)
        except:
            return
        
        if not giveaway["participants"]:
            await channel.send("❌ Le giveaway s'est terminé sans participants.")
            del self.giveaway_data[message_id]
            return
        
        winner = random.choice(giveaway["participants"])
        winner_user = self.bot.get_user(winner)
        
        embed = nextcord.Embed(
            title="🎉 GIVEAWAY TERMINÉ 🎉",
            description=f"**Prix:** {giveaway['prize']}\n\n**Gagnant:** {winner_user.mention}",
            color=0x2ECC71
        )
        
        await message.edit(embed=embed, content=None)
        await channel.send(f"🎉 Félicitations {winner_user.mention} ! Tu as gagné **{giveaway['prize']}** !")
        
        del self.giveaway_data[message_id]
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id in self.giveaway_data:
            if str(payload.emoji) == "🎉":
                if payload.user_id not in self.giveaway_data[payload.message_id]["participants"]:
                    self.giveaway_data[payload.message_id]["participants"].append(payload.user_id)
    
    # ============= RÔLES PAR RÉACTION =============
    @commands.command(name="reactionrole")
    @commands.has_permissions(manage_roles=True)
    async def reaction_role(self, ctx, message_id: str, emoji: str, role: nextcord.Role):
        """Ajouter un rôle par réaction"""
        try:
            message = await ctx.channel.fetch_message(int(message_id))
        except:
            return await ctx.send("❌ Message introuvable.")
        
        await message.add_reaction(emoji)
        
        if message.id not in self.reaction_roles:
            self.reaction_roles[message.id] = {}
        
        self.reaction_roles[message.id][emoji] = role.id
        
        embed = nextcord.Embed(
            title="✅ Rôle par réaction ajouté",
            description=f"Réagissez avec {emoji} pour obtenir le rôle {role.mention}",
            color=0x2ECC71
        )
        
        await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id in self.reaction_roles:
            if str(payload.emoji) in self.reaction_roles[payload.message_id]:
                guild = self.bot.get_guild(payload.guild_id)
                role_id = self.reaction_roles[payload.message_id][str(payload.emoji)]
                role = guild.get_role(role_id)
                
                if role:
                    member = guild.get_member(payload.user_id)
                    if member and not payload.bot:
                        await member.add_roles(role)
    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.message_id in self.reaction_roles:
            if str(payload.emoji) in self.reaction_roles[payload.message_id]:
                guild = self.bot.get_guild(payload.guild_id)
                role_id = self.reaction_roles[payload.message_id][str(payload.emoji)]
                role = guild.get_role(role_id)
                
                if role:
                    member = guild.get_member(payload.user_id)
                    if member and not payload.bot:
                        await member.remove_roles(role)
    
    # ============= STATISTIQUES SERVEUR =============
    @commands.command(name="serverstats")
    async def server_stats(self, ctx):
        """Afficher les statistiques du serveur"""
        embed = nextcord.Embed(
            title="📊 Statistiques du Serveur",
            description=f"Statistiques de {ctx.guild.name}",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        
        total_members = len(ctx.guild.members)
        online_members = len([m for m in ctx.guild.members if m.status != nextcord.Status.offline])
        text_channels = len(ctx.guild.text_channels)
        voice_channels = len(ctx.guild.voice_channels)
        roles = len(ctx.guild.roles)
        emojis = len(ctx.guild.emojis)
        
        embed.add_field(name="👥 Membres", value=f"Total: {total_members}\nEn ligne: {online_members}", inline=True)
        embed.add_field(name="📝 Salons", value=f"Texte: {text_channels}\nVocal: {voice_channels}", inline=True)
        embed.add_field(name="🎭 Autres", value=f"Rôles: {roles}\nÉmojis: {emojis}", inline=True)
        
        # Membres par statut
        online = len([m for m in ctx.guild.members if m.status == nextcord.Status.online])
        idle = len([m for m in ctx.guild.members if m.status == nextcord.Status.idle])
        dnd = len([m for m in ctx.guild.members if m.status == nextcord.Status.dnd])
        offline = len([m for m in ctx.guild.members if m.status == nextcord.Status.offline])
        
        embed.add_field(
            name="📈 Statuts",
            value=f"🟢 {online} | 🌙 {idle} | 🔴 {dnd} | ⚫ {offline}",
            inline=False
        )
        
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        embed.set_footer(text=f"Serveur créé le {ctx.guild.created_at.strftime('%d/%m/%Y')}")
        
        await ctx.send(embed=embed)
    
    # ============= INFO UTILISATEUR =============
    @commands.command(name="userinfo")
    async def user_info(self, ctx, member: nextcord.Member = None):
        """Afficher les informations d'un utilisateur"""
        if member is None:
            member = ctx.author
        
        embed = nextcord.Embed(
            title=f"👤 Informations sur {member.name}",
            color=member.color,
            timestamp=datetime.datetime.now()
        )
        
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"ID: {member.id}")
        
        # Informations de base
        embed.add_field(
            name="📝 Informations",
            value=f"**Nom:** {member.name}\n**Surnom:** {member.nick or 'Aucun'}\n**ID:** {member.id}",
            inline=False
        )
        
        # Dates
        embed.add_field(
            name="📅 Dates",
            value=f"**Rejoint le:** {member.joined_at.strftime('%d/%m/%Y %H:%M')}\n**Compte créé:** {member.created_at.strftime('%d/%m/%Y %H:%M')}",
            inline=False
        )
        
        # Rôles
        if member.roles:
            roles = [role.mention for role in member.roles if role != ctx.guild.default_role]
            embed.add_field(
                name="🎭 Rôles",
                value=f"{len(roles)} rôle(s)\n" + " ".join(roles[:10]) + ("..." if len(roles) > 10 else ""),
                inline=False
            )
        
        # Statut
        status_emoji = {
            nextcord.Status.online: "🟢",
            nextcord.Status.idle: "🌙", 
            nextcord.Status.dnd: "🔴",
            nextcord.Status.offline: "⚫"
        }
        
        embed.add_field(
            name="📊 Statut",
            value=f"{status_emoji.get(member.status, '❓')} {member.status}",
            inline=True
        )
        
        # Activité
        if member.activity:
            embed.add_field(
                name="🎮 Activité",
                value=f"**{member.activity.type.name}:** {member.activity.name}",
                inline=True
            )
        
        await ctx.send(embed=embed)
    
    # ============= SALON TEMPORAIRE =============
    @commands.command(name="tempvoice")
    async def temp_voice(self, ctx, *, name: str = "Salon Temporaire"):
        """Créer un salon vocal temporaire"""
        if not ctx.author.voice:
            return await ctx.send("❌ Tu dois être dans un salon vocal pour créer un salon temporaire.")
        
        category = ctx.author.voice.channel.category
        if not category:
            return await ctx.send("❌ Le salon vocal doit être dans une catégorie.")
        
        # Créer le salon temporaire
        overwrites = {
            ctx.guild.default_role: nextcord.PermissionOverwrite(connect=False),
            ctx.author: nextcord.PermissionOverwrite(
                connect=True,
                speak=True,
                mute_members=True,
                deafen_members=True,
                move_members=True,
                manage_channels=True
            )
        }
        
        temp_channel = await ctx.guild.create_voice_channel(
            name=f"🔊 {name}",
            category=category,
            overwrites=overwrites
        )
        
        # Déplacer l'utilisateur
        await ctx.author.move_to(temp_channel)
        
        embed = nextcord.Embed(
            title="✅ Salon Temporaire Créé",
            description=f"Salon {temp_channel.mention} créé pour {ctx.author.mention}",
            color=0x2ECC71
        )
        
        await ctx.send(embed=embed)
        
        # Supprimer le salon quand tout le monde est parti
        self.bot.loop.create_task(self.delete_empty_voice(temp_channel))
    
    async def delete_empty_voice(self, channel):
        """Supprimer un salon vocal temporaire quand il est vide"""
        while True:
            await asyncio.sleep(30)  # Vérifier toutes les 30 secondes
            
            if len(channel.members) == 0:
                try:
                    await channel.delete()
                    break
                except:
                    break
    
    # ============= COMMANDES UTILITAIRES =============
    @commands.command(name="calc")
    async def calc(self, ctx, *, expression: str):
        """Calculatrice simple"""
        try:
            # Sécuriser l'évaluation
            allowed_chars = set("0123456789+-*/().")
            if not all(c in allowed_chars or c.isspace() for c in expression):
                return await ctx.send("❌ Caractères non autorisés.")
            
            result = eval(expression)
            await ctx.send(f"🧮 **{expression}** = **{result}**")
        except:
            await ctx.send("❌ Expression invalide.")
    
    @commands.command(name="remind")
    async def remind(self, ctx, time: str, *, message: str):
        """Rappel (format: 1h, 30m, 1d)"""
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
        
        await ctx.author.send(embed=embed)
    
    @commands.command(name="translate")
    async def translate(self, ctx, lang: str, *, text: str):
        """Traduire un texte (langues: fr, en, es, de, it)"""
        # Simulation de traduction (à remplacer par une vraie API)
        translations = {
            "fr": {"en": "Hello world", "es": "Hola mundo", "de": "Hallo Welt", "it": "Ciao mondo"},
            "en": {"fr": "Bonjour le monde", "es": "Hola mundo", "de": "Hallo Welt", "it": "Ciao mondo"},
            "es": {"fr": "Bonjour le monde", "en": "Hello world", "de": "Hallo Welt", "it": "Ciao mondo"},
            "de": {"fr": "Bonjour le monde", "en": "Hello world", "es": "Hola mundo", "it": "Ciao mondo"},
            "it": {"fr": "Bonjour le monde", "en": "Hello world", "es": "Hola mundo", "de": "Hallo Welt"}
        }
        
        if lang not in translations:
            return await ctx.send("❌ Langue source non supportée. Utilise: fr, en, es, de, it")
        
        # Détecter la langue cible (simple simulation)
        target_lang = "en" if lang != "en" else "fr"
        
        if target_lang in translations[lang]:
            result = translations[lang][target_lang]
        else:
            result = text  # Si pas de traduction
        
        embed = nextcord.Embed(
            title="🌐 Traduction",
            description=f"**Original ({lang}):** {text}\n**Traduit ({target_lang}):** {result}",
            color=0x3498db
        )
        
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(CommunityFeatures(bot))
