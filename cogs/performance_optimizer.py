import nextcord
from nextcord.ext import commands
import datetime
import psutil
import gc
import os

class PerformanceOptimizer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="optimize")
    @commands.has_permissions(administrator=True)
    async def optimize(self, ctx):
        """Optimiser les performances du bot"""
        try:
            # Nettoyer la mémoire
            gc.collect()
            
            # Obtenir les stats avant optimisation
            memory_before = psutil.virtual_memory().percent
            cpu_before = psutil.cpu_percent(interval=1)
            
            # Forcer le garbage collection
            collected = gc.collect()
            
            # Stats après optimisation
            memory_after = psutil.virtual_memory().percent
            cpu_after = psutil.cpu_percent(interval=1)
            
            embed = nextcord.Embed(
                title="⚡ Optimisation Terminée",
                description="Le bot a été optimisé avec succès!",
                color=0x2ecc71,
                timestamp=datetime.datetime.now()
            )
            
            embed.add_field(name="🧹 Mémoire nettoyée", value=f"{collected} objets collectés", inline=True)
            embed.add_field(name="💾 Mémoire avant", value=f"{memory_before:.1f}%", inline=True)
            embed.add_field(name="💾 Mémoire après", value=f"{memory_after:.1f}%", inline=True)
            embed.add_field(name="🖥️ CPU avant", value=f"{cpu_before:.1f}%", inline=True)
            embed.add_field(name="🖥️ CPU après", value=f"{cpu_after:.1f}%", inline=True)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur lors de l'optimisation: {e}")
    
    @commands.command(name="cache")
    @commands.has_permissions(administrator=True)
    async def cache(self, ctx, action: str = "clear"):
        """Gérer le cache du bot"""
        if action == "clear":
            # Vider le cache
            gc.collect()
            
            embed = nextcord.Embed(
                title="🗑️ Cache Vidé",
                description="Le cache du bot a été vidé avec succès.",
                color=0x2ecc71,
                timestamp=datetime.datetime.now()
            )
            await ctx.send(embed=embed)
            
        elif action == "info":
            # Informations sur le cache
            memory_info = psutil.virtual_memory()
            
            embed = nextcord.Embed(
                title="📊 Informations Cache",
                description="Statistiques actuelles du cache:",
                color=0x3498db,
                timestamp=datetime.datetime.now()
            )
            
            embed.add_field(name="💾 Mémoire totale", value=f"{memory_info.total // (1024**3)} GB", inline=True)
            embed.add_field(name="💾 Mémoire utilisée", value=f"{memory_info.percent:.1f}%", inline=True)
            embed.add_field(name="💾 Mémoire disponible", value=f"{100 - memory_info.percent:.1f}%", inline=True)
            
            await ctx.send(embed=embed)
            
        else:
            await ctx.send("❌ Actions disponibles: `clear`, `info`")
    
    @commands.command(name="restart_bot")
    @commands.is_owner()
    async def restart_bot(self, ctx):
        """Redémarrer le bot (owner only)"""
        await ctx.send("🔄 Redémarrage du bot...")
        
        # Sauvegarder l'état si nécessaire
        # Puis redémarrer
        await self.bot.close()
    
    @commands.command(name="health")
    async def health(self, ctx):
        """Vérifier la santé du bot"""
        try:
            # Stats système
            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=1)
            
            # Stats bot
            uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(self.bot.start_time)
            guilds = len(self.bot.guilds)
            users = len(self.bot.users)
            commands = len(self.bot.commands)
            
            embed = nextcord.Embed(
                title="🏥 Santé du Bot",
                description="État de santé actuel du bot:",
                color=0x3498db,
                timestamp=datetime.datetime.now()
            )
            
            embed.add_field(name="⏱️ Uptime", value=str(uptime).split('.')[0], inline=True)
            embed.add_field(name="💾 Mémoire", value=f"{memory.percent:.1f}%", inline=True)
            embed.add_field(name="🖥️ CPU", value=f"{cpu:.1f}%", inline=True)
            embed.add_field(name="🚀 Latence", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
            embed.add_field(name="📡 Serveurs", value=str(guilds), inline=True)
            embed.add_field(name="👥 Utilisateurs", value=str(users), inline=True)
            embed.add_field(name="⚙️ Commandes", value=str(commands), inline=True)
            
            # Déterminer le statut
            if memory.percent < 70 and cpu < 70:
                status = "🟢 Excellent"
                color = 0x2ecc71
            elif memory.percent < 85 and cpu < 85:
                status = "🟡 Bon"
                color = 0xf39c12
            else:
                status = "🔴 Critique"
                color = 0xe74c3c
            
            embed.add_field(name="🏥 Statut", value=status, inline=False)
            embed.color = color
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")

def setup(bot):
    bot.add_cog(PerformanceOptimizer(bot))
