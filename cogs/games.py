import nextcord
from nextcord.ext import commands
import random
from config import AUTHORIZED_ROLE_ID

active_games = {}

def has_role():
    async def predicate(ctx):
        role = ctx.guild.get_role(AUTHORIZED_ROLE_ID)
        return role in ctx.author.roles
    return commands.check(predicate)

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="devinelenombre",
        help="Lance un jeu où les membres doivent deviner un nombre dans un salon donné."
    )
    @has_role()
    async def devinelenombre(self, ctx, min_val: int, max_val: int, channel: nextcord.TextChannel):
        number = random.randint(min_val, max_val)
        active_games[channel.id] = number

        await ctx.send(f"🎮 Le jeu commence dans {channel.mention} !")
        await channel.send(f"Devinez un nombre entre **{min_val}** et **{max_val}** !")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        cid = message.channel.id
        if cid not in active_games:
            return

        try:
            guess = int(message.content)
        except:
            return

        if guess == active_games[cid]:
            await message.channel.send(f"🎉 {message.author.mention} a trouvé le nombre !")
            del active_games[cid]

def setup(bot):
    bot.add_cog(Games(bot))
