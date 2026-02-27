import nextcord
from nextcord.ext import commands
import time
from config import AUTHORIZED_ROLE_ID

start_time = time.time()

def has_role():
    async def predicate(ctx):
        role = ctx.guild.get_role(AUTHORIZED_ROLE_ID)
        return role in ctx.author.roles
    return commands.check(predicate)

class System(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    @has_role()
    async def help(self, ctx, *, query=None):
        # ============================
        # HELP GENERAL
        # ============================
        if query is None:
            embed = nextcord.Embed(
                title="📘 Aide du bot",
                description="Utilise `+help <commande>` pour plus d'informations.",
                color=0x3498db
            )

            embed.add_field(
                name="🎙️ Vocal",
                value=(
                    "`mooveallrandom`, `mooveusers`, `moove`, `move`, `mooverandom`, `mooveall`,\n"
                    "`shuffle start`, `shufflestop`, `back`, `mooveserver`,\n"
                    "`joinme`, `join`, `leave`"
                ),
                inline=False
            )

            embed.add_field(
                name="🛡️ Modération",
                value="`lockchannel`, `unlockchannel`, `say`",
                inline=False
            )

            embed.add_field(
                name="🎮 Jeux",
                value="`devinelenombre`",
                inline=False
            )

            embed.add_field(
                name="📊 Système",
                value="`stat`",
                inline=False
            )

            return await ctx.send(embed=embed)

        # ============================
        # HELP POUR UNE COMMANDE
        # ============================
        command = self.bot.get_command(query)

        if command is None:
            return await ctx.send("❌ Commande inconnue.")

        embed = nextcord.Embed(
            title=f"ℹ️ Aide : `{command.name}`",
            color=0x3498db
        )

        embed.add_field(
            name="Description",
            value=command.help or "Aucune description disponible.",
            inline=False
        )

        embed.add_field(
            name="Utilisation",
            value=f"`+{command.name} {command.signature}`",
            inline=False
        )

        return await ctx.send(embed=embed)

    @commands.command(name="stat")
    @has_role()
    async def stat(self, ctx):
        uptime = int(time.time() - start_time)
        embed = nextcord.Embed(title="📊 Statistiques", color=0x3498db)
        embed.add_field(name="Uptime", value=f"{uptime} sec")
        embed.add_field(name="Ping", value=f"{round(self.bot.latency * 1000)} ms")
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(System(bot))


