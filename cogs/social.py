import nextcord
from nextcord.ext import commands
import datetime
import random

class Social(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="hug")
    async def hug(self, ctx, member: nextcord.Member = None):
        """Faire un câlin à quelqu'un"""
        target = member or ctx.author
        
        hug_messages = [
            f"🤗 {ctx.author.mention} fait un grand câlin à {target.mention}!",
            f"💝 {ctx.author.mention} serre {target.mention} dans ses bras!",
            f"🌟 {ctx.author.mention} envoie tout son amour à {target.mention}!"
        ]
        
        embed = nextcord.Embed(
            title="🤗 Câlin!",
            description=random.choice(hug_messages),
            color=0xff69b4,
            timestamp=datetime.datetime.now()
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="slap")
    async def slap(self, ctx, member: nextcord.Member = None):
        """Donner une claque à quelqu'un"""
        target = member or ctx.author
        
        slap_messages = [
            f"👋 {ctx.author.mention} donne une petite claque à {target.mention}!",
            f"💥 {ctx.author.mention} distribue une claque mémorable à {target.mention}!",
            f"🔥 {ctx.author.mention} applique une correction à {target.mention}!"
        ]
        
        embed = nextcord.Embed(
            title="👋 Claques!",
            description=random.choice(slap_messages),
            color=0xff6347,
            timestamp=datetime.datetime.now()
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="highfive")
    async def highfive(self, ctx, member: nextcord.Member = None):
        """Faire un high-five"""
        target = member or ctx.author
        
        embed = nextcord.Embed(
            title="🙌 High-Five!",
            description=f"🎉 {ctx.author.mention} et {target.mention} se font un high-five!",
            color=0xffd700,
            timestamp=datetime.datetime.now()
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="poke")
    async def poke(self, ctx, member: nextcord.Member = None):
        """Pousser quelqu'un"""
        target = member or ctx.author
        
        embed = nextcord.Embed(
            title="👉 Poke!",
            description=f"👆 {ctx.author.mention} poke {target.mention}!",
            color=0x9370db,
            timestamp=datetime.datetime.now()
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="pat")
    async def pat(self, ctx, member: nextcord.Member = None):
        """Câliner la tête de quelqu'un"""
        target = member or ctx.author
        
        embed = nextcord.Embed(
            title="👋 Pat Pat",
            description=f"🥰 {ctx.author.mention} fait pat-pat sur la tête de {target.mention}!",
            color=0xffb6c1,
            timestamp=datetime.datetime.now()
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="wave")
    async def wave(self, ctx, member: nextcord.Member = None):
        """Saluer quelqu'un"""
        target = member or ctx.author
        
        embed = nextcord.Embed(
            title="👋 Salut!",
            description=f"🌊 {ctx.author.mention} salue chaleureusement {target.mention}!",
            color=0x87ceeb,
            timestamp=datetime.datetime.now()
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="compliment")
    async def compliment(self, ctx, member: nextcord.Member = None):
        """Faire un compliment à quelqu'un"""
        target = member or ctx.author
        
        compliments = [
            f"✨ {target.mention}, tu es incroyablement talentueux(se)!",
            f"🌟 {target.mention}, ta présence illumine le serveur!",
            f"💎 {target.mention}, tu es une personne vraiment exceptionnelle!",
            f"🎨 {target.mention}, tu as une créativité sans limites!",
            f"🚀 {target.mention}, tu vas accomplir de grandes choses!",
            f"🌈 {target.mention}, tu rends le monde meilleur!",
            f"💫 {target.mention}, tu es une source d'inspiration!",
            f"🎯 {target.mention}, tu as un esprit brillant!"
        ]
        
        embed = nextcord.Embed(
            title="💝 Compliment",
            description=random.choice(compliments),
            color=0xff69b4,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Compliment de {ctx.author.name}")
        
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Social(bot))
