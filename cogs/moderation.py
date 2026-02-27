import nextcord
from nextcord.ext import commands

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="stats",
        help="Affiche les statistiques du serveur."
    )
    async def stats(self, ctx):
        guild = ctx.guild

        # Membres totaux
        total_members = guild.member_count

        # Membres en ligne
        online_members = sum(
            1 for m in guild.members 
            if m.status in (nextcord.Status.online, nextcord.Status.idle, nextcord.Status.dnd)
        )

        # Membres en vocal
        voice_members = sum(len(vc.members) for vc in guild.voice_channels)

        # Boosts
        boosts = guild.premium_subscription_count

        # Embed
        embed = nextcord.Embed(
            title=f"📊 Statistiques du serveur : {guild.name}",
            color=0x2F3136
        )

        embed.add_field(name="👥 Membres totaux", value=total_members, inline=True)
        embed.add_field(name="🟢 Membres en ligne", value=online_members, inline=True)
        embed.add_field(name="🔊 Membres en vocal", value=voice_members, inline=True)
        embed.add_field(name="🚀 Boosts", value=boosts, inline=True)

        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.set_footer(text=f"Demandé par {ctx.author}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Stats(bot))

