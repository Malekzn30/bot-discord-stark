import nextcord
from nextcord.ext import commands
import time
from cogs.moderation import COMMAND_ROLES, save_command_roles

# interactive help content ---------------------------------------------------
HELP_CATEGORIES = {
    "🛡️ Modération": (
        "`warn` `kick` `ban` `unban` `tempban` `softban` `mute` `unmute` "
        "`timeout` `untimeout` `clear` `clearuser` `lock` `unlock` "
        "`slowmode` `slowmode_disable` `massunmute` `warn_check` "
        "`bulkdelete` `clearbots` `clearembeds` `masskick` `massban` "
        "`warnlist` `unwarn` `clearwarns`") ,
    "ℹ️ Infos": "`serverinfo` `userinfo` `ping` `uptime` `botinfo` `stats` `roles` `channels` `members_top` `avatar`,",
    "📊 Logs": "`logs_setup` `logs_reset` `logs_status` `logs_clear` `logs_list_categories`",
    "🛠️ Permissions": "`addrole` `removerole`",
    "🎮 Jeux": "`dice` `coin` `rps` `trivia` `devinelenombre` `higher_lower` `slots` `rock_paper_scissors`",
    "🎙️ Vocal": (
        "`moove` `mooveusers` `mooverandom` `mooverandomusers` `mooveall` `mooveallrandom` "
        "`mooveserver` `back` `moveserver_single` `moveall_category` `movecat_rebalance` "
        "`move_category_to_category` `voicekick` `rebalance_category` `rebalanceserver` "
        "`autobalance` `autosplit` `autosort` `rotateusers` `rotateall` `rotaterandom` "
        "`rotategroups` `smartbalance` `moveserver_rebalance` `shuffle` `shufflestop` "
        "`spin` `spinall` `randomtp` `nukevoice` `nukecategory` `nukerandom` "
        "`nukeshuffle` `clearvoice` `clearcategory` `randomteams` `randomsplit` "
        "`randompair` `randomassign` `randomkickvoice` `russianroulette` `solo_channels` "
        "`lockvoice` `unlockvoice` `muteall` `unmuteall` `deafenall` `undeafenall` "
        "`voice_mute_all_server` `voice_unmute_all_server` `voice_deafen_all_server` "
        "`voicestats` `movelog` `whoisvoice` `listvoice` `joinme` `join` `leave` "
        "`voiceinfo` `voice_limit` `voice_bitrate`"),
    "🎙️ Divers": "(aucune pour l'instant)",
    "🎫 Tickets": (
        "`ticket` `ticket setup` `ticket setup wizard` `ticket setup category` "
        "`ticket setup logs` `ticket setup title` `ticket setup description` "
        "`ticket setup addmanager` `ticket setup removemanager` "
        "`ticket setup adddeletor` `ticket setup removedeletor` "
        "`ticket setup access_add` `ticket setup access_remove` "
        "`ticket setup panel_add` `ticket setup panel_remove` `ticket setup panel_list` "
        "`ticket claim` `ticket close` `ticket delete`" )
}


def create_main_help_embed():
    embed = nextcord.Embed(
        title="📚 AIDE – Commandes disponibles",
        description="Cliquez sur l'un des boutons ci-dessous pour voir les commandes de chaque catégorie.",
        color=0x3498db
    )
    return embed


def paginate_commands(cmd_string: str, per_page: int = 10):
    """Return a list of pages, each containing up to `per_page` commands."""
    items = cmd_string.split()
    pages = []
    for i in range(0, len(items), per_page):
        pages.append(" ".join(items[i : i + per_page]))
    return pages


def create_category_page_embed(label: str, pages: list[str], page_index: int):
    """Build an embed for a specific page of a category."""
    desc = pages[page_index]
    embed = nextcord.Embed(
        title=f"📖 {label} (page {page_index + 1}/{len(pages)})",
        description=desc,
        color=0x3498db,
    )
    embed.set_footer(text="⬅️ Appuyez sur Retour pour revenir à la liste des catégories.")
    return embed


class HelpButton(nextcord.ui.Button):
    def __init__(self, label: str):
        super().__init__(label=label, style=nextcord.ButtonStyle.secondary)
        self.label = label

    async def callback(self, interaction: nextcord.Interaction):
        # build pages for the selected category
        cmds = HELP_CATEGORIES.get(self.label, "")
        pages = paginate_commands(cmds, per_page=10)
        embed = create_category_page_embed(self.label, pages, 0)
        view = CategoryView(self.label, pages)
        await interaction.response.edit_message(embed=embed, view=view)


class NavButton(nextcord.ui.Button):
    def __init__(self, direction: str, parent: "CategoryView"):
        label = "◀️" if direction == "prev" else "▶️"
        super().__init__(label=label, style=nextcord.ButtonStyle.secondary)
        self.direction = direction
        self.parent_view_ref = parent

    async def callback(self, interaction: nextcord.Interaction):
        view: CategoryView = self.parent_view_ref
        if self.direction == "prev":
            view.current_page = (view.current_page - 1) % len(view.pages)
        else:
            view.current_page = (view.current_page + 1) % len(view.pages)
        embed = create_category_page_embed(view.label, view.pages, view.current_page)
        await interaction.response.edit_message(embed=embed, view=view)


class CategoryView(nextcord.ui.View):
    def __init__(self, label: str, pages: list[str]):
        super().__init__(timeout=180)
        self.label = label
        self.pages = pages
        self.current_page = 0

        # add navigation buttons only if more than one page
        if len(pages) > 1:
            self.add_item(NavButton("prev", self))
            self.add_item(NavButton("next", self))
        # always allow backing out to main help
        self.add_item(BackButton())


class BackButton(nextcord.ui.Button):
    def __init__(self):
        super().__init__(label="⬅️ Retour", style=nextcord.ButtonStyle.primary)

    async def callback(self, interaction: nextcord.Interaction):
        embed = create_main_help_embed()
        view = HelpView()
        await interaction.response.edit_message(embed=embed, view=view)


class HelpView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        for label in HELP_CATEGORIES.keys():
            self.add_item(HelpButton(label))


class BackView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(BackButton())

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
            # interactive menu with buttons selects
            embed = create_main_help_embed()
            view = HelpView()
            await ctx.send(embed=embed, view=view)
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
                "description": "Ouvrir un ticket (préfixe uniquement ; `/ticket` n'est pas utilisable).",
                "usage": "+ticket",
                "exemple": "+ticket"
            },
            "ticket setup": {
                "description": "Voir/modifier la configuration des tickets (admin) via boutons ; vous pouvez créer/éditer des panels, leurs formulaires et options.",
                "usage": "+ticket setup",
                "exemple": "+ticket setup"
            },
            "ticket setup wizard": {
                "description": "Assistant interactif pas-à-pas pour configurer les tickets.",
                "usage": "+ticket setup wizard",
                "exemple": "+ticket setup wizard"
            },
            "ticket claim": {
                "description": "Réclamer un ticket (staff). Usage en préfixe seulement (+ticket claim).",
                "usage": "+ticket claim",
                "exemple": "+ticket claim"
            },
            "ticket setup category": {
                "description": "Définit la catégorie où les tickets seront créés (admin).",
                "usage": "+ticket setup category <#catégorie>",
                "exemple": "+ticket setup category #tickets"
            },
            "ticket setup logs": {
                "description": "Spécifie le salon de logs des tickets (admin).",
                "usage": "+ticket setup logs <#salon>",
                "exemple": "+ticket setup logs #logs-tickets"
            },
            "ticket setup title": {
                "description": "Change le titre de l'embed des tickets (admin).",
                "usage": "+ticket setup title <texte>",
                "exemple": "+ticket setup title 🎫 Assistance"
            },
            "ticket setup description": {
                "description": "Modifie la description de l'embed initial (admin).",
                "usage": "+ticket setup description <texte>",
                "exemple": "+ticket setup description Expliquez votre problème"
            },
            "ticket setup addmanager": {
                "description": "Ajoute un rôle comme gestionnaire (admin). alias +ticket setup add-manager / add_manager",
                "usage": "+ticket setup addmanager <@rôle>",
                "exemple": "+ticket setup addmanager @Modérateur"
            },
            "ticket setup removemanager": {
                "description": "Retire un rôle de la liste des gestionnaires (admin). alias +ticket setup remove-manager / remove_manager",
                "usage": "+ticket setup removemanager <@rôle>",
                "exemple": "+ticket setup removemanager @Modérateur"
            },
            "ticket setup adddeletor": {
                "description": "Ajoute un rôle autorisé à supprimer des tickets (admin). alias +ticket setup add-deletor / add_deletor",
                "usage": "+ticket setup adddeletor <@rôle>",
                "exemple": "+ticket setup adddeletor @Admin"
            },
            "ticket setup removedeletor": {
                "description": "Retire un rôle autorisé à supprimer des tickets (admin). alias +ticket setup remove-deletor / remove_deletor",
                "usage": "+ticket setup removedeletor <@rôle>",
                "exemple": "+ticket setup removedeletor @Admin"
            },
            "ticket setup access_add": {
                "description": "Donne l'accès aux tickets à un rôle (admin). alias +ticket setup addaccess / access-add",
                "usage": "+ticket setup access_add <@rôle>",
                "exemple": "+ticket setup access_add @Membre"
            },
            "ticket setup access_remove": {
                "description": "Retire l'accès aux tickets d'un rôle (admin). alias +ticket setup removeaccess / access-remove",
                "usage": "+ticket setup access_remove <@rôle>",
                "exemple": "+ticket setup access_remove @Visiteur"
            },
            "ticket setup panel_add": {
                "description": "Crée un panel de ticket interactif dans un salon (admin).",
                "usage": "+ticket setup panel_add <#salon> <#catégorie> [titre] [description]",
                "exemple": "+ticket setup panel_add #accueil #tickets '🎫 Help' 'Cliquez pour ouvrir un ticket.'"
            },
            "ticket setup panel_remove": {
                "description": "Supprime un panel précédemment créé (admin).",
                "usage": "+ticket setup panel_remove <id_panel>",
                "exemple": "+ticket setup panel_remove 1584123456789"
            },
            "ticket setup panel_list": {
                "description": "Liste tous les panels de ticket configurés.",
                "usage": "+ticket setup panel_list",
                "exemple": "+ticket setup panel_list"
            },
            "ticket close": {
                "description": "Fermer le ticket courant (préfixe uniquement).",
                "usage": "+ticket close [raison]",
                "exemple": "+ticket close Résolu"
            },
            "ticket delete": {
                "description": "Supprimer un ticket (rôle autorisé, préfixe uniquement).",
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

    @commands.command(name="embed")
    @commands.has_permissions(administrator=True)
    async def create_embed(self, ctx, title: str, description: str, *, footer: str = None):
        """Créer un embed personnalisé avec icône du serveur et footer du bot
        
        Usage: +embed "Titre" "Description" "Footer optionnel"
        """
        # Créer l'embed avec l'icône du serveur
        embed = nextcord.Embed(
            title=title,
            description=description,
            color=0x3498db,
            timestamp=ctx.message.created_at
        )
        
        # Ajouter l'icône du serveur si disponible
        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)
        
        # Ajouter le footer avec le nom du bot
        if footer:
            embed.set_footer(text=f"{footer} • {ctx.bot.user.name}", icon_url=ctx.bot.user.display_avatar.url)
        else:
            embed.set_footer(text=f"{ctx.bot.user.name}", icon_url=ctx.bot.user.display_avatar.url)
        
        # Ajouter l'auteur du message
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)
        await ctx.message.delete()  # Supprimer la commande d'origine

def setup(bot):
    bot.add_cog(System(bot))
