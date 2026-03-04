import nextcord
from nextcord.ext import commands
import asyncio
import datetime
import json
import os

class UtilityEnhanced(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_timers = {}
        
    # ============= SYSTÈME DE TIMER =============
    @commands.command(name="timer")
    async def timer(self, ctx, time_str: str, *, message: str = "Temps écoulé !"):
        """Démarrer un minuteur (format: 30s, 5m, 1h)"""
        try:
            # Parser le temps
            seconds = 0
            if time_str.endswith('s'):
                seconds = int(time_str[:-1])
            elif time_str.endswith('m'):
                seconds = int(time_str[:-1]) * 60
            elif time_str.endswith('h'):
                seconds = int(time_str[:-1]) * 3600
            else:
                seconds = int(time_str)
            
            if seconds < 1 or seconds > 86400:  # Max 24h
                return await ctx.send("❌ Le timer doit être entre 1 seconde et 24 heures.")
            
            # Envoyer le message de confirmation
            embed = nextcord.Embed(
                title="⏰ Timer Démarré",
                description=f"**Durée:** {time_str}\n**Message:** {message}",
                color=0x3498db,
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Timer de {ctx.author.name}")
            
            msg = await ctx.send(embed=embed)
            
            # Attendre le temps
            await asyncio.sleep(seconds)
            
            # Envoyer le message de fin
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
    
    # ============= SYSTÈME DE STOPWATCH =============
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
            
            # Ajouter les réactions pour arrêter
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
    
    # ============= SYSTÈME DE RAPPELS =============
    @commands.command(name="remind")
    async def remind(self, ctx, time_str: str, *, message: str):
        """Créer un rappel"""
        try:
            # Parser le temps
            seconds = 0
            if time_str.endswith('s'):
                seconds = int(time_str[:-1])
            elif time_str.endswith('m'):
                seconds = int(time_str[:-1]) * 60
            elif time_str.endswith('h'):
                seconds = int(time_str[:-1]) * 3600
            elif time_str.endswith('d'):
                seconds = int(time_str[:-1]) * 86400
            else:
                seconds = int(time_str)
            
            if seconds < 1 or seconds > 604800:  # Max 7 jours
                return await ctx.send("❌ Le rappel doit être entre 1 seconde et 7 jours.")
            
            # Envoyer la confirmation
            embed = nextcord.Embed(
                title="🔔 Rappel Créé",
                description=f"**Message:** {message}\n**Dans:** {time_str}",
                color=0x3498db,
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Rappel de {ctx.author.name}")
            
            await ctx.send(embed=embed)
            
            # Attendre le temps
            await asyncio.sleep(seconds)
            
            # Envoyer le rappel
            remind_embed = nextcord.Embed(
                title="🔔 Rappel !",
                description=f"**Message:** {message}",
                color=0xe74c3c,
                timestamp=datetime.datetime.now()
            )
            remind_embed.set_footer(text=f"Rappel de {ctx.author.name}")
            
            await ctx.author.send(embed=remind_embed)
            await ctx.send(f"🔔 Rappel envoyé à {ctx.author.mention}")
            
        except ValueError:
            await ctx.send("❌ Format invalide. Utilise: `+remind 30s message`, `+remind 5m message`, `+remind 1h message`")
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="reminders")
    async def reminders(self, ctx):
        """Voir ses rappels actifs"""
        try:
            embed = nextcord.Embed(
                title="🔔 Rappels Actifs",
                description="Tu n'as pas de rappels actifs pour le moment.",
                color=0x3498db,
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Rappels de {ctx.author.name}")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")

def setup(bot):
    bot.add_cog(UtilityEnhanced(bot))
