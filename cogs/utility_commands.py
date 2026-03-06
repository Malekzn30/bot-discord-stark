import nextcord
from nextcord.ext import commands
import datetime
import random
import requests

class UtilityCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="userinfo")
    async def userinfo(self, ctx, member: nextcord.Member = None):
        """Informations sur un utilisateur"""
        target = member or ctx.author
        
        embed = nextcord.Embed(
            title=f"👤 Informations - {target.name}",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="🆔 ID", value=target.id, inline=True)
        embed.add_field(name="📅 Rejoint le", value=target.joined_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="🎭 Rôles", value=len(target.roles), inline=True)
        embed.set_thumbnail(url=target.display_avatar.url)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="serverinfo")
    async def serverinfo(self, ctx):
        """Informations sur le serveur"""
        embed = nextcord.Embed(
            title=f"🏢 {ctx.guild.name}",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="👥 Membres", value=ctx.guild.member_count, inline=True)
        embed.add_field(name="📚 Salons", value=len(ctx.guild.channels), inline=True)
        embed.add_field(name="🎭 Rôles", value=len(ctx.guild.roles), inline=True)
        embed.add_field(name="👑 Owner", value=ctx.guild.owner.mention, inline=True)
        embed.add_field(name="📅 Créé le", value=ctx.guild.created_at.strftime("%d/%m/%Y"), inline=True)
        
        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="avatar")
    async def avatar(self, ctx, member: nextcord.Member = None):
        """Voir l'avatar d'un utilisateur"""
        target = member or ctx.author
        
        embed = nextcord.Embed(
            title=f"🖼️ Avatar de {target.name}",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        embed.set_image(url=target.display_avatar.url)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="calc")
    async def calc(self, ctx, *, expression: str):
        """Calculatrice simple"""
        try:
            # Remplacer les opérateurs pour eval
            expression = expression.replace('x', '*').replace('÷', '/')
            result = eval(expression)
            
            embed = nextcord.Embed(
                title="🧮 Calculatrice",
                description=f"**Calcul:** {expression}\n**Résultat:** {result}",
                color=0x3498db,
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Demandé par {ctx.author.name}")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send("❌ Expression invalide.")
    
    @commands.command(name="choose")
    async def choose(self, ctx, *, options: str):
        """Choisir une option au hasard"""
        choices = [opt.strip() for opt in options.split(',')]
        if len(choices) < 2:
            return await ctx.send("❌ Spécifiez au moins 2 options séparées par des virgules.")
        
        selected = random.choice(choices)
        
        embed = nextcord.Embed(
            title="🎲 Choix Aléatoire",
            description=f"**Options:** {', '.join(choices)}\n\n**Choisi:** {selected}",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(UtilityCommands(bot))
