import nextcord
from nextcord.ext import commands
from config import AUTHORIZED_ROLE_ID

def has_role():
    async def predicate(ctx):
        role = ctx.guild.get_role(AUTHORIZED_ROLE_ID)
        return role in ctx.author.roles
    return commands.check(predicate)

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="lockchannel",
        help="Verrouille un salon pour empêcher les membres d’envoyer des messages."
    )
    @has_role()
    async def lockchannel(self, ctx, channel: nextcord.TextChannel = None):
        channel = channel or ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send(f"🔒 Salon verrouillé : {channel.mention}")

    @commands.command(
        name="unlockchannel",
        help="Déverrouille un salon pour permettre aux membres d’envoyer des messages."
    )
    @has_role()
    async def unlockchannel(self, ctx, channel: nextcord.TextChannel = None):
        channel = channel or ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = True
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send(f"🔓 Salon déverrouillé : {channel.mention}")

    @commands.command(
        name="say",
        help="Fait parler le bot dans le salon actuel."
    )
    @has_role()
    async def say(self, ctx, *, message=None):
        if not message:
            return await ctx.send("Utilise : `+say <message>`")
        await ctx.send(message)
        await ctx.message.delete()

def setup(bot):
    bot.add_cog(Moderation(bot))
