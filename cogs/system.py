import nextcord
from nextcord.ext import commands
from nextcord import ui
from config import AUTHORIZED_ROLE_ID

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
            nextcord.SelectOption(label="🎮 Jeux", description="Commandes de jeux"),
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

        # ============================
        # LISTES DE COMMANDES + DESCRIPTIONS
        # ============================

        commands_dict = {
            "🎙️ Vocal": {
                # Déplacements
                "moove": "Déplace un utilisateur vers un autre salon vocal.",
                "move": "Alias de moove.",
                "mooveusers": "Déplace plusieurs utilisateurs sélectionnés.",
                "mooverandom": "Déplace un utilisateur aléatoirement.",
                "mooverandomusers": "Déplace plusieurs utilisateurs aléatoires.",
                "mooveall": "Déplace tous les utilisateurs du salon.",
                "mooveallrandom": "Déplace tous les utilisateurs aléatoirement.",
                "mooveserver": "Déplace tout le serveur vers un salon.",
                "mooveeveryone": "Déplace tout le serveur vers un salon.",
                "back": "Ramène les utilisateurs à leur salon précédent.",

                # Shuffle
                "shuffle start": "Commence un shuffle vocal.",
                "shufflestop": "Arrête le shuffle vocal.",

                # Rotation
                "rotateusers": "Fait tourner les utilisateurs entre les salons.",
                "rotateall": "Fait tourner tout le monde.",
                "rotaterandom": "Rotation aléatoire.",
                "rotationrandom": "Rotation aléatoire.",
                "rotategroups": "Rotation par groupes.",
                "rotationgroups": "Rotation par groupes.",

                # Random teams / split / assign
                "randompair": "Crée des paires aléatoires.",
                "randomteams": "Crée des équipes aléatoires.",
                "randomsplit": "Sépare en deux groupes.",
                "randomassign": "Assigne aléatoirement des utilisateurs.",

                # Gestion vocale
                "clearvoice": "Vide un salon vocal.",
                "clearcategory": "Vide toute une catégorie vocale.",
                "lockvoice": "Verrouille un salon vocal.",
                "unlockvoice": "Déverrouille un salon vocal.",
                "muteall": "Mute tout le monde.",
                "unmuteall": "Unmute tout le monde.",
                "deafenall": "Rend tout le monde sourd.",
                "undeafenall": "Rend tout le monde audible.",

                # Fun / troll
                "spin": "Fait tourner un utilisateur.",
                "spinall": "Fait tourner tout le monde.",
                "randomtp": "Téléporte un utilisateur aléatoire.",
                "russianroulette": "Kick vocal aléatoire.",
                "randomkickvoice": "Kick vocal aléatoire.",

                # Auto
                "autobalance": "Équilibre automatiquement les salons.",
                "autoregroup": "Regroupe automatiquement.",
                "autosplit": "Sépare automatiquement.",
                "autosort": "Trie automatiquement.",

                # Nuke
                "nukevoice": "Nuke un salon vocal.",
                "nukecategory": "Nuke une catégorie.",
                "nukerandom": "Nuke aléatoire.",
                "nukeshuffle": "Nuke + shuffle.",

                # Stats / logs / utils
                "voicestats": "Affiche les statistiques vocales.",
                "movelog": "Affiche les logs de déplacement.",
                "whoisvoice": "Montre où se trouve un utilisateur.",
                "listvoice": "Liste les utilisateurs en vocal.",

                # Bot actions
                "joinme": "Fait rejoindre le bot ton salon.",
                "join": "Fait rejoindre le bot un salon.",
                "leave": "Fait quitter le bot."
            },

            "🛡️ Modération": {
                "lockchannel": "Verrouille un salon texte.",
                "unlockchannel": "Déverrouille un salon texte.",
                "say": "Fait parler le bot."
            },

            "🎮 Jeux": {
                "devinelenombre": "Jeu : devine le nombre."
            },

            "📊 Système": {
                "stat": "Affiche les statistiques du bot."
            }
        }

        cmds = list(commands_dict[category].items())

        # ============================
        # PAGINATION AUTOMATIQUE
        # ============================

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

        # ============================
        # ENVOI AVEC PAGINATION
        # ============================

        await interaction.response.edit_message(
            embed=pages[0],
            view=PageView(pages)
        )


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
