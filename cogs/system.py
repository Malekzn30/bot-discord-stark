import nextcord
from nextcord.ext import commands
import time

class System(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help(self, ctx, command: str = None):
        if not command:
            # HELP GÉNÉRAL
            embed = nextcord.Embed(
                title="📚 AIDE - Commandes disponibles",
                description="Tape `+help <commande>` pour plus de détails.",
                color=0x3498db
            )
            
            embed.add_field(
                name="🛡️ Modération",
                value="`warn` `kick` `ban` `unban` `tempban` `softban` `mute` `unmute` `timeout` `untimeout` `clear` `lock` `unlock` `slowmode`",
                inline=False
            )
            
            embed.add_field(
                name="📊 Logs",
                value="`logs_setup` `logs_reset` `logs_status`",
                inline=False
            )
            
            embed.add_field(
                name="ℹ️ Infos",
                value="`serverinfo` `userinfo` `ping` `uptime`",
                inline=False
            )
            
            embed.set_footer(text="Prefix: +")
            return await ctx.send(embed=embed)
        
        # HELP D'UNE COMMANDE SPÉCIFIQUE
        helps = {
            "warn": {
                "description": "Avertir un membre",
                "usage": "+warn <@membre> [raison]",
                "exemple": "+warn @User Spam excessif"
            },
            "kick": {
                "description": "Expulser un membre du serveur",
                "usage": "+kick <@membre> [raison]",
                "exemple": "+kick @User Comportement toxique"
            },
            "ban": {
                "description": "Bannir un membre du serveur",
                "usage": "+ban <@membre> [raison]",
                "exemple": "+ban @User Harcèlement"
            },
            "tempban": {
                "description": "Bannir temporairement un membre",
                "usage": "+tempban <@membre> <minutes> [raison]",
                "exemple": "+tempban @User 60 Spam"
            },
            "mute": {
                "description": "Rendre muet un membre (rôle)",
                "usage": "+mute <@membre> [raison]",
                "exemple": "+mute @User Langage inapproprié"
            },
            "timeout": {
                "description": "Timeout un membre (ne peut pas discuter)",
                "usage": "+timeout <@membre> <minutes>",
                "exemple": "+timeout @User 10"
            },
            "clear": {
                "description": "Supprimer des messages",
                "usage": "+clear <nombre>",
                "exemple": "+clear 50"
            },
            "logs_setup": {
                "description": "Configurer un salon pour les logs",
                "usage": "+logs_setup <catégorie> <#salon>",
                "exemple": "+logs_setup warn #logs-warns"
            },
            "ping": {
                "description": "Vérifier la latence du bot",
                "usage": "+ping",
                "exemple": "+ping"
            },
            "uptime": {
                "description": "Voir depuis combien de temps le bot est actif",
                "usage": "+uptime",
                "exemple": "+uptime"
            }
        }
        
        cmd = helps.get(command.lower())
        if not cmd:
            return await ctx.send(f"❌ Commande `{command}` non trouvée. Tape `+help` pour voir toutes les commandes.")
        
        embed = nextcord.Embed(
            title=f"📖 Aide - {command}",
            description=cmd["description"],
            color=0x3498db
        )
        embed.add_field(name="📝 Usage", value=f"`{cmd['usage']}`", inline=False)
        embed.add_field(name="💡 Exemple", value=f"`{cmd['exemple']}`", inline=False)
        
        await ctx.send(embed=embed)

    @commands.command(name="ping")
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        await ctx.send(f"🏓 Pong! **{latency}ms**")

    @commands.command(name="uptime")
    async def uptime(self, ctx):
        uptime_seconds = int(time.time() - self.bot.start_time)
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        await ctx.send(f"⏱️ Uptime: **{hours}h {minutes}m {seconds}s**")

def setup(bot):
    bot.add_cog(System(bot))
