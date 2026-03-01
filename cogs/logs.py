import nextcord
from nextcord.ext import commands
from datetime import datetime

LOG_CHANNELS = {
    "warn": None,
    "commands": None,
    "moderation": None
}

async def send_log(bot, log_type: str, message: str, ctx=None):
    channel_id = LOG_CHANNELS.get(log_type)

    if not channel_id:
        return

    log_channel = bot.get_channel(channel_id)
    if not log_channel:
        return

    used_in = ctx.channel.mention if ctx else "Inconnu"
    now = datetime.now().strftime("%H:%M:%S")

    embed = nextcord.Embed(
        title=f"📄 Log : {log_type}",
        color=0xFFCC00
    )

    embed.add_field(name="📌 Salon", value=used_in, inline=False)
    embed.add_field(name="⏰ Heure", value=now, inline=False)
    embed.add_field(name="📝 Il y a :", value=message, inline=False)

    embed.set_footer(text="Log System")

    await log_channel.send(embed=embed)

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def logs(self, ctx, arg=None):
        if arg != "setup":
            return await ctx.send("Utilise : `+logs setup`")

        await ctx.send(
            "**Configuration des logs**\n"
            "Envoie le **type de log** que tu veux configurer :\n"
            "`warn`, `commands`, `moderation`"
        )

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        msg_type = await self.bot.wait_for("message", check=check)
        log_type = msg_type.content.lower()

        if log_type not in LOG_CHANNELS:
            return await ctx.send("❌ Type invalide.")

        await ctx.send("Mentionne le salon pour ce type de log.")

        msg_channel = await self.bot.wait_for("message", check=check)

        if not msg_channel.channel_mentions:
            return await ctx.send("❌ Aucun salon détecté.")

        channel = msg_channel.channel_mentions[0]

        LOG_CHANNELS[log_type] = channel.id

        await ctx.send(f"✔️ Log `{log_type}` configuré dans {channel.mention} !")

    # 🔥 AUTO-LOG DES COMMANDES VALIDES
    @commands.Cog.listener()
    async def on_command(self, ctx):
        if ctx.command is None:
            return  # ignore les commandes invalides

        await send_log(
            self.bot,
            "commands",
            f"{ctx.author} a utilisé : {ctx.command}",
            ctx
        )

def setup(bot):
    bot.add_cog(Logs(bot))