import nextcord
from nextcord.ext import commands
from nextcord import ui
from config import AUTHORIZED_ROLE_ID

# ============================================================
# PERMISSION CHECK
# ============================================================

def has_role():
    async def predicate(ctx):
        role = ctx.guild.get_role(AUTHORIZED_ROLE_ID)
        return role in ctx.author.roles
    return commands.check(predicate)

# ============================================================
# PAGINATION VIEW
# ============================================================

class PageView(ui.View):
    def __init__(self, pages):
        super().__init__(timeout=None)
        self.pages = pages
        self.index = 0

    @ui.button(label="⬅️", style=nextcord.ButtonStyle.primary)
    async def previous(self, button, interaction):
        self.index = (self.index - 1) % len(self.pages)
        await interaction.response.edit_message(embed=self.pages[self.index], view=self)

    @ui.button(label="➡️", style=nextcord.ButtonStyle.primary)
    async def next(self, button, interaction):
        self.index = (self.index + 1) % len(self.pages)
        await interaction.response.edit_message(embed=self.pages[self.index], view=self)

# ============================================================
# MENU DÉROULANT
# ============================================================

class CategorySelect(ui.Select):
    def __init__(self, bot):
        self.bot = bot

        options = [
            nextcord.SelectOption(label="🎙️ Vocal", description="Commandes vocales"),
            nextcord.SelectOption(label="🛡️ Modération", description="Commandes de modération"),
            nextcord.SelectOption(label="📊 Système", description="Commandes système"),
        ]

        super().__init__(
            placeholder="Choisis une catégorie…",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: nextcord.Interaction):
        category = self.values[0]

        # ============================================================
        # LISTE DES COMMANDES PAR CATÉGORIE
        # ============================================================

        commands_dict = {

            # ====================================================
            # VOCAL
            # ====================================================
            "🎙️ Vocal": {

                # Déplacements
                "moove": "Déplace un utilisateur vers un salon vocal.",
                "mooveusers": "Déplace plusieurs utilisateurs vers un salon.",
                "mooverandom": "Déplace un utilisateur dans un salon aléatoire.",
                "mooverandomusers": "Déplace plusieurs utilisateurs aléatoirement.",
                "mooveall": "Déplace toute ta vocal vers un salon.",
                "mooveallrandom": "Déplace toute ta vocal aléatoirement.",
                "mooveserver": "Déplace tout le serveur vers un salon.",
                "back": "Ramène les utilisateurs à leur salon précédent.",

                # Shuffle
                "shuffle start": "Commence un shuffle vocal.",
                "shufflestop": "Arrête le shuffle vocal.",

                # Rotation
                "rotateusers": "Fait tourner des utilisateurs entre les salons.",
                "rotateall": "Fait tourner toute la vocal.",
                "rotaterandom": "Rotation aléatoire.",
                "rotategroups": "Rotation par groupes.",

                # Random teams / split / assign
                "randompair": "Crée des duos aléatoires.",
                "randomteams": "Crée des équipes aléatoires.",
                "randomsplit": "Sépare en deux groupes.",
                "randomassign": "Assigne chaque membre à un salon aléatoire.",

                # Gestion vocale
                "clearvoice": "Vide un salon vocal.",
                "clearcategory": "Vide une catégorie vocale.",
                "lockvoice": "Verrouille un salon vocal.",
                "unlockvoice": "Déverrouille un salon vocal.",
                "muteall": "Mute tout le monde.",
                "unmuteall": "Unmute tout le monde.",
                "deafenall": "Rend tout le monde sourd.",
                "undeafenall": "Rend tout le monde audible.",

                # Fun / troll
                "spin": "Fait tourner un utilisateur.",
                "spinall": "Fait tourner toute la vocal.",
                "randomtp": "Téléporte un utilisateur aléatoirement.",
                "russianroulette": "Choisit un perdant aléatoire.",
                "randomkickvoice": "Kick vocal aléatoire.",

                # Auto
                "autobalance": "Équilibre automatiquement les salons.",
                "autoregroup": "Regroupe tout le monde dans un salon.",
                "autosplit": "Sépare automatiquement en X salons.",
                "autosort": "Trie les membres par rôle.",

                # Nuke
                "nukevoice": "Vide un salon vocal.",
                "nukecategory": "Vide une catégorie vocale.",
                "nukerandom": "Déplace tout le monde aléatoirement.",
                "nukeshuffle": "Shuffle massif.",

                # Stats / logs / utils
                "voicestats": "Affiche les statistiques vocales.",
                "movelog": "Historique des déplacements.",
                "whoisvoice": "Montre où se trouve un utilisateur.",
                "listvoice": "Liste les salons vocaux et leurs membres.",

                # Bot actions
                "joinme": "Fait rejoindre le bot ton salon.",
                "join": "Fait rejoindre le bot un salon.",
                "leave": "Fait quitter le bot."
            },

            # ====================================================
            # MODÉRATION
            # ====================================================
            "🛡️ Modération": {

                # Actions
                "kick": "Expulse un membre.",
                "ban": "Bannit un membre.",
                "unban": "Débannit un utilisateur.",
                "tempban": "Ban temporaire.",
                "softban": "Ban + unban (supprime messages).",
                "masskick": "Kick plusieurs membres.",
                "massban": "Ban plusieurs membres.",

                # Mute / timeout
                "mute": "Mute un membre.",
                "unmute": "Unmute un membre.",
                "timeout": "Timeout un membre.",
                "untimeout": "Retire le timeout.",

                # Warns (SQLite)
                "warn": "Ajoute un avertissement.",
                "warnlist": "Liste les avertissements.",
                "unwarn": "Retire un avertissement.",
                "clearwarns": "Supprime tous les avertissements.",

                # Gestion salon
                "lock": "Verrouille le salon.",
                "unlock": "Déverrouille le salon.",
                "slowmode": "Active un slowmode.",

                # Messages
                "clear": "Supprime des messages.",
                "clearuser": "Supprime les messages d’un membre.",
                "clearbots": "Supprime les messages des bots.",
                "clearembeds": "Supprime les embeds.",

                # Infos
                "userinfo": "Infos sur un membre.",
                "serverinfo": "Infos sur le serveur.",

                # Nicknames
                "setnick": "Change le pseudo d’un membre.",
                "resetnick": "Réinitialise le pseudo."
            },

            # ====================================================
            # SYSTÈME
            # ====================================================
            "📊 Système": {
                "help": "Affiche ce menu d’aide.",
                "stat": "Affiche les statistiques du bot."
            }
        }

        # ============================================================
        # CRÉATION DES PAGES
        # ============================================================

        cmds = list(commands_dict[category].items())
        pages = []
        per_page = 10

        for i in range(0, len(cmds), per_page):
            chunk = cmds[i:i + per_page]

            description = "\n".join(
                f"**`{name}`** — {desc}"
                for name, desc in chunk
            )

            embed = nextcord.Embed(
                title=f"{category} — Page {len(pages)+1}",
                description=description,
                color=0x3498db
            )

            pages.append(embed)

        await interaction.response.edit_message(
            embed=pages[0],
            view=PageView(pages)
        )

# ============================================================
# HELP VIEW
# ============================================================

class HelpView(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.add_item(CategorySelect(bot))

# ============================================================
# COG SYSTEM
# ============================================================

class System(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    @has_role()
    async def help(self, ctx):
        embed = nextcord.Embed(
            title="📘 Aide du bot",
            description="Choisis une catégorie dans le menu ci‑dessous.",
            color=0x3498db
        )

        await ctx.send(embed=embed, view=HelpView(self.bot))

    @commands.command(name="stat")
    @has_role()
    async def stat(self, ctx):
        import time
        uptime = int(time.time() - self.bot.start_time)
        embed = nextcord.Embed(title="📊 Statistiques", color=0x3498db)
        embed.add_field(name="Uptime", value=f"{uptime} sec")
        embed.add_field(name="Ping", value=f"{round(self.bot.latency * 1000)} ms")
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(System(bot))
