import nextcord
from nextcord.ext import commands
import time

class System(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help(self, ctx, command: str = None):
        """
        +help            → liste générale (1 seul embed)
        +help <commande> → détails sur la commande (1 seul embed)
        """
        if command is None:
            # --- aide générale ------------------------------------------------
            embed = nextcord.Embed(
                title="📚 AIDE – Commandes disponibles",
                description="Tapez `+help <commande>` pour obtenir des détails.",
                color=0x3498db
            )

            embed.add_field(
                name="🛡️ Modération",
                value=(
                    "`warn` `kick` `ban` `unban` `tempban` `softban` `mute` "
                    "`unmute` `timeout` `untimeout` `clear` `clearuser` "
                    "`lock` `unlock` `slowmode`"
                ),
                inline=False
            )

            embed.add_field(
                name="ℹ️ Infos",
                value="`serverinfo` `userinfo` `ping` `uptime`",
                inline=False
            )

            embed.add_field(
                name="📊 Logs",
                value="`logs_setup` `logs_reset` `logs_status`",
                inline=False
            )

            embed.add_field(
                name="🛠️ Permissions",
                value="`addrole` `removerole`",
                inline=False
            )

            embed.add_field(
                name="🎮 Jeux",
                value="`dice` `coin` `rps` `trivia`",
                inline=False
            )

            embed.add_field(
                name="🎙️ Divers",
                value="(aucune pour l'instant)",
                inline=False
            )

            embed.add_field(
                name="🎫 Tickets",
                value=(
                    "`ticket` `ticket setup` `ticket setup category` "
                    "`ticket setup logs` `ticket setup title` "
                    "`ticket setup description` `ticket setup addmanager` "
                    "`ticket setup removemanager` `ticket setup adddeletor` "
                    "`ticket setup removedeletor` `ticket setup access_add` "
                    "`ticket setup access_remove` `ticket claim` "
                    "`ticket close` `ticket delete`"
                ),
                inline=False
            )

            embed.set_footer(text="Préfixe : +")
            await ctx.send(embed=embed)
            return

        # --- aide spécifique ------------------------------------------------
        helps = {
            "warn": {
                "description": "Avertir un membre (ajoute automatiquement le rôle de warn).",
                "usage": "+warn <@membre> [raison]",
                "exemple": "+warn @User Spam excessif"
            },
            "kick": {
                "description": "Expulser un membre du serveur.",
                "usage": "+kick <@membre> [raison]",
                "exemple": "+kick @User Comportement toxique"
            },
            "ban": {
                "description": "Bannir un membre du serveur.",
                "usage": "+ban <@membre> [raison]",
                "exemple": "+ban @User Harcèlement"
            },
            "tempban": {
                "description": "Bannir temporairement un membre.",
                "usage": "+tempban <@membre> <minutes> [raison]",
                "exemple": "+tempban @User 60 Spam"
            },
            "mute": {
                "description": "Ajouter le rôle muet à un membre.",
                "usage": "+mute <@membre> [raison]",
                "exemple": "+mute @User Langage inapproprié"
            },
            "timeout": {
                "description": "Placer un membre en timeout (impossible de parler).",
                "usage": "+timeout <@membre> <minutes>",
                "exemple": "+timeout @User 10"
            },
            "clear": {
                "description": "Supprimer un nombre de messages.",
                "usage": "+clear <nombre>",
                "exemple": "+clear 50"
            },
            "logs_setup": {
                "description": "Configurer un salon pour une catégorie de logs.",
                "usage": "+logs_setup <catégorie> <#salon>",
                "exemple": "+logs_setup warn #logs-warns"
            },
            "logs_reset": {
                "description": "Réinitialiser un salon de logs déjà configuré.",
                "usage": "+logs_reset <catégorie>",
                "exemple": "+logs_reset warn"
            },
            "logs_status": {
                "description": "Voir l'état de toutes les catégories de logs.",
                "usage": "+logs_status",
                "exemple": "+logs_status"
            },
            "addrole": {
                "description": "Autoriser un rôle à utiliser une commande.",
                "usage": "+addrole <commande> <@rôle>",
                "exemple": "+addrole warn @Modérateur"
            },
            "removerole": {
                "description": "Retirer l'autorisation d'une commande à un rôle.",
                "usage": "+removerole <commande> <@rôle>",
                "exemple": "+removerole warn @Modérateur"
            },
            "ping": {
                "description": "Mesurer la latence du bot.",
                "usage": "+ping",
                "exemple": "+ping"
            },
            "uptime": {
                "description": "Afficher le temps d'activité du bot.",
                "usage": "+uptime",
                "exemple": "+uptime"
            },
            "ticket": {
                "description": "Ouvrir un ticket. +ticket <sous‑commande> pour la configuration.",
                "usage": "+ticket",
                "exemple": "+ticket"
            },
            "ticket setup": {
                "description": "Voir/modifier la configuration des tickets (admin).",
                "usage": "+ticket setup",
                "exemple": "+ticket setup"
            },
            "ticket claim": {
                "description": "Réclamer un ticket (staff).",
                "usage": "+ticket claim",
                "exemple": "+ticket claim"
            },
            "ticket close": {
                "description": "Fermer le ticket courant.",
                "usage": "+ticket close [raison]",
                "exemple": "+ticket close Résolu"
            },
            "ticket delete": {
                "description": "Supprimer un ticket (rôle autorisé).",
                "usage": "+ticket delete",
                "exemple": "+ticket delete"
            }
        }

        entry = helps.get(command.lower())
        if entry is None:
            embed = nextcord.Embed(
                title="❌ Commande introuvable",
                description=f"La commande `{command}` n'existe pas.\nTapez `+help` pour la liste complète.",
                color=0xE74C3C
            )
            await ctx.send(embed=embed)
            return

        embed = nextcord.Embed(
            title=f"📖 Aide – {command.lower()}",
            description=entry["description"],
            color=0x3498db
        )
        embed.add_field(name="📝 Usage", value=f"`{entry['usage']}`", inline=False)
        embed.add_field(name="💡 Exemple", value=f"`{entry['exemple']}`", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="ping")
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        await ctx.send(f"🏓 Pong ! **{latency} ms**")

    @commands.command(name="uptime")
    async def uptime(self, ctx):
        uptime_seconds = int(time.time() - self.bot.start_time)
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        await ctx.send(f"⏱️ Uptime : **{hours}h {minutes}m {seconds}s**")

def setup(bot):
    bot.add_cog(System(bot))
