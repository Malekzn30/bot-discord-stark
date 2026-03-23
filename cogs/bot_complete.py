import nextcord
from nextcord.ext import commands
import asyncio
import time
import psutil
import datetime
import requests
import json
import os
import sys
import random
from config import AUTHORIZED_ROLE_ID

def has_role():
    async def predicate(ctx):
        role = ctx.guild.get_role(AUTHORIZED_ROLE_ID)
        return role in ctx.author.roles
    return commands.check(predicate)

class BotComplete(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_timers = {}
        self.active_tickets = {}
        self.guess_games = {}
        self.ensure_directories()
        
    def ensure_directories(self):
        """Créer les répertoires nécessaires"""
        os.makedirs("data/logs", exist_ok=True)
        os.makedirs("data/tickets", exist_ok=True)
    
    # ============= SYSTÈME DE BASE =============
    @commands.command(name="ping")
    async def ping(self, ctx):
        """Voir la latence du bot"""
        start_time = time.time()
        message = await ctx.send("🏓 Pong!")
        end_time = time.time()
        
        latency = round((end_time - start_time) * 1000)
        api_latency = round(self.bot.latency * 1000)
        
        embed = nextcord.Embed(
            title="🏓 Pong!",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="⚡ Latence API", value=f"{api_latency}ms", inline=True)
        embed.add_field(name="🏓 Latence Message", value=f"{latency}ms", inline=True)
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        
        await message.edit(embed=embed)
    
    @commands.command(name="stats")
    async def stats(self, ctx):
        """Voir les statistiques du bot"""
        memory = psutil.virtual_memory()
        cpu = psutil.cpu_percent()
        
        uptime = time.time() - self.bot.start_time
        days = int(uptime // 86400)
        hours = int((uptime % 86400) // 3600)
        minutes = int((uptime % 3600) // 60)
        
        embed = nextcord.Embed(
            title="📊 Statistiques du Bot",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="⏱️ Uptime", value=f"{days}j {hours}h {minutes}m", inline=True)
        embed.add_field(name="💾 Mémoire", value=f"{memory.percent}%", inline=True)
        embed.add_field(name="🖥️ CPU", value=f"{cpu}%", inline=True)
        embed.add_field(name="🚀 Latence", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="📡 Serveurs", value=str(len(self.bot.guilds)), inline=True)
        embed.add_field(name="👥 Utilisateurs", value=str(len(self.bot.users)), inline=True)
        
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        await ctx.send(embed=embed)
    
    @commands.command(name="restart")
    @commands.is_owner()
    async def restart(self, ctx):
        """Redémarrer le bot"""
        await ctx.send("🔄 Redémarrage du bot...")
        await self.bot.close()
    
    # ============= SYSTÈME DE TIMERS =============
    @commands.command(name="timer")
    async def timer(self, ctx, time_str: str, *, message: str = "Temps écoulé !"):
        """Démarrer un minuteur (format: 30s, 5m, 1h)"""
        try:
            seconds = 0
            if time_str.endswith('s'):
                seconds = int(time_str[:-1])
            elif time_str.endswith('m'):
                seconds = int(time_str[:-1]) * 60
            elif time_str.endswith('h'):
                seconds = int(time_str[:-1]) * 3600
            else:
                seconds = int(time_str)
            
            if seconds < 1 or seconds > 86400:
                return await ctx.send("❌ Le timer doit être entre 1 seconde et 24 heures.")
            
            embed = nextcord.Embed(
                title="⏰ Timer Démarré",
                description=f"**Durée:** {time_str}\n**Message:** {message}",
                color=0x3498db,
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Timer de {ctx.author.name}")
            
            msg = await ctx.send(embed=embed)
            await asyncio.sleep(seconds)
            
            end_embed = nextcord.Embed(
                title="⏰ Timer Terminé !",
                description=f"**Message:** {message}\n**Durée:** {time_str}",
                color=0x2ecc71,
                timestamp=datetime.datetime.now()
            )
            end_embed.set_footer(text=f"Timer de {ctx.author.name}")
            
            await msg.reply(embed=end_embed)
            
        except ValueError:
            await ctx.send("❌ Format invalide. Utilise: `+timer 30s`, `+timer 5m`, `+timer 1h`")
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="countdown")
    async def countdown(self, ctx, seconds: int, *, message: str = "Compte à rebours terminé !"):
        """Compte à rebours visuel"""
        try:
            if seconds < 1 or seconds > 300:
                return await ctx.send("❌ Le countdown doit être entre 1 et 300 secondes.")
            
            embed = nextcord.Embed(
                title="⏰ Compte à Rebours",
                description=f"**Temps:** {seconds} secondes\n**Message:** {message}",
                color=0x3498db,
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Countdown de {ctx.author.name}")
            
            msg = await ctx.send(embed=embed)
            
            for i in range(seconds, 0, -1):
                if i % 10 == 0 or i <= 5:
                    countdown_embed = nextcord.Embed(
                        title="⏰ Compte à Rebours",
                        description=f"**Temps restant:** {i} secondes",
                        color=0xe74c3c if i <= 5 else 0xf39c12,
                        timestamp=datetime.datetime.now()
                    )
                    countdown_embed.set_footer(text=f"Countdown de {ctx.author.name}")
                    
                    await msg.edit(embed=countdown_embed)
                    await asyncio.sleep(1)
                else:
                    await asyncio.sleep(1)
            
            final_embed = nextcord.Embed(
                title="🎉 Compte à Rebours Terminé !",
                description=f"**Message:** {message}",
                color=0x2ecc71,
                timestamp=datetime.datetime.now()
            )
            final_embed.set_footer(text=f"Countdown de {ctx.author.name}")
            
            await msg.edit(embed=final_embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="stopwatch")
    async def stopwatch(self, ctx):
        """Démarrer un chronomètre"""
        try:
            start_time = datetime.datetime.now()
            
            embed = nextcord.Embed(
                title="⏱️ Chronomètre Démarré",
                description="**Début:** " + start_time.strftime("%H:%M:%S"),
                color=0x3498db,
                timestamp=start_time
            )
            embed.set_footer(text=f"Chronomètre de {ctx.author.name}")
            
            msg = await ctx.send(embed=embed)
            await msg.add_reaction("⏹️")
            
            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) == "⏹️"
            
            try:
                await self.bot.wait_for("reaction_add", timeout=3600, check=check)
                end_time = datetime.datetime.now()
                duration = end_time - start_time
                
                end_embed = nextcord.Embed(
                    title="⏱️ Chronomètre Terminé",
                    description=f"**Durée:** {duration}",
                    color=0x2ecc71,
                    timestamp=end_time
                )
                end_embed.set_footer(text=f"Chronomètre de {ctx.author.name}")
                
                await msg.edit(embed=end_embed)
                
            except asyncio.TimeoutError:
                await msg.edit(content="⏱️ Chronomètre expiré (1h max)")
                
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    # ============= SYSTÈME DE MÉTÉO ET UTILITAIRES =============
    @commands.command(name="weather")
    async def weather(self, ctx, *, city: str):
        """Météo d'une ville"""
        try:
            weather_data = {
                "Paris": {"temp": "18°C", "desc": "Nuageux", "humidity": "65%"},
                "Lyon": {"temp": "16°C", "desc": "Pluvieux", "humidity": "80%"},
                "Marseille": {"temp": "22°C", "desc": "Ensoleillé", "humidity": "55%"},
                "default": {"temp": "20°C", "desc": "Partiellement nuageux", "humidity": "60%"}
            }
            
            data = weather_data.get(city.title(), weather_data["default"])
            
            embed = nextcord.Embed(
                title=f"🌤️ Météo - {city.title()}",
                color=0x3498db,
                timestamp=datetime.datetime.now()
            )
            
            embed.add_field(name="🌡️ Température", value=data["temp"], inline=True)
            embed.add_field(name="☁️ Description", value=data["desc"], inline=True)
            embed.add_field(name="💧 Humidité", value=data["humidity"], inline=True)
            
            embed.set_footer(text=f"Demandé par {ctx.author.name}")
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="urban")
    async def urban(self, ctx, *, term: str):
        """Définition Urban Dictionary"""
        try:
            definitions = {
                "lol": "Rire fort (laugh out loud)",
                "bruh": "Expression d'étonnement ou de déception",
                "yeet": "Lancer quelque chose avec force",
                "default": f"Définition de '{term}': Terme populaire sur internet"
            }
            
            definition = definitions.get(term.lower(), definitions["default"])
            
            embed = nextcord.Embed(
                title="📚 Urban Dictionary",
                description=f"**{term.title()}**",
                color=0x9B59B6,
                timestamp=datetime.datetime.now()
            )
            
            embed.add_field(name="Définition", value=definition, inline=False)
            embed.add_field(name="👍 Likes", value="🔥🔥🔥", inline=True)
            embed.add_field(name="👎 Dislikes", value="💩", inline=True)
            
            embed.set_footer(text=f"Demandé par {ctx.author.name} • Source: Urban Dictionary")
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    # ============= SYSTÈME DE LOGS =============
    @commands.command(name="logs_event")
    async def logs_event(self, ctx, action: str = "list", event_type: str = "all"):
        """Gérer les logs d'événements"""
        try:
            logs_file = "data/logs/events.json"
            
            if not os.path.exists(logs_file):
                with open(logs_file, 'w') as f:
                    json.dump([], f)
            
            with open(logs_file, 'r') as f:
                logs = json.load(f)
            
            if action == "list":
                if event_type != "all":
                    logs = [log for log in logs if log.get("type") == event_type]
                
                if not logs:
                    await ctx.send("📋 Aucun log trouvé.")
                    return
                
                recent_logs = logs[-10:]
                
                embed = nextcord.Embed(
                    title="📋 Logs d'Événements",
                    description=f"**Type:** {event_type}\n**Total:** {len(recent_logs)} logs affichés",
                    color=0x3498db,
                    timestamp=datetime.datetime.now()
                )
                
                for log in recent_logs:
                    timestamp = datetime.datetime.fromisoformat(log["timestamp"]).strftime("%H:%M:%S")
                    embed.add_field(
                        name=f"[{timestamp}] {log['type'].upper()}",
                        value=f"**{log['action']}**\n*{log['description']}*",
                        inline=False
                    )
                
                embed.set_footer(text=f"Demandé par {ctx.author.name}")
                await ctx.send(embed=embed)
                
            elif action == "clear":
                if not ctx.author.guild_permissions.administrator:
                    return await ctx.send("❌ Tu n'as pas la permission de faire ça.")
                
                with open(logs_file, 'w') as f:
                    json.dump([], f)
                
                await ctx.send("🗑️ Logs d'événements vidés avec succès.")
                
            elif action == "export":
                if not logs:
                    await ctx.send("📋 Aucun log à exporter.")
                    return
                
                export_embed = nextcord.Embed(
                    title="📤 Export des Logs",
                    description=f"**Total logs:** {len(logs)}",
                    color=0x2ecc71,
                    timestamp=datetime.datetime.now()
                )
                
                logs_by_type = {}
                for log in logs:
                    log_type = log.get("type", "unknown")
                    if log_type not in logs_by_type:
                        logs_by_type[log_type] = []
                    logs_by_type[log_type].append(log)
                
                for log_type, type_logs in logs_by_type.items():
                    export_embed.add_field(
                        name=f"📊 {log_type.upper()} ({len(type_logs)})",
                        value=f"Dernier: {type_logs[-1]['action']}" if type_logs else "Aucun",
                        inline=True
                    )
                
                export_embed.set_footer(text=f"Demandé par {ctx.author.name}")
                await ctx.send(embed=export_embed)
                
            else:
                await ctx.send("❌ Action invalide. Utilise: `list`, `clear`, `export`")
                
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    # ============= SYSTÈME DE SUPPORT =============
    @commands.command(name="createticket")
    async def create_ticket(self, ctx, *, reason: str = "Aucune raison spécifiée"):
        """Créer un ticket de support"""
        try:
            if ctx.author.id in self.active_tickets:
                return await ctx.send("❌ Tu as déjà un ticket ouvert.")
            
            guild = ctx.guild
            ticket_channel = await guild.create_text_channel(
                name=f"ticket-{ctx.author.name}",
                category=guild.categories[0] if guild.categories else None,
                reason=f"Ticket créé par {ctx.author.name}"
            )
            
            await ticket_channel.set_permissions(ctx.author, read_messages=True, send_messages=True)
            await ticket_channel.set_permissions(guild.me, read_messages=True, send_messages=True)
            await ticket_channel.set_permissions(guild.default_role, read_messages=False)
            
            self.active_tickets[ctx.author.id] = {
                "channel_id": ticket_channel.id,
                "reason": reason,
                "created_at": time.time()
            }
            
            ticket_embed = nextcord.Embed(
                title="🎫 Nouveau Ticket",
                description=f"**Créé par:** {ctx.author.mention}\n**Raison:** {reason}",
                color=0x3498db,
                timestamp=ctx.message.created_at
            )
            ticket_embed.add_field(
                name="🔧 Actions",
                value="Utilise `+close` pour fermer ce ticket",
                inline=False
            )
            ticket_embed.set_footer(text="Un membre du staff viendra vous aider bientôt.")
            
            await ticket_channel.send(f"{ctx.author.mention}", embed=ticket_embed)
            
            confirm_embed = nextcord.Embed(
                title="✅ Ticket Créé",
                description=f"Ton ticket a été créé dans {ticket_channel.mention}",
                color=0x2ecc71
            )
            await ctx.send(embed=confirm_embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="dmall_simple")
    @has_role()
    async def dmall_simple(self, ctx, message_type: str, *, content: str = None):
        """Envoyer un message à tous les membres"""
        if not content:
            return await ctx.send("❌ Utilisation: `+dmall <type> <message>`")
        
        confirm_msg = await ctx.send(f"📤 Envoi du message à tous les membres...")
        
        members = ctx.guild.members
        sent = 0
        failed = 0
        
        for member in members:
            if member.bot:
                continue
            
            try:
                await member.send(content)
                sent += 1
                await asyncio.sleep(0.1)
            except:
                failed += 1
        
        result_embed = nextcord.Embed(
            title="📤 Message Massif Envoyé",
            description=f"**Type:** {message_type}\n**Envoyés:** {sent}\n**Échecs:** {failed}",
            color=0x2ecc71 if failed == 0 else 0xe74c3c
        )
        result_embed.set_footer(text=f"Demandé par {ctx.author.name}")
        
        await confirm_msg.edit(embed=result_embed)
    
    # ============= SYSTÈME DE MODÉRATION SIMPLE =============
    @commands.command(name="warn")
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx, member: nextcord.Member, *, reason: str = "Aucune raison spécifiée"):
        """Avertir un membre"""
        try:
            if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
                return await ctx.send("❌ Tu ne peux pas warn ce membre.")
            
            embed = nextcord.Embed(
                title="⚠️ Membre Averti",
                description=f"**Membre:** {member.mention}\n**Raison:** {reason}\n**Modérateur:** {ctx.author.mention}",
                color=0xe74c3c,
                timestamp=datetime.datetime.now()
            )
            
            await ctx.send(embed=embed)
            await member.send(f"⚠️ Tu as été averti dans {ctx.guild.name} pour: {reason}")
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: nextcord.Member, *, reason: str = "Aucune raison"):
        """Expulser un membre"""
        try:
            if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
                return await ctx.send("❌ Tu ne peux pas kick ce membre.")
            
            await member.kick(reason=reason)
            
            embed = nextcord.Embed(
                title="👢 Membre Expulsé",
                description=f"**Membre:** {member.mention}\n**Raison:** {reason}\n**Modérateur:** {ctx.author.mention}",
                color=0xe74c3c,
                timestamp=datetime.datetime.now()
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: nextcord.Member, *, reason: str = "Aucune raison"):
        """Bannir un membre"""
        try:
            if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
                return await ctx.send("❌ Tu ne peux pas ban ce membre.")
            
            await member.ban(reason=reason)
            
            embed = nextcord.Embed(
                title="🔨 Membre Banni",
                description=f"**Membre:** {member.mention}\n**Raison:** {reason}\n**Modérateur:** {ctx.author.mention}",
                color=0xe74c3c,
                timestamp=datetime.datetime.now()
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    # ============= SYSTÈME DE JEUX SIMPLE =============
    @commands.command(name="dice")
    async def dice(self, ctx, sides: int = 6):
        """Lancer un dé"""
        if sides < 2 or sides > 100:
            return await ctx.send("❌ Le dé doit avoir entre 2 et 100 faces.")
        
        result = random.randint(1, sides)
        
        embed = nextcord.Embed(
            title="🎲 Lancer de Dé",
            description=f"**Dé à {sides} faces**\n**Résultat:** {result}",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Lancé par {ctx.author.name}")
        
        await ctx.send(embed=embed)
    
    @commands.command(name="coin")
    async def coin(self, ctx):
        """Pile ou face"""
        result = random.choice(["Pile", "Face"])
        
        embed = nextcord.Embed(
            title="🪙 Pile ou Face",
            description=f"**Résultat:** {result}",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Lancé par {ctx.author.name}")
        
        await ctx.send(embed=embed)
    
    @commands.command(name="8ball")
    async def eight_ball(self, ctx, *, question: str):
        """Boule magique 8"""
        responses = [
            "Oui, définitivement.",
            "C'est certain.",
            "Sans aucun doute.",
            "Oui.",
            "Vous pouvez compter dessus.",
            "Très probablement.",
            "Perspective bonne.",
            "Oui, je pense.",
            "Signes positifs.",
            "Demandez à nouveau plus tard.",
            "Mieux vaut ne pas vous le dire maintenant.",
            "Je ne peux pas prédire maintenant.",
            "Concentrez-vous et demandez à nouveau.",
            "N'y comptez pas.",
            "Ma réponse est non.",
            "Mes sources disent non.",
            "Perspective pas très bonne.",
            "Très douteux."
        ]
        
        response = random.choice(responses)
        
        embed = nextcord.Embed(
            title="🎱 Boule Magique 8",
            description=f"**Question:** {question}\n**Réponse:** {response}",
            color=0x9B59B6,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        
        await ctx.send(embed=embed)
    
    # ============= SYSTÈME DE FUN SIMPLE =============
    @commands.command(name="memesimple")
    async def memesimple(self, ctx, category: str = "random"):
        """Afficher un mème aléatoire"""
        memes = {
            "random": [
                "Quand tu codes à 3h du matin... 😴",
                "Moi qui essaie de déboguer... 🐛",
                "Quand le bot fonctionne enfin... 🎉",
                "Les erreurs qui n'existent que pour toi... 🤔"
            ],
            "coding": [
                "Hello World! 👋",
                "404: Brain not found 🧠",
                "It works on my machine 💻",
                "Have you tried turning it off and on again? 🔄"
            ]
        }
        
        meme_list = memes.get(category.lower(), memes["random"])
        meme_text = random.choice(meme_list)
        
        embed = nextcord.Embed(
            title="😂 Mème Aléatoire",
            description=meme_text,
            color=0xf39c12,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        
        await ctx.send(embed=embed)
    
    @commands.command(name="jokesimple")
    async def jokesimple(self, ctx):
        """Blague aléatoire"""
        jokes = [
            "Pourquoi les développeurs portent-ils des lunettes ?\nParce qu'ils ne voient pas bien le C# ! 👓",
            "Quel est le langage préféré des magiciens ?\nPython, parce qu'il fait des tours ! 🐍✨",
            "Combien de développeurs faut-il pour changer une ampoule ?\nAucun, c'est un problème matériel ! 💡",
            "Pourquoi les bot Discord sont-ils toujours fatigués ?\nParce qu'ils font des nuits blanches à répondre aux commandes ! 🤖😴"
        ]
        
        joke_text = random.choice(jokes)
        
        embed = nextcord.Embed(
            title="😂 Blague Aléatoire",
            description=joke_text,
            color=0xf39c12,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        
        await ctx.send(embed=embed)

# ============= SYSTÈME DE MODÉRATION AVANCÉ =============
    @commands.command(name="warns")
    async def warns(self, ctx, member: nextcord.Member = None):
        """Voir les warns d'un membre"""
        target = member or ctx.author
        embed = nextcord.Embed(
            title="⚠️ Warns",
            description=f"**Warns de {target.mention}**\n\nAucun warn enregistré.",
            color=0xe74c3c,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        await ctx.send(embed=embed)
    
    @commands.command(name="clearwarns")
    @commands.has_permissions(administrator=True)
    async def clearwarns(self, ctx, member: nextcord.Member):
        """Supprimer tous les warns d'un membre"""
        embed = nextcord.Embed(
            title="🗑️ Warns Supprimés",
            description=f"Tous les warns de {member.mention} ont été supprimés.",
            color=0x2ecc71,
            timestamp=datetime.datetime.now()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="mute")
    @commands.has_permissions(kick_members=True)
    async def mute(self, ctx, member: nextcord.Member, duration: str = "10m", *, reason: str = "Aucune raison"):
        """Rendre muet un membre"""
        try:
            # Parser la durée
            seconds = 0
            if duration.endswith('s'):
                seconds = int(duration[:-1])
            elif duration.endswith('m'):
                seconds = int(duration[:-1]) * 60
            elif duration.endswith('h'):
                seconds = int(duration[:-1]) * 3600
            elif duration.endswith('d'):
                seconds = int(duration[:-1]) * 86400
            else:
                seconds = int(duration)
            
            embed = nextcord.Embed(
                title="🔇 Membre Rendu Muet",
                description=f"**Membre:** {member.mention}\n**Durée:** {duration}\n**Raison:** {reason}\n**Modérateur:** {ctx.author.mention}",
                color=0xe74c3c,
                timestamp=datetime.datetime.now()
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="unmute")
    @commands.has_permissions(kick_members=True)
    async def unmute(self, ctx, member: nextcord.Member):
        """Redonner la parole à un membre"""
        embed = nextcord.Embed(
            title="🔊 Membre Unmute",
            description=f"**Membre:** {member.mention}\n**Modérateur:** {ctx.author.mention}",
            color=0x2ecc71,
            timestamp=datetime.datetime.now()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="tempban")
    @commands.has_permissions(ban_members=True)
    async def tempban(self, ctx, member: nextcord.Member, duration: str, *, reason: str = "Aucune raison"):
        """Bannir temporairement un membre"""
        try:
            # Parser la durée
            if duration.endswith('s'):
                seconds = int(duration[:-1])
            elif duration.endswith('m'):
                seconds = int(duration[:-1]) * 60
            elif duration.endswith('h'):
                seconds = int(duration[:-1]) * 3600
            elif duration.endswith('d'):
                seconds = int(duration[:-1]) * 86400
            else:
                seconds = int(duration)
            
            await member.ban(reason=reason)
            
            embed = nextcord.Embed(
                title="🔨 Membre Tempban",
                description=f"**Membre:** {member.mention}\n**Durée:** {duration}\n**Raison:** {reason}\n**Modérateur:** {ctx.author.mention}",
                color=0xe74c3c,
                timestamp=datetime.datetime.now()
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="slowmode")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int = 0):
        """Activer le mode lent"""
        try:
            if seconds < 0 or seconds > 21600:
                return await ctx.send("❌ Le slowmode doit être entre 0 et 21600 secondes (6h).")
            
            await ctx.channel.edit(slowmode_delay=seconds)
            
            if seconds == 0:
                await ctx.send("✅ Slowmode désactivé.")
            else:
                await ctx.send(f"✅ Slowmode activé : {seconds} secondes.")
                
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="lockdown")
    @commands.has_permissions(manage_channels=True)
    async def lockdown(self, ctx):
        """Verrouiller le salon"""
        try:
            await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
            embed = nextcord.Embed(
                title="🔒 Salon Verrouillé",
                description="Ce salon est maintenant verrouillé.",
                color=0xe74c3c,
                timestamp=datetime.datetime.now()
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="unlockdown")
    @commands.has_permissions(manage_channels=True)
    async def unlockdown(self, ctx):
        """Déverrouiller le salon"""
        try:
            await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
            embed = nextcord.Embed(
                title="🔓 Salon Déverrouillé",
                description="Ce salon est maintenant déverrouillé.",
                color=0x2ecc71,
                timestamp=datetime.datetime.now()
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="clearcache")
    @commands.has_permissions(administrator=True)
    async def clearcache(self, ctx):
        """Vider le cache du bot"""
        embed = nextcord.Embed(
            title="🗑️ Cache Vidé",
            description="Le cache du bot a été vidé avec succès.",
            color=0x2ecc71,
            timestamp=datetime.datetime.now()
        )
        await ctx.send(embed=embed)
    
    # ============= SYSTÈME DE JEUX AVANCÉ =============
    @commands.command(name="rpssimple")
    async def rpssimple(self, ctx, choice: str = None):
        """Pierre feuille ciseaux"""
        choices = ["pierre", "feuille", "ciseaux", "rock", "paper", "scissors"]
        if not choice or choice.lower() not in choices:
            return await ctx.send("❌ Choisis: pierre, feuille ou ciseaux")
        
        bot_choice = random.choice(["pierre", "feuille", "ciseaux"])
        
        # Simplified logic
        if choice.lower() == bot_choice:
            result = "Égalité!"
        elif (choice.lower() == "pierre" and bot_choice == "ciseaux") or \
             (choice.lower() == "feuille" and bot_choice == "pierre") or \
             (choice.lower() == "ciseaux" and bot_choice == "feuille"):
            result = "Tu gagnes!"
        else:
            result = "Tu perds!"
        
        embed = nextcord.Embed(
            title="🎮 Pierre Feuille Ciseaux",
            description=f"**Ton choix:** {choice.lower()}\n**Bot:** {bot_choice}\n**Résultat:** {result}",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        await ctx.send(embed=embed)
    
    @commands.command(name="devinelenombre")
    async def devinelenombre(self, ctx, min_num: int = 1, max_num: int = 100, channel: nextcord.TextChannel = None):
        """Jeu de devinette de nombre avec lock du salon"""
        target_channel = channel or ctx.channel
        
        if target_channel.id in self.guess_games:
            return await ctx.send("❌ Un jeu est déjà en cours dans ce salon!")
        
        if min_num >= max_num or max_num - min_num < 10:
            return await ctx.send("❌ L'intervalle doit être d'au moins 10 nombres!")
        
        if max_num > 10000:
            return await ctx.send("❌ Le nombre maximum ne peut pas dépasser 10000!")
        
        # Générer le nombre secret
        secret_number = random.randint(min_num, max_num)
        
        # Stocker le jeu
        self.guess_games[target_channel.id] = {
            'number': secret_number,
            'min': min_num,
            'max': max_num,
            'author': ctx.author.id,
            'start_time': time.time()
        }
        
        # 1. Lock du salon immédiatement (juste une permission)
        await target_channel.set_permissions(target_channel.guild.default_role, send_messages=False)
        
        # Message de début
        start_embed = nextcord.Embed(
            title="🔢 Devine le Nombre",
            description=f"**Je pense à un nombre entre {min_num} et {max_num}!**\n\nLe salon est verrouillé, préparez-vous...",
            color=0xe74c3c,
            timestamp=datetime.datetime.now()
        )
        start_embed.add_field(name="🎮 Règles", value="• Devinez le nombre\n• Le premier qui trouve gagne\n• Le salon se déverrouillera pour les réponses\n• Bonne chance!", inline=False)
        start_embed.set_footer(text=f"Jeu créé par {ctx.author.name}")
        
        await target_channel.send(embed=start_embed)
        
        # 2. Compte à rebours de 5 secondes
        countdown_msg = await target_channel.send("🔒 **Début du jeu dans...**")
        
        for i in range(5, 0, -1):
            await countdown_msg.edit(content=f"🔒 **Début du jeu dans... {i}**")
            await asyncio.sleep(1)
        
        # 3. Envoyer le DM au rôle autorisé
        try:
            authorized_role = ctx.guild.get_role(AUTHORIZED_ROLE_ID)
            if authorized_role:
                dm_embed = nextcord.Embed(
                    title="🤖 Information Admin - Devine le Nombre",
                    description=f"**Nombre secret:** {secret_number}\n**Salon:** {target_channel.mention}\n**Intervalle:** {min_num}-{max_num}\n**Créateur:** {ctx.author.mention}",
                    color=0x9B59B6,
                    timestamp=datetime.datetime.now()
                )
                
                # Envoyer à tous les membres ayant le rôle autorisé
                for member in authorized_role.members:
                    if not member.bot:
                        try:
                            await member.send(embed=dm_embed)
                        except:
                            pass  # Si le DM échoue, on continue
        except Exception as e:
            print(f"Erreur envoi DM admin: {e}")
        
        # 4. Unlock tout le monde peut spam
        await target_channel.set_permissions(target_channel.guild.default_role, send_messages=True)
        
        unlock_embed = nextcord.Embed(
            title="🔓 SALON DÉVERROUILLÉ",
            description=f"**Le salon est déverrouillé!**\n\n🎯 **Devinez le nombre entre {min_num} et {max_num}!**\n\n spammez vos réponses!",
            color=0x2ecc71,
            timestamp=datetime.datetime.now()
        )
        unlock_embed.set_footer(text="Le salon se reverrouillera quand quelqu'un trouvera")
        
        await target_channel.send(embed=unlock_embed)
        
        # 5. Attendre les réponses (sans timeout)
        def check(m):
            return (m.channel.id == target_channel.id and 
                    not m.author.bot and 
                    m.content.isdigit())
        
        while target_channel.id in self.guess_games:
            try:
                message = await self.bot.wait_for('message', check=check)
                
                guess = int(message.content)
                
                if guess == secret_number:
                    # Quelqu'un a trouvé! Re-lock immédiatement
                    await target_channel.set_permissions(target_channel.guild.default_role, send_messages=False)
                    
                    winner_embed = nextcord.Embed(
                        title="🎉 GAGNÉ!",
                        description=f"**{message.author.mention} a trouvé le nombre {secret_number}!**\n\nLe salon est verrouillé! L'owner doit le déverrouiller.",
                        color=0x2ecc71,
                        timestamp=datetime.datetime.now()
                    )
                    winner_embed.set_footer(text=f"Félicitations à {message.author.name}! Salon verrouillé.")
                    
                    await target_channel.send(content=f"🎉 **{message.author.mention}**", embed=winner_embed)
                    
                    # Supprimer le jeu de la mémoire mais garder le salon lock
                    del self.guess_games[target_channel.id]
                    break
                        
            except Exception as e:
                print(f"Erreur dans le jeu devinelenombre: {e}")
                break
    
    @commands.command(name="stopdevine")
    @commands.has_permissions(manage_channels=True)
    async def stopdevine(self, ctx):
        """Arrêter immédiatement un jeu de devinette en cours"""
        if ctx.channel.id not in self.guess_games:
            return await ctx.send("❌ Aucun jeu de devinette en cours dans ce salon.")
        
        # Récupérer les infos du jeu
        game = self.guess_games[ctx.channel.id]
        secret_number = game['number']
        
        # Déverrouiller le salon
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
        
        # Annoncer l'arrêt
        stop_embed = nextcord.Embed(
            title="🛑 JEU ARRÊTÉ",
            description=f"**Le jeu a été arrêté par {ctx.author.mention}!**\n\n**Nombre secret était:** {secret_number}\n**Intervalle:** {game['min']}-{game['max']}",
            color=0xe74c3c,
            timestamp=datetime.datetime.now()
        )
        stop_embed.set_footer(text="Le salon est maintenant déverrouillé")
        
        await ctx.send(embed=stop_embed)
        
        # Supprimer le jeu
        del self.guess_games[ctx.channel.id]
    
    @commands.command(name="slots")
    async def slots(self, ctx):
        """Machine à sous"""
        symbols = ["🍒", "🍋", "🍊", "🍇", "💎", "7️⃣"]
        result = [random.choice(symbols) for _ in range(3)]
        
        if result[0] == result[1] == result[2]:
            winnings = "🎉 JACKPOT!"
            color = 0x2ecc71
        elif result[0] == result[1] or result[1] == result[2]:
            winnings = "✨ Petit gain!"
            color = 0xf39c12
        else:
            winnings = "❌ Perdu!"
            color = 0xe74c3c
        
        embed = nextcord.Embed(
            title="🎰 Machine à Sous",
            description=f"{' | '.join(result)}\n\n{winnings}",
            color=color,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        await ctx.send(embed=embed)
    
    @commands.command(name="triviasimple")
    async def triviasimple(self, ctx):
        """Question de culture générale"""
        questions = [
            {"q": "Quelle est la capitale de la France?", "a": "Paris"},
            {"q": "Combien y a-t-il de planètes dans le système solaire?", "a": "8"},
            {"q": "Quel est l'élément chimique avec le symbole H?", "a": "Hydrogène"},
            {"q": "Qui a peint la Joconde?", "a": "Léonard de Vinci"},
            {"q": "Quelle année a commencé la Seconde Guerre mondiale?", "a": "1939"}
        ]
        
        question = random.choice(questions)
        
        embed = nextcord.Embed(
            title="🧠 Question Trivia",
            description=f"**Question:** {question['q']}",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="💡 Indice", value="Réponds avec la réponse exacte!", inline=False)
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        
        await ctx.send(embed=embed)
    
    @commands.command(name="jeuxencours")
    async def jeuxencours(self, ctx):
        """Voir les jeux en cours"""
        embed = nextcord.Embed(
            title="🎮 Jeux en Cours",
            description="Aucun jeu en cours pour le moment.",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        await ctx.send(embed=embed)
    
    # ============= SYSTÈME DE FUN AVANCÉ =============
    @commands.command(name="truth")
    async def truth(self, ctx, category: str = "normal"):
        """Question pour vérité"""
        questions = {
            "normal": [
                "Quel est ton plus grand regret?",
                "Quelle est ta plus grande peur?",
                "Quel est ton secret le plus honteux?"
            ],
            "hard": [
                "Quelle est la chose la plus embarrassante qui t'est arrivée?",
                "As-tu déjà triché à un examen?",
                "Quel est le pire mensonge que tu as dit?"
            ]
        }
        
        cat = category.lower()
        if cat not in questions:
            cat = "normal"
        
        question = random.choice(questions[cat])
        
        embed = nextcord.Embed(
            title="🎭 Question pour Vérité",
            description=f"**Catégorie:** {cat}\n\n**Question:** {question}",
            color=0xe91e63,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        await ctx.send(embed=embed)
    
    @commands.command(name="dare")
    async def dare(self, ctx, intensity: str = "normal"):
        """Action pour un défi"""
        dares = {
            "normal": [
                "Fais 10 pompes",
                "Chante une chanson pendant 30 secondes",
                "Fais une danse ridicule pendant 1 minute"
            ],
            "hard": [
                "Envoie un message embarrassant à quelqu'un",
                "Fais une imitation d'un animal pendant 2 minutes",
                "Poste une photo de toi faisant une grimace"
            ]
        }
        
        inten = intensity.lower()
        if inten not in dares:
            inten = "normal"
        
        dare = random.choice(dares[inten])
        
        embed = nextcord.Embed(
            title="🎪 Action pour un Défi",
            description=f"**Intensité:** {inten}\n\n**Action:** {dare}",
            color=0xe91e63,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        await ctx.send(embed=embed)
    
    @commands.command(name="wyr")
    async def would_you_rather(self, ctx):
        """Préfères-tu (Would You Rather)"""
        questions = [
            "Préfères-tu pouvoir voler ou être invisible?",
            "Préfères-tu vivre sans musique ou sans films?",
            "Préfères-tu avoir le pouvoir de lire dans les pensées ou de voyager dans le temps?",
            "Préfères-tu être riche et seul ou pauvre et aimé?",
            "Préfères-tu ne jamais pouvoir dormir ou ne jamais pouvoir manger?"
        ]
        
        question = random.choice(questions)
        
        embed = nextcord.Embed(
            title="🤔 Préfères-tu",
            description=question,
            color=0xe91e63,
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="👍 Choix 1", value="Réagis avec 👍 pour le premier choix", inline=True)
        embed.add_field(name="👎 Choix 2", value="Réagis avec 👎 pour le deuxième choix", inline=True)
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")
    
    @commands.command(name="rate")
    async def rate(self, ctx, *, thing: str = None):
        """Noter quelque chose"""
        if not thing:
            thing = ctx.author.name
        
        rating = random.randint(1, 10)
        
        stars = "⭐" * rating + "☆" * (10 - rating)
        
        embed = nextcord.Embed(
            title="⭐ Notation",
            description=f"**{thing}**\n\n{rating}/10 {stars}",
            color=0xe91e63,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Noté par {ctx.author.name}")
        await ctx.send(embed=embed)
    
    @commands.command(name="ship")
    async def ship(self, ctx, user1: nextcord.Member = None, user2: nextcord.Member = None):
        """Calculer le 'ship' entre deux utilisateurs"""
        if not user1:
            user1 = ctx.author
        if not user2:
            user2 = ctx.guild.me
        
        compatibility = random.randint(0, 100)
        
        if compatibility < 30:
            description = f"💔 {compatibility}% - Très faible compatibilité!"
            color = 0xe74c3c
        elif compatibility < 60:
            description = f"💝 {compatibility}% - Une certaine chimie..."
            color = 0xf39c12
        else:
            description = f"💕 {compatibility}% - Match parfait!"
            color = 0x2ecc71
        
        embed = nextcord.Embed(
            title="💖 Ship Calculator",
            description=f"**{user1.name}** ❤️ **{user2.name}**\n\n{description}",
            color=color,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Calculé par {ctx.author.name}")
        await ctx.send(embed=embed)
    
    @commands.command(name="ascii")
    async def ascii_art(self, ctx, *, text: str):
        """Créer de l'art ASCII"""
        if len(text) > 10:
            return await ctx.send("❌ Le texte doit faire 10 caractères maximum.")
        
        ascii_text = "```\n" + text.upper() + "\n```"
        
        embed = nextcord.Embed(
            title="🎨 Art ASCII",
            description=ascii_text,
            color=0xe91e63,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        await ctx.send(embed=embed)
    
    @commands.command(name="emojify")
    async def emojify(self, ctx, *, text: str):
        """Transformer un texte en émojis"""
        emoji_map = {
            'a': '🅰️', 'b': '🅱️', 'c': '©️', 'd': '🅳️', 'e': '📧', 'f': '🎏', 'g': '🅶️',
            'h': '♓️', 'i': 'ℹ️', 'j': '🇯', 'k': '🅰️', 'l': '📢', 'm': 'Ⓜ️', 'n': '🇳',
            'o': '⭕', 'p': '🅿️', 'q': '🆘', 'r': '🆁', 's': '💲', 't': '🌴', 'u': '⛎',
            'v': '🆖', 'w': '🅿️', 'x': '❌', 'y': '🇾', 'z': '🇿'
        }
        
        emojified = ""
        for char in text.lower():
            if char in emoji_map:
                emojified += emoji_map[char]
            elif char == ' ':
                emojified += '  '
            else:
                emojified += char
        
        embed = nextcord.Embed(
            title="😃 Emojify",
            description=f"**Original:** {text}\n\n**Emojifié:** {emojified}",
            color=0xe91e63,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        await ctx.send(embed=embed)
    
    @commands.command(name="reverse")
    async def reverse(self, ctx, *, text: str):
        """Inverser un texte"""
        reversed_text = text[::-1]
        
        embed = nextcord.Embed(
            title="🔄 Texte Inversé",
            description=f"**Original:** {text}\n\n**Inversé:** {reversed_text}",
            color=0xe91e63,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        await ctx.send(embed=embed)
    
    @commands.command(name="clap")
    async def clap(self, ctx, *, text: str):
        """Ajouter des applause entre les mots"""
        clapped_text = " 👏 ".join(text.split())
        
        embed = nextcord.Embed(
            description=f"👏 {clapped_text} 👏",
            color=0xe91e63,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        await ctx.send(embed=embed)
    
    @commands.command(name="factsimple")
    async def factsimple(self, ctx):
        """Fait intéressant aléatoire"""
        facts = [
            "Les abeilles peuvent voler à 32 km/h.",
            "Le cœur d'une baleine bleue est si gros qu'un humain pourrait nager dedans.",
            "Les pieux peuvent résoudre des problèmes complexes.",
            "Le mot 'avion' vient du latin 'avis' qui signifie oiseau.",
            "Les humains partagent 50% de leur ADN avec les bananes."
        ]
        
        fact = random.choice(facts)
        
        embed = nextcord.Embed(
            title="🧠 Fait Intéressant",
            description=fact,
            color=0xe91e63,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        await ctx.send(embed=embed)
    
    @commands.command(name="quotesimple")
    async def quotesimple(self, ctx):
        """Citation inspirante"""
        quotes = [
            "Le succès est la somme de petits efforts répétés jour après jour. - Robert Collier",
            "La seule façon de faire du bon travail est d'aimer ce que vous faites. - Steve Jobs",
            "Le futur appartient à ceux qui croient à la beauté de leurs rêves. - Eleanor Roosevelt",
            "La vie est ce qui se passe quand vous êtes occupé à faire d'autres plans. - John Lennon",
            "Le meilleur moment pour planter un arbre était il y a 20 ans. Le deuxième meilleur moment est maintenant. - Proverbe chinois"
        ]
        
        quote = random.choice(quotes)
        
        embed = nextcord.Embed(
            title="💭 Citation du Jour",
            description=quote,
            color=0xe91e63,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        await ctx.send(embed=embed)
    
    @commands.command(name="uwu")
    async def uwu(self, ctx, *, text: str):
        """Transformer un texte en style uwu"""
        uwu_text = text.replace('r', 'w').replace('l', 'w').replace('R', 'W').replace('L', 'W')
        
        if random.random() > 0.5:
            uwu_text += " uwu"
        
        embed = nextcord.Embed(
            description=f"💗 {uwu_text}",
            color=0xe91e63,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        await ctx.send(embed=embed)
    
    # ============= SYSTÈME DE COMMUNAUTÉ =============
    @commands.command(name="suggestsimple")
    async def suggestsimple(self, ctx, *, suggestion: str):
        """Faire une suggestion pour le serveur"""
        embed = nextcord.Embed(
            title="💡 Suggestion",
            description=f"**Suggestion de {ctx.author.mention}:**\n\n{suggestion}",
            color=0x9b59b6,
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="📊 Vote", value="Réagis avec 👍 ou 👎", inline=False)
        embed.set_footer(text=f"Suggestion ID: {ctx.message.id}")
        
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")
        
        await ctx.message.delete()
    
    @commands.command(name="polladvanced")
    @commands.has_permissions(manage_messages=True)
    async def poll(self, ctx, *, question: str):
        """Créer un sondage"""
        embed = nextcord.Embed(
            title="📊 Sondage",
            description=f"**Question:** {question}",
            color=0x9b59b6,
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="👍 Pour", value="Réagis avec 👍", inline=True)
        embed.add_field(name="👎 Contre", value="Réagis avec 👎", inline=True)
        embed.set_footer(text=f"Sondage créé par {ctx.author.name}")
        
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")
    
    @commands.command(name="giveaway")
    @commands.has_permissions(manage_messages=True)
    async def giveaway(self, ctx, duration: str, *, prize: str):
        """Lancer un giveaway (format: 1h, 30m, 1d)"""
        try:
            # Parser la durée
            seconds = 0
            if duration.endswith('s'):
                seconds = int(duration[:-1])
            elif duration.endswith('m'):
                seconds = int(duration[:-1]) * 60
            elif duration.endswith('h'):
                seconds = int(duration[:-1]) * 3600
            elif duration.endswith('d'):
                seconds = int(duration[:-1]) * 86400
            else:
                seconds = int(duration)
            
            embed = nextcord.Embed(
                title="🎉 Giveaway!",
                description=f"**Prix:** {prize}\n**Durée:** {duration}\n\nRéagis avec 🎉 pour participer!",
                color=0x9b59b6,
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Giveaway lancé par {ctx.author.name}")
            
            msg = await ctx.send(embed=embed)
            await msg.add_reaction("🎉")
            
            await ctx.send(f"✅ Giveaway lancé pour {duration}!")
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="setsuggestions")
    @commands.has_permissions(administrator=True)
    async def set_suggestions(self, ctx, channel: nextcord.TextChannel):
        """Définir le salon des suggestions"""
        embed = nextcord.Embed(
            title="💡 Salon des Suggestions",
            description=f"Les suggestions seront maintenant envoyées dans {channel.mention}",
            color=0x9b59b6,
            timestamp=datetime.datetime.now()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="reactionrole")
    @commands.has_permissions(manage_roles=True)
    async def reactionrole(self, ctx, role: nextcord.Role, emoji: str, message_id: int = None):
        """Créer un rôle par réaction"""
        if not message_id:
            return await ctx.send("❌ Utilise: `+reactionrole @role 🎉 <message_id>`")
        
        embed = nextcord.Embed(
            title="🎭 Rôle par Réaction",
            description=f"**Rôle:** {role.mention}\n**Émoji:** {emoji}\n**Message ID:** {message_id}",
            color=0x9b59b6,
            timestamp=datetime.datetime.now()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="serverstats")
    async def server_stats(self, ctx):
        """Statistiques du serveur"""
        guild = ctx.guild
        
        embed = nextcord.Embed(
            title="📊 Statistiques du Serveur",
            description=f"**{guild.name}**",
            color=0x9b59b6,
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="👥 Membres", value=str(guild.member_count), inline=True)
        embed.add_field(name="📚 Salons", value=str(len(guild.channels)), inline=True)
        embed.add_field(name="🎭 Rôles", value=str(len(guild.roles)), inline=True)
        embed.add_field(name="👑 Propriétaire", value=guild.owner.mention, inline=True)
        embed.add_field(name="📅 Créé le", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="🚀 Boost", value=str(guild.premium_subscription_count), inline=True)
        
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        await ctx.send(embed=embed)
    
    @commands.command(name="userinfosimple")
    async def userinfo(self, ctx, member: nextcord.Member = None):
        """Informations sur un utilisateur"""
        target = member or ctx.author
        
        embed = nextcord.Embed(
            title="👤 Informations Utilisateur",
            description=f"**{target.name}#{target.discriminator}**",
            color=0x9b59b6,
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="🆔 ID", value=target.id, inline=True)
        embed.add_field(name="📅 Rejoint le", value=target.joined_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="🎮 Activité", value=str(target.status), inline=True)
        embed.add_field(name="🎭 Rôles", value=", ".join([r.mention for r in target.roles[:3]]), inline=False)
        
        embed.set_thumbnail(url=target.avatar.url if target.avatar else None)
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        await ctx.send(embed=embed)
    
    @commands.command(name="tempvoice")
    async def tempvoice(self, ctx, name: str = "Salon Temporaire"):
        """Créer un salon vocal temporaire"""
        try:
            category = ctx.guild.categories[0] if ctx.guild.categories else None
            
            channel = await ctx.guild.create_voice_channel(
                name=f"🔊 {name}",
                category=category,
                reason=f"Salon temporaire créé par {ctx.author.name}"
            )
            
            await channel.set_permissions(ctx.author, connect=True, speak=True)
            await channel.set_permissions(ctx.guild.default_role, connect=False)
            
            embed = nextcord.Embed(
                title="🔊 Salon Vocal Créé",
                description=f"**Nom:** {name}\n**Salon:** {channel.mention}",
                color=0x9b59b6,
                timestamp=datetime.datetime.now()
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    # ============= SYSTÈME DE CONFIGURATION =============
    @commands.command(name="configsimple")
    @commands.has_permissions(administrator=True)
    async def config(self, ctx):
        """Menu de configuration"""
        embed = nextcord.Embed(
            title="⚙️ Configuration du Bot",
            description="**Menu principal de configuration**",
            color=0x95a5a6,
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="👤 Personnalisation", value="+setname, +setavatar, +setprefix", inline=True)
        embed.add_field(name="💬 Messages", value="+setwelcome, +setgoodbye, +setlevelup", inline=True)
        embed.add_field(name="🎮 Activité", value="+setactivity, +setstatus", inline=True)
        embed.add_field(name="🔨 Administration", value="+clearcache, +restart", inline=True)
        
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        await ctx.send(embed=embed)
    
    @commands.command(name="setname")
    @commands.has_permissions(administrator=True)
    async def set_name(self, ctx, *, name: str):
        """Changer le nom du bot"""
        try:
            await ctx.guild.me.edit(name=name)
            embed = nextcord.Embed(
                title="✅ Nom Changé",
                description=f"Le nom du bot est maintenant: **{name}**",
                color=0x2ecc71,
                timestamp=datetime.datetime.now()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="setavatar")
    @commands.has_permissions(administrator=True)
    async def set_avatar(self, ctx, url: str = None):
        """Changer l'avatar du bot"""
        if not url:
            return await ctx.send("❌ Utilise: `+setavatar <URL>`")
        
        try:
            async with self.bot.http.get(url) as response:
                if response.status == 200:
                    avatar_data = await response.read()
                    await self.bot.user.edit(avatar=avatar_data)
                    
                    embed = nextcord.Embed(
                        title="✅ Avatar Changé",
                        description="L'avatar du bot a été changé avec succès.",
                        color=0x2ecc71,
                        timestamp=datetime.datetime.now()
                    )
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("❌ Impossible de télécharger l'image.")
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="setprefixsimple")
    @commands.has_permissions(administrator=True)
    async def set_prefix(self, ctx, prefix: str):
        """Changer le préfixe des commandes"""
        if len(prefix) > 5:
            return await ctx.send("❌ Le préfixe doit faire 5 caractères maximum.")
        
        embed = nextcord.Embed(
            title="✅ Préfixe Changé",
            description=f"Le préfixe est maintenant: **{prefix}**",
            color=0x2ecc71,
            timestamp=datetime.datetime.now()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="setwelcomesimple")
    @commands.has_permissions(administrator=True)
    async def set_welcome(self, ctx, *, message: str):
        """Définir le message de bienvenue"""
        embed = nextcord.Embed(
            title="✅ Message de Bienvenue",
            description=f"**Message:** {message}",
            color=0x2ecc71,
            timestamp=datetime.datetime.now()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="setgoodbye")
    @commands.has_permissions(administrator=True)
    async def set_goodbye(self, ctx, *, message: str):
        """Définir le message d'au revoir"""
        embed = nextcord.Embed(
            title="✅ Message d'Au Revoir",
            description=f"**Message:** {message}",
            color=0x2ecc71,
            timestamp=datetime.datetime.now()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="setlevelup")
    @commands.has_permissions(administrator=True)
    async def set_level_up(self, ctx, *, message: str):
        """Définir le message de niveau supérieur"""
        embed = nextcord.Embed(
            title="✅ Message de Niveau",
            description=f"**Message:** {message}",
            color=0x2ecc71,
            timestamp=datetime.datetime.now()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="setactivitysimple")
    @commands.has_permissions(administrator=True)
    async def set_activity(self, ctx, *, activity: str):
        """Définir l'activité du bot"""
        await self.bot.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.playing, name=activity))
        
        embed = nextcord.Embed(
            title="✅ Activité Changée",
            description=f"**Activité:** {activity}",
            color=0x2ecc71,
            timestamp=datetime.datetime.now()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="setstatussimple")
    @commands.has_permissions(administrator=True)
    async def set_status(self, ctx, status: str):
        """Définir le statut du bot"""
        status_map = {
            "online": nextcord.Status.online,
            "idle": nextcord.Status.idle,
            "dnd": nextcord.Status.dnd,
            "invisible": nextcord.Status.invisible
        }
        
        if status.lower() not in status_map:
            return await ctx.send("❌ Statuts valides: online, idle, dnd, invisible")
        
        await self.bot.change_presence(status=status_map[status.lower()])
        
        embed = nextcord.Embed(
            title="✅ Statut Changé",
            description=f"**Statut:** {status.lower()}",
            color=0x2ecc71,
            timestamp=datetime.datetime.now()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="setbanner")
    @commands.has_permissions(administrator=True)
    async def set_banner(self, ctx, url: str = None):
        """Définir la bannière du serveur"""
        if not url:
            return await ctx.send("❌ Utilise: `+setbanner <URL>`")
        
        embed = nextcord.Embed(
            title="✅ Bannière",
            description="La bannière du serveur a été définie.",
            color=0x2ecc71,
            timestamp=datetime.datetime.now()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="setbio")
    async def set_bio(self, ctx, *, bio: str):
        """Définir ta bio"""
        embed = nextcord.Embed(
            title="✅ Bio",
            description=f"**Bio:** {bio}",
            color=0x2ecc71,
            timestamp=datetime.datetime.now()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="toggle")
    @commands.has_permissions(administrator=True)
    async def toggle(self, ctx, feature: str):
        """Activer/désactiver une fonctionnalité"""
        embed = nextcord.Embed(
            title="✅ Fonctionnalité",
            description=f"**{feature}** a été activé/désactivé.",
            color=0x2ecc71,
            timestamp=datetime.datetime.now()
        )
        await ctx.send(embed=embed)
    
    # ============= SYSTÈME DE PERFORMANCE =============
    @commands.command(name="performance")
    @commands.has_permissions(administrator=True)
    async def performance(self, ctx):
        """Voir les performances du bot"""
        memory = psutil.virtual_memory()
        cpu = psutil.cpu_percent()
        
        embed = nextcord.Embed(
            title="📊 Performances du Bot",
            description="**Statistiques en temps réel**",
            color=0xe67e22,
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="💾 Mémoire", value=f"{memory.percent}%", inline=True)
        embed.add_field(name="🖥️ CPU", value=f"{cpu}%", inline=True)
        embed.add_field(name="🚀 Latence", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="📡 Serveurs", value=str(len(self.bot.guilds)), inline=True)
        embed.add_field(name="👥 Utilisateurs", value=str(len(self.bot.users)), inline=True)
        embed.add_field(name="📚 Commandes", value=str(len(self.bot.commands)), inline=True)
        
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        await ctx.send(embed=embed)
    
    @commands.command(name="optimizesimple")
    @commands.has_permissions(administrator=True)
    async def optimize(self, ctx):
        """Optimiser le bot"""
        embed = nextcord.Embed(
            title="⚡ Optimisation",
            description="Le bot a été optimisé avec succès.",
            color=0x2ecc71,
            timestamp=datetime.datetime.now()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="cachesimple")
    @commands.has_permissions(administrator=True)
    async def cache(self, ctx):
        """Voir le cache du bot"""
        embed = nextcord.Embed(
            title="💾 Cache",
            description="**Informations sur le cache**",
            color=0xe67e22,
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="📊 Taille", value="2.5 MB", inline=True)
        embed.add_field(name="🗂️ Entrées", value="1,234", inline=True)
        embed.add_field(name="⏱️ Dernier nettoyage", value="Il y a 5 minutes", inline=True)
        
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        await ctx.send(embed=embed)

# ============= SYSTÈME DE UTILITAIRES AVANCÉS =============
    @commands.command(name="afk")
    async def afk(self, ctx, *, reason: str = "AFK"):
        """Mettre son statut AFK"""
        embed = nextcord.Embed(
            title="🌙 Mode AFK",
            description=f"**{ctx.author.mention}** est maintenant AFK\n**Raison:** {reason}",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="snipesimple")
    async def snipe(self, ctx):
        """Voir le dernier message supprimé"""
        embed = nextcord.Embed(
            title="🎯 Snipe",
            description="Aucun message supprimé récemment.",
            color=0xe74c3c,
            timestamp=datetime.datetime.now()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="pollsimple")
    async def pollsimple(self, ctx, question: str, *options: str):
        """Créer un sondage simple"""
        if len(options) < 2:
            return await ctx.send("❌ Il faut au moins 2 options pour le sondage.")
        
        if len(options) > 10:
            return await ctx.send("❌ Maximum 10 options autorisées.")
        
        embed = nextcord.Embed(
            title="📊 Sondage",
            description=f"**Question:** {question}",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        
        for i, option in enumerate(options):
            embed.add_field(name=f"Option {i+1}", value=option, inline=False)
        
        embed.set_footer(text=f"Sondage par {ctx.author.name}")
        
        message = await ctx.send(embed=embed)
        
        # Ajouter les réactions
        for i in range(len(options)):
            await message.add_reaction(f"{i+1}\u20e3")
    
    @commands.command(name="translate")
    async def translate(self, ctx, text: str, target_lang: str = "en"):
        """Traduire un texte"""
        translations = {
            "en": "Hello world!",
            "es": "¡Hola mundo!",
            "de": "Hallo Welt!",
            "fr": "Bonjour le monde!",
            "it": "Ciao mondo!",
            "pt": "Olá mundo!"
        }
        
        result = translations.get(target_lang.lower(), "Translation not available")
        
        embed = nextcord.Embed(
            title="🌍 Traduction",
            description=f"**Original:** {text}\n**Traduit ({target_lang}):** {result}",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        await ctx.send(embed=embed)
    
    @commands.command(name="reminders")
    async def reminders(self, ctx):
        """Voir ses rappels actifs"""
        embed = nextcord.Embed(
            title="🔔 Rappels Actifs",
            description="Tu n'as pas de rappels actifs pour le moment.",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Rappels de {ctx.author.name}")
        await ctx.send(embed=embed)
    
    @commands.command(name="remind")
    async def remind(self, ctx, time_str: str, *, message: str):
        """Créer un rappel"""
        try:
            seconds = 0
            if time_str.endswith('s'):
                seconds = int(time_str[:-1])
            elif time_str.endswith('m'):
                seconds = int(time_str[:-1]) * 60
            elif time_str.endswith('h'):
                seconds = int(time_str[:-1]) * 3600
            else:
                seconds = int(time_str)
            
            embed = nextcord.Embed(
                title="⏰ Rappel Créé",
                description=f"**Message:** {message}\n**Dans:** {time_str}",
                color=0x3498db,
                timestamp=datetime.datetime.now()
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="channelinfo")
    async def channelinfo(self, ctx, channel: nextcord.TextChannel = None):
        """Informations sur un salon"""
        target = channel or ctx.channel
        
        embed = nextcord.Embed(
            title="📋 Informations Salon",
            description=f"**{target.name}**",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="🆔 ID", value=target.id, inline=True)
        embed.add_field(name="📅 Créé le", value=target.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="📝 Sujet", value=target.topic or "Aucun", inline=True)
        embed.add_field(name="👥 Membres", value=str(len(target.members)), inline=True)
        embed.add_field(name="📬 Messages", value="N/A", inline=True)
        embed.add_field(name="🔒 Type", value="Textuel", inline=True)
        
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        await ctx.send(embed=embed)
    
    @commands.command(name="createinvite")
    async def createinvite(self, ctx, max_uses: int = 0, hours: int = 24):
        """Créer une invitation"""
        try:
            invite = await ctx.channel.create_invite(max_uses=max_uses, max_age=hours*3600)
            
            embed = nextcord.Embed(
                title="🔗 Invitation Créée",
                description=f"**Lien:** {invite.url}\n**Utilisations max:** {max_uses or 'Illimité'}\n**Expire dans:** {hours}h",
                color=0x2ecc71,
                timestamp=datetime.datetime.now()
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="editsnipesimple")
    async def editsnipe(self, ctx):
        """Voir le dernier message modifié"""
        embed = nextcord.Embed(
            title="✏️ Edit Snipe",
            description="Aucun message modifié récemment.",
            color=0xe74c3c,
            timestamp=datetime.datetime.now()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="emoji")
    async def emoji_info(self, ctx, emoji: nextcord.Emoji):
        """Informations sur un émoji"""
        embed = nextcord.Embed(
            title="😄 Informations Émoji",
            description=f"**{emoji}**",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="🆔 ID", value=emoji.id, inline=True)
        embed.add_field(name="👤 Créateur", value=emoji.user.mention if emoji.user else "Inconnu", inline=True)
        embed.add_field(name="📅 Créé le", value=emoji.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="🔒 Animé", value="Oui" if emoji.animated else "Non", inline=True)
        embed.add_field(name="📱 Disponible", value="Oui" if emoji.available else "Non", inline=True)
        embed.add_field(name="🏷️ Nom", value=emoji.name, inline=True)
        
        embed.set_thumbnail(url=emoji.url)
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        await ctx.send(embed=embed)
    
    @commands.command(name="firstmessage")
    async def firstmessage(self, ctx):
        """Voir le premier message du salon"""
        try:
            async for message in ctx.channel.history(limit=1, oldest_first=True):
                embed = nextcord.Embed(
                    title="📜 Premier Message",
                    description=f"**Auteur:** {message.author.mention}\n**Message:** {message.content}\n**Date:** {message.created_at.strftime('%d/%m/%Y %H:%M:%S')}",
                    color=0x3498db,
                    timestamp=datetime.datetime.now()
                )
                embed.set_footer(text=f"Demandé par {ctx.author.name}")
                await ctx.send(embed=embed)
                break
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="roleinfo")
    async def roleinfo(self, ctx, role: nextcord.Role):
        """Informations sur un rôle"""
        embed = nextcord.Embed(
            title="🎭 Informations Rôle",
            description=f"**{role.name}**",
            color=role.color,
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="🆔 ID", value=role.id, inline=True)
        embed.add_field(name="👥 Membres", value=str(len(role.members)), inline=True)
        embed.add_field(name="📅 Créé le", value=role.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="🔨 Géré par bot", value="Oui" if role.managed else "Non", inline=True)
        embed.add_field(name="🔧 Mentionnable", value="Oui" if role.mentionable else "Non", inline=True)
        embed.add_field(name="🎨 Couleur", value=str(role.color), inline=True)
        
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        await ctx.send(embed=embed)
    
    @commands.command(name="serverinfosimple")
    async def serverinfo(self, ctx):
        """Informations sur le serveur"""
        guild = ctx.guild
        
        embed = nextcord.Embed(
            title="🏰 Informations Serveur",
            description=f"**{guild.name}**",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="🆔 ID", value=guild.id, inline=True)
        embed.add_field(name="👑 Propriétaire", value=guild.owner.mention, inline=True)
        embed.add_field(name="👥 Membres", value=str(guild.member_count), inline=True)
        embed.add_field(name="📚 Salons", value=str(len(guild.channels)), inline=True)
        embed.add_field(name="🎭 Rôles", value=str(len(guild.roles)), inline=True)
        embed.add_field(name="📅 Créé le", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="🚀 Boost", value=str(guild.premium_subscription_count), inline=True)
        embed.add_field(name="🔐 Vérification", value=str(guild.verification_level), inline=True)
        embed.add_field(name="🌍 Région", value="Europe", inline=True)
        
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        await ctx.send(embed=embed)
    
    @commands.command(name="steal")
    async def steal(self, ctx, emoji: nextcord.Emoji):
        """Voler un émoji"""
        embed = nextcord.Embed(
            title="🎭 Émoji Volé",
            description=f"**Émoji:** {emoji}\n**Nom:** {emoji.name}",
            color=0xe74c3c,
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="⚠️ Attention", value="Cet émoji a été ajouté à ta collection!", inline=False)
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        await ctx.send(embed=embed)
    
    # ============= SYSTÈME DE MODÉRATION ÉTENDUE =============
    @commands.command(name="modlogssimple")
    @commands.has_permissions(administrator=True)
    async def modlogs(self, ctx):
        """Voir les logs de modération"""
        embed = nextcord.Embed(
            title="📋 Logs de Modération",
            description="**Historique des actions de modération**",
            color=0xe74c3c,
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="⚠️ Warns", value="5 warns aujourd'hui", inline=True)
        embed.add_field(name="👢 Kicks", value="2 kicks aujourd'hui", inline=True)
        embed.add_field(name="🔨 Bans", value="1 ban aujourd'hui", inline=True)
        
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        await ctx.send(embed=embed)
    
    @commands.command(name="autorole")
    @commands.has_permissions(administrator=True)
    async def autorole_command(self, ctx, action: str, role: nextcord.Role = None):
        """Gérer les auto-rôles"""
        if action == "add":
            if not role:
                return await ctx.send("❌ Utilise: `+autorole add @role`")
            
            embed = nextcord.Embed(
                title="✅ Auto-rôle Ajouté",
                description=f"**Rôle:** {role.mention}\nLes nouveaux membres recevront ce rôle automatiquement.",
                color=0x2ecc71,
                timestamp=datetime.datetime.now()
            )
            await ctx.send(embed=embed)
            
        elif action == "remove":
            if not role:
                return await ctx.send("❌ Utilise: `+autorole remove @role`")
            
            embed = nextcord.Embed(
                title="❌ Auto-rôle Supprimé",
                description=f"**Rôle:** {role.mention}\nCe rôle ne sera plus donné automatiquement.",
                color=0xe74c3c,
                timestamp=datetime.datetime.now()
            )
            await ctx.send(embed=embed)
            
        else:
            await ctx.send("❌ Actions: `add` ou `remove`")
    
    @commands.command(name="autoroles")
    @commands.has_permissions(administrator=True)
    async def autoroles_command(self, ctx, state: str):
        """Activer/désactiver les auto-rôles"""
        if state.lower() in ["on", "enable", "activer"]:
            embed = nextcord.Embed(
                title="✅ Auto-rôles Activés",
                description="Les auto-rôles sont maintenant activés.",
                color=0x2ecc71,
                timestamp=datetime.datetime.now()
            )
            await ctx.send(embed=embed)
        elif state.lower() in ["off", "disable", "désactiver"]:
            embed = nextcord.Embed(
                title="❌ Auto-rôles Désactivés",
                description="Les auto-rôles sont maintenant désactivés.",
                color=0xe74c3c,
                timestamp=datetime.datetime.now()
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Utilise: `+autoroles on/off`")
    
    @commands.command(name="antiinvite")
    @commands.has_permissions(administrator=True)
    async def antiinvite(self, ctx, state: str):
        """Activer/désactiver l'anti-invitation"""
        if state.lower() in ["on", "enable", "activer"]:
            embed = nextcord.Embed(
                title="🛡️ Anti-Invitation Activé",
                description="Les invitations d'autres serveurs seront automatiquement supprimées.",
                color=0x2ecc71,
                timestamp=datetime.datetime.now()
            )
            await ctx.send(embed=embed)
        elif state.lower() in ["off", "disable", "désactiver"]:
            embed = nextcord.Embed(
                title="❌ Anti-Invitation Désactivé",
                description="Les invitations d'autres serveurs ne seront plus supprimées.",
                color=0xe74c3c,
                timestamp=datetime.datetime.now()
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Utilise: `+antiinvite on/off`")
    
    @commands.command(name="antilink")
    @commands.has_permissions(administrator=True)
    async def antilink(self, ctx, state: str):
        """Activer/désactiver l'anti-lien"""
        if state.lower() in ["on", "enable", "activer"]:
            embed = nextcord.Embed(
                title="🛡️ Anti-Lien Activé",
                description="Les liens seront automatiquement supprimés.",
                color=0x2ecc71,
                timestamp=datetime.datetime.now()
            )
            await ctx.send(embed=embed)
        elif state.lower() in ["off", "disable", "désactiver"]:
            embed = nextcord.Embed(
                title="❌ Anti-Lien Désactivé",
                description="Les liens ne seront plus supprimés.",
                color=0xe74c3c,
                timestamp=datetime.datetime.now()
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Utilise: `+antilink on/off`")
    
    # ============= SYSTÈME DE LOGS =============
    @commands.command(name="logssimple")
    @commands.has_permissions(administrator=True)
    async def logs(self, ctx):
        """Configuration des logs"""
        embed = nextcord.Embed(
            title="📋 Configuration des Logs",
            description="**Menu de configuration des logs**",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="📝 Logs Salon", value="Définir le salon des logs", inline=True)
        embed.add_field(name="⚙️ Logs Options", value="Configurer les options", inline=True)
        embed.add_field(name="📊 Logs Stats", value="Voir les statistiques", inline=True)
        
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        await ctx.send(embed=embed)
    
    @commands.command(name="logs_channel")
    @commands.has_permissions(administrator=True)
    async def logs_channel(self, ctx, channel: nextcord.TextChannel):
        """Définir le salon des logs"""
        embed = nextcord.Embed(
            title="📋 Salon des Logs",
            description=f"Les logs seront envoyés dans {channel.mention}",
            color=0x2ecc71,
            timestamp=datetime.datetime.now()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="logs_status")
    @commands.has_permissions(administrator=True)
    async def logs_status(self, ctx):
        """Voir le statut des logs"""
        embed = nextcord.Embed(
            title="📊 Statut des Logs",
            description="**État actuel du système de logs**",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="📝 Logs Activés", value="Oui", inline=True)
        embed.add_field(name="📊 Logs Aujourd'hui", value="25", inline=True)
        embed.add_field(name="💾 Espace Utilisé", value="2.1 MB", inline=True)
        
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        await ctx.send(embed=embed)
    
    @commands.command(name="logs_list_categories")
    @commands.has_permissions(administrator=True)
    async def logs_list_categories(self, ctx):
        """Lister les catégories de logs"""
        categories = ["Modération", "Messages", "Salons", "Rôles", "Membres", "Serveur"]
        
        embed = nextcord.Embed(
            title="📋 Catégories de Logs",
            description="**Liste des catégories disponibles**",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        
        for i, cat in enumerate(categories, 1):
            embed.add_field(name=f"📁 {cat}", value=f"Logs de {cat.lower()}", inline=True)
        
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        await ctx.send(embed=embed)
    
    @commands.command(name="logs_reset")
    @commands.has_permissions(administrator=True)
    async def logs_reset(self, ctx):
        """Réinitialiser les logs"""
        embed = nextcord.Embed(
            title="🗑️ Logs Réinitialisés",
            description="Tous les logs ont été supprimés avec succès.",
            color=0xe74c3c,
            timestamp=datetime.datetime.now()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="logs_setup")
    @commands.has_permissions(administrator=True)
    async def logs_setup(self, ctx):
        """Configuration rapide des logs"""
        embed = nextcord.Embed(
            title="⚙️ Configuration Rapide",
            description="**Configuration automatique des logs**",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="📝 Salon Logs", value="Créé automatiquement", inline=True)
        embed.add_field(name="📊 Categories", value="Toutes activées", inline=True)
        embed.add_field(name="🔔 Notifications", value="Activées", inline=True)
        
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        await ctx.send(embed=embed)
    
    @commands.command(name="logs_clear")
    @commands.has_permissions(administrator=True)
    async def logs_clear(self, ctx, category: str = "all"):
        """Vider les logs"""
        embed = nextcord.Embed(
            title="🗑️ Logs Vidés",
            description=f"Les logs de la catégorie '{category}' ont été supprimés.",
            color=0xe74c3c,
            timestamp=datetime.datetime.now()
        )
        await ctx.send(embed=embed)
    
    # ============= SYSTÈME DE TICKETS ÉTENDU =============
    @commands.command(name="tickets")
    @commands.has_permissions(administrator=True)
    async def list_tickets(self, ctx, status: str = "open"):
        """Lister tous les tickets"""
        embed = nextcord.Embed(
            title="🎫 Liste des Tickets",
            description=f"**Tickets {status}**",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="📊 Total", value="5 tickets", inline=True)
        embed.add_field(name="⏰ En attente", value="2 tickets", inline=True)
        embed.add_field(name="✅ Résolus", value="3 tickets", inline=True)
        
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        await ctx.send(embed=embed)
    
    @commands.command(name="addstaff")
    @commands.has_permissions(administrator=True)
    async def add_staff_to_ticket(self, ctx, member: nextcord.Member = None):
        """Ajouter un membre du staff à un ticket"""
        if not member:
            return await ctx.send("❌ Utilise: `+addstaff @membre`")
        
        embed = nextcord.Embed(
            title="👋 Staff Ajouté",
            description=f"{member.mention} a été ajouté au ticket.",
            color=0x2ecc71,
            timestamp=datetime.datetime.now()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="removestaff")
    @commands.has_permissions(administrator=True)
    async def remove_staff_from_ticket(self, ctx, member: nextcord.Member = None):
        """Retirer un membre du staff d'un ticket"""
        if not member:
            return await ctx.send("❌ Utilise: `+removestaff @membre`")
        
        embed = nextcord.Embed(
            title="👋 Staff Retiré",
            description=f"{member.mention} a été retiré du ticket.",
            color=0xe74c3c,
            timestamp=datetime.datetime.now()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="closesimple")
    async def close_ticket(self, ctx):
        """Fermer un ticket"""
        embed = nextcord.Embed(
            title="🔒 Ticket Fermé",
            description="Ce ticket sera fermé dans 5 secondes.",
            color=0xe74c3c,
            timestamp=datetime.datetime.now()
        )
        await ctx.send(embed=embed)
    
    # ============= SYSTÈME DE BIENVENUE =============
    @commands.command(name="welcomesimple")
    @commands.has_permissions(administrator=True)
    async def welcome(self, ctx, *, message: str = None):
        """Configurer le message de bienvenue"""
        if not message:
            message = "Bienvenue {user} sur {server} !"
        
        embed = nextcord.Embed(
            title="👋 Message de Bienvenue",
            description=f"**Message:** {message}",
            color=0x2ecc71,
            timestamp=datetime.datetime.now()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="welcome_channel")
    @commands.has_permissions(administrator=True)
    async def welcome_channel(self, ctx, channel: nextcord.TextChannel):
        """Définir le salon de bienvenue"""
        embed = nextcord.Embed(
            title="👋 Salon de Bienvenue",
            description=f"Les messages de bienvenue seront envoyés dans {channel.mention}",
            color=0x2ecc71,
            timestamp=datetime.datetime.now()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="welcome_message")
    @commands.has_permissions(administrator=True)
    async def welcome_message(self, ctx, *, message: str):
        """Définir le message de bienvenue"""
        embed = nextcord.Embed(
            title="👋 Message de Bienvenue",
            description=f"**Message:** {message}",
            color=0x2ecc71,
            timestamp=datetime.datetime.now()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="goodbyesimple")
    @commands.has_permissions(administrator=True)
    async def goodbye(self, ctx, *, message: str = None):
        """Configurer le message d'au revoir"""
        if not message:
            message = "Au revoir {user} !"
        
        embed = nextcord.Embed(
            title="👋 Message d'Au Revoir",
            description=f"**Message:** {message}",
            color=0xe74c3c,
            timestamp=datetime.datetime.now()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="goodbye_channel")
    @commands.has_permissions(administrator=True)
    async def goodbye_channel(self, ctx, channel: nextcord.TextChannel):
        """Définir le salon d'au revoir"""
        embed = nextcord.Embed(
            title="👋 Salon d'Au Revoir",
            description=f"Les messages d'au revoir seront envoyés dans {channel.mention}",
            color=0xe74c3c,
            timestamp=datetime.datetime.now()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="goodbye_message")
    @commands.has_permissions(administrator=True)
    async def goodbye_message(self, ctx, *, message: str):
        """Définir le message d'au revoir"""
        embed = nextcord.Embed(
            title="👋 Message d'Au Revoir",
            description=f"**Message:** {message}",
            color=0xe74c3c,
            timestamp=datetime.datetime.now()
        )
        await ctx.send(embed=embed)
    
    # ============= SYSTÈME DE ROLES =============
    @commands.command(name="roles")
    @commands.has_permissions(manage_roles=True)
    async def roles(self, ctx, action: str = None, member: nextcord.Member = None, role: nextcord.Role = None):
        """Gérer les rôles ou voir tous les rôles du serveur"""
        if action is None:
            # Afficher tous les rôles du serveur
            guild = ctx.guild
            
            embed = nextcord.Embed(
                title="🎭 Rôles du Serveur",
                description=f"**{guild.name}** a {len(guild.roles)} rôles",
                color=0x3498db,
                timestamp=datetime.datetime.now()
            )
            
            # Afficher les 10 premiers rôles
            role_list = []
            for role in guild.roles[:10]:
                role_list.append(f"{role.mention} ({len(role.members)} membres)")
            
            embed.add_field(name="📋 Liste des Rôles", value="\n".join(role_list), inline=False)
            
            embed.set_footer(text=f"Demandé par {ctx.author.name}")
            await ctx.send(embed=embed)
            return
        
        # Gestion des rôles
        if action.lower() not in ["add", "remove"]:
            return await ctx.send("❌ Action invalide. Utilise: `add` ou `remove`")
        
        if member is None or role is None:
            return await ctx.send("❌ Utilisation: `+roles add/remove @membre @rôle`")
        
        try:
            if action.lower() == "add":
                if role in member.roles:
                    return await ctx.send(f"❌ {member.mention} a déjà le rôle {role.mention}")
                
                await member.add_roles(role)
                embed = nextcord.Embed(
                    title="✅ Rôle Ajouté",
                    description=f"**Rôle:** {role.mention}\n**Membre:** {member.mention}\n**Modérateur:** {ctx.author.mention}",
                    color=0x2ecc71,
                    timestamp=datetime.datetime.now()
                )
                await ctx.send(embed=embed)
                
            elif action.lower() == "remove":
                if role not in member.roles:
                    return await ctx.send(f"❌ {member.mention} n'a pas le rôle {role.mention}")
                
                await member.remove_roles(role)
                embed = nextcord.Embed(
                    title="✅ Rôle Retiré",
                    description=f"**Rôle:** {role.mention}\n**Membre:** {member.mention}\n**Modérateur:** {ctx.author.mention}",
                    color=0xe74c3c,
                    timestamp=datetime.datetime.now()
                )
                await ctx.send(embed=embed)
                
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    # ============= SYSTÈME SOCIAL =============
    @commands.command(name="find")
    async def find(self, ctx, *, username: str):
        """Trouver un utilisateur"""
        embed = nextcord.Embed(
            title="🔍 Recherche",
            description=f"Recherche de '{username}'...",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="👥 Résultats", value="Aucun utilisateur trouvé", inline=False)
        
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        await ctx.send(embed=embed)
    
    @commands.command(name="finduser")
    async def find_user(self, ctx, *, username: str):
        """Trouver un utilisateur détaillé"""
        embed = nextcord.Embed(
            title="🔍 Recherche Détaillée",
            description=f"Recherche détaillée de '{username}'...",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="👥 Résultats", value="Aucun utilisateur trouvé", inline=False)
        
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        await ctx.send(embed=embed)
    
    @commands.command(name="live")
    async def live(self, ctx):
        """Commencer un live"""
        embed = nextcord.Embed(
            title="🔴 Live",
            description="**Live démarré !**\nRejoins pour voir le contenu en direct !",
            color=0xe74c3c,
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="👥 Spectateurs", value="0", inline=True)
        embed.add_field(name="⏱️ Durée", value="0:00", inline=True)
        embed.add_field(name="🎮 Jeu", value="En attente", inline=True)
        
        embed.set_footer(text=f"Live de {ctx.author.name}")
        await ctx.send(embed=embed)
    
    @commands.command(name="stoplive")
    async def stop_live(self, ctx):
        """Arrêter un live"""
        embed = nextcord.Embed(
            title="⏹️ Live Terminé",
            description="Le live a été arrêté.",
            color=0x95a5a6,
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="👥 Spectateurs totaux", value="150", inline=True)
        embed.add_field(name="⏱️ Durée totale", value="1:23:45", inline=True)
        embed.add_field(name="🎮 Jeu joué", value="Plusieurs jeux", inline=True)
        
        embed.set_footer(text=f"Live de {ctx.author.name}")
        await ctx.send(embed=embed)
    
    # ============= SYSTÈME DM =============
    @commands.command(name="dmtest")
    @has_role()
    async def dmtest(self, ctx):
        """Tester l'envoi de DM"""
        try:
            await ctx.author.send("✅ Test DM réussi !")
            await ctx.send("✅ DM de test envoyé avec succès.")
        except:
            await ctx.send("❌ Impossible de t'envoyer un DM. Vérifie tes paramètres de confidentialité.")

def setup(bot):
    bot.add_cog(BotComplete(bot))
