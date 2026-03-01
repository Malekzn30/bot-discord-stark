import nextcord
from nextcord.ext import commands
import time
from cogs.moderation import COMMAND_ROLES, save_command_roles

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
                    "`lock` `unlock` `slowmode` `slowmode_disable` `massunmute` "
                    "`warn_check` `bulkdelete` `clearbots` `clearembeds` "
                    "`masskick` `massban` `warnlist` `unwarn` `clearwarns`"
                ),
                inline=False
            )

            embed.add_field(
                name="ℹ️ Infos",
                value="`serverinfo` `userinfo` `ping` `uptime` `botinfo` `stats` `roles` `channels` `members_top` `avatar`",
                inline=False
            )

            embed.add_field(
                name="📊 Logs",
                value="`logs_setup` `logs_reset` `logs_status` `logs_clear` `logs_list_categories`",
                inline=False
            )

            embed.add_field(
                name="🛠️ Permissions",
                value="`addrole` `removerole`",
                inline=False
            )

            embed.add_field(
                name="🎮 Jeux",
                value=(
                    "`dice` `coin` `rps` `trivia` `devinelenombre` "
                    "`higher_lower` `slots` `rock_paper_scissors`"
                ),
                inline=False
            )

            embed.add_field(
                name="🎙️ Vocal – Déplacements",
                value=(
                    "`moove` `mooveusers` `mooverandom` `mooverandomusers` "
                    "`mooveall` `mooveallrandom` `mooveserver` `back` "
                    "`moveserver_single` `moveall_category` `movecat_rebalance` "
                    "`move_category_to_category` `voicekick`"
                ),
                inline=False
            )

            embed.add_field(
                name="🎙️ Vocal – Rééquilibrage",
                value=(
                    "`rebalance_category` `rebalanceserver` `autobalance` `autosplit` `autosort` "
                    "`rotateusers` `rotateall` `rotaterandom` `rotategroups` `smartbalance` `moveserver_rebalance`"
                ),
                inline=False
            )

            embed.add_field(
                name="🎙️ Vocal – Shuffle & Nuke",
                value=(
                    "`shuffle` `shufflestop` `spin` `spinall` `randomtp` `nukevoice` "
                    "`nukecategory` `nukerandom` `nukeshuffle` `clearvoice` `clearcategory`"
                ),
                inline=False
            )

            embed.add_field(
                name="🎙️ Vocal – Teams & Pairs",
                value=(
                    "`randomteams` `randomsplit` `randompair` `randomassign` "
                    "`randomkickvoice` `russianroulette` `solo_channels`"
                ),
                inline=False
            )

            embed.add_field(
                name="🎙️ Vocal – Lock & Mute",
                value=(
                    "`lockvoice` `unlockvoice` `muteall` `unmuteall` `deafenall` `undeafenall` "
                    "`voice_mute_all_server` `voice_unmute_all_server` `voice_deafen_all_server`"
                ),
                inline=False
            )

            embed.add_field(
                name="🎙️ Vocal – Info & Config",
                value=(
                    "`voicestats` `movelog` `whoisvoice` `listvoice` `joinme` `join` `leave` "
                    "`voiceinfo` `voice_limit` `voice_bitrate`"
                ),
                inline=False
            )

            embed.add_field(
                name="🎙️ Vocal – Info & Bot",
                value=(
                    "`voicestats` `movelog` `whoisvoice` `listvoice` `joinme` `join` `leave`"
                ),
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
            },
            "moove": {
                "description": "Déplacer un membre vers un salon vocal.",
                "usage": "+moove <@membre> <#salon>",
                "exemple": "+moove @User #vocal"
            },
            "rebalance_category": {
                "description": "Rééquilibrer une catégorie vocale (répartir les gens équitablement).",
                "usage": "+rebalance_category <ID_CAT>",
                "exemple": "+rebalance_category 123456789"
            },
            "moveserver_rebalance": {
                "description": "Déplacer tout le serveur vers une catégorie et rééquilibrer.",
                "usage": "+moveserver_rebalance <ID_CAT>",
                "exemple": "+moveserver_rebalance 123456789"
            },
            "rebalanceserver": {
                "description": "Rééquilibrer tout le serveur dans TOUTES les catégories vocales.",
                "usage": "+rebalanceserver",
                "exemple": "+rebalanceserver"
            },
            "moveserver_single": {
                "description": "Déplacer TOUS les membres du serveur vers 1 seul salon.",
                "usage": "+moveserver_single <#salon>",
                "exemple": "+moveserver_single #vocal-principal"
            },
            "randomteams": {
                "description": "Créer des équipes aléatoires dans le vocal.",
                "usage": "+randomteams <NOMBRE>",
                "exemple": "+randomteams 4"
            },
            "voicestats": {
                "description": "Afficher les statistiques vocales du serveur.",
                "usage": "+voicestats",
                "exemple": "+voicestats"
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
    @commands.command(name="botinfo")
    async def botinfo(self, ctx):
        embed = nextcord.Embed(title="🤖 Infos du bot", color=0x3498db)
        embed.add_field(name="Nom", value=self.bot.user.name, inline=False)
        embed.add_field(name="ID", value=self.bot.user.id, inline=False)
        embed.add_field(name="Latence", value=f"{round(self.bot.latency * 1000)}ms", inline=False)
        embed.add_field(name="Uptime", value=f"{int(time.time() - self.bot.start_time)}s", inline=False)
        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        await ctx.send(embed=embed)

    @commands.command(name="stats")
    async def stats(self, ctx):
        embed = nextcord.Embed(title="📊 Stats du serveur", color=0x3498db)
        embed.add_field(name="Serveur", value=ctx.guild.name, inline=False)
        embed.add_field(name="Membres", value=ctx.guild.member_count, inline=False)
        embed.add_field(name="Salons textuels", value=len(ctx.guild.text_channels), inline=False)
        embed.add_field(name="Salons vocaux", value=len(ctx.guild.voice_channels), inline=False)
        embed.add_field(name="Rôles", value=len(ctx.guild.roles), inline=False)
        embed.add_field(name="Catégories", value=len(ctx.guild.categories), inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="roles")
    async def roles(self, ctx):
        roles = [r.mention for r in ctx.guild.roles if r.name != '@everyone'][:25]
        embed = nextcord.Embed(title="🏷️ Rôles du serveur", description=", ".join(roles) or "Aucun rôle", color=0x3498db)
        await ctx.send(embed=embed)

    @commands.command(name="channels")
    async def channels(self, ctx):
        desc = ""
        for ch in ctx.guild.text_channels[:20]:
            desc += f"• {ch.mention}\n"
        embed = nextcord.Embed(title="💬 Salons textuels", description=desc or "Aucun", color=0x3498db)
        await ctx.send(embed=embed)

    @commands.command(name="members_top")
    async def members_top(self, ctx, limit: int = 5):  # Limité à 5 au lieu de 10
        if limit > 10:
            limit = 10  # Max 10
        members = sorted(ctx.guild.members, key=lambda m: m.joined_at)[-limit:]
        desc = ""
        for i, m in enumerate(reversed(members), 1):
            desc += f"{i}. {m.mention} ({m.joined_at.strftime('%d/%m/%Y')})\n"
        embed = nextcord.Embed(title=f"👥 Top {limit} plus récents", description=desc, color=0x3498db)
        await ctx.send(embed=embed)

    @commands.command(name="avatar")
    async def avatar(self, ctx, member: nextcord.Member = None):
        member = member or ctx.author
        embed = nextcord.Embed(title=f"Avatar de {member.name}", color=0x3498db)
        embed.set_image(url=member.avatar.url if member.avatar else None)
        await ctx.send(embed=embed)
    @commands.command(name="addrole")
    @commands.has_permissions(administrator=True)
    async def addrole(self, ctx, command_name: str = None, role: nextcord.Role = None):
        if not command_name or role is None:
            return await ctx.send("❌ Utilise : `+addrole <commande> <@rôle>`")

        cfg = COMMAND_ROLES
        allowed = cfg.get(command_name)
        if allowed is None:
            cfg[command_name] = [role.id]
        elif role.id in allowed:
            return await ctx.send("✅ Ce rôle est déjà autorisé pour cette commande.")
        else:
            allowed.append(role.id)

        save_command_roles(cfg)
        await ctx.send(f"✅ {role.mention} autorisé pour la commande `{command_name}`.")

    @commands.command(name="removerole")
    @commands.has_permissions(administrator=True)
    async def removerole(self, ctx, command_name: str = None, role: nextcord.Role = None):
        if not command_name or role is None:
            return await ctx.send("❌ Utilise : `+removerole <commande> <@rôle>`")

        cfg = COMMAND_ROLES
        allowed = cfg.get(command_name)
        if not allowed or role.id not in allowed:
            return await ctx.send("❌ Ce rôle n'est pas autorisé pour cette commande.")

        allowed.remove(role.id)
        save_command_roles(cfg)
        await ctx.send(f"✅ {role.mention} retiré pour la commande `{command_name}`.")

def setup(bot):
    bot.add_cog(System(bot))
