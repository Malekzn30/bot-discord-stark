import nextcord
from nextcord.ext import commands
import time
import psutil
import datetime

class BasicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
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
        # Stats système
        memory = psutil.virtual_memory()
        cpu = psutil.cpu_percent()
        
        # Stats bot
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
        """Redémarrer le bot (propriétaire uniquement)"""
        await ctx.send("🔄 Redémarrage du bot...")
        await self.bot.close()
    
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
        await ctx.send(embed)

def setup(bot):
    bot.add_cog(BasicCommands(bot))
