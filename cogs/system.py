import nextcord
from nextcord.ext import commands
import asyncio
import datetime
from config import AUTHORIZED_ROLE_ID

class System(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx, command: str = None):
        """Système d'aide complet avec 150+ commandes"""
        
        if command is None:
            # Page d'accueil avec toutes les catégories
            embed = nextcord.Embed(
                title="🤖 Bot Stark - 150+ Commandes",
                description="**Le bot Discord le plus complet !**\n\nUtilise `+help <catégorie>` pour voir les commandes d'une catégorie.",
                color=0x3498db,
                timestamp=datetime.datetime.now()
            )
            
            embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
            
            # Toutes les catégories avec descriptions
            categories = [
                ("🛡️ Modération", "Gestion serveur et modération avancée", "15 commandes"),
                ("🎤 Vocal", "Gestion complète des salons vocaux", "21 commandes"),
                ("🎮 Jeux", "Jeux et divertissement variés", "10 commandes"),
                ("🎉 Communauté", "Fonctionnalités communautaires", "10 commandes"),
                ("🛠️ Utilitaires", "Commandes utilitaires diverses", "12 commandes"),
                ("😂 Fun", "Commandes d'amusement et divertissement", "10 commandes"),
                ("🚀 Étendu", "Commandes avancées et systèmes", "17 commandes"),
                ("⚙️ Configuration", "Personnalisation complète du bot", "10 commandes"),
                ("📊 Performance", "Monitoring et optimisation", "4 commandes")
            ]
            
            for name, desc, count in categories:
                embed.add_field(
                    name=f"{name} ({count})",
                    value=f"➜ {desc}\n`+help {name.split()[1].lower()}`",
                    inline=True
                )
            
            embed.add_field(
                name="📊 Statistiques",
                value=f"**Total: 150+ commandes** dans 9 catégories\n**Prefixe:** `+`\n**Permissions:** Configurables",
                inline=False
            )
            
            embed.set_footer(text="Utilise +help <commande> pour l'aide détaillée")
            await ctx.send(embed=embed)
            
        elif command.lower() in ["modération", "moderation"]:
            await self.show_moderation_help(ctx)
        elif command.lower() in ["vocal"]:
            await self.show_vocal_help(ctx)
        elif command.lower() in ["jeux"]:
            await self.show_games_help(ctx)
        elif command.lower() in ["communauté", "communaute"]:
            await self.show_community_help(ctx)
        elif command.lower() in ["utilitaires"]:
            await self.show_utility_help(ctx)
        elif command.lower() in ["fun"]:
            await self.show_fun_help(ctx)
        elif command.lower() in ["étendu", "etendu"]:
            await self.show_extended_help(ctx)
        elif command.lower() in ["configuration", "config"]:
            await self.show_config_help(ctx)
        elif command.lower() in ["performance"]:
            await self.show_performance_help(ctx)
        else:
            # Recherche de commande
            await self.search_command(ctx, command)

    async def show_moderation_help(self, ctx):
        """Afficher l'aide de la modération"""
        embed = nextcord.Embed(
            title="🛡️ Modération Avancée (15 commandes)",
            description="Commandes pour gérer et modérer le serveur",
            color=0xE74C3C
        )
        
        commands = [
            ("warn", "Avertir un membre avec système de points", "+warn @membre <raison>", "Admin/Modo"),
            ("warns", "Voir les warns d'un membre", "+warns [@membre]", "Admin/Modo"),
            ("clearwarns", "Supprimer tous les warns d'un membre", "+clearwarns @membre", "Admin"),
            ("mute", "Rendre muet un membre", "+mute @membre [durée] <raison>", "Admin/Modo"),
            ("unmute", "Rendre la parole à un membre", "+unmute @membre", "Admin/Modo"),
            ("tempban", "Bannir temporairement un membre", "+tempban @membre <durée> <raison>", "Admin"),
            ("kick", "Expulser un membre", "+kick @membre <raison>", "Admin/Modo"),
            ("ban", "Bannir un membre", "+ban @membre <raison>", "Admin"),
            ("slowmode", "Activer le mode lent", "+slowmode [secondes]", "Admin/Modo"),
            ("lockdown", "Verrouiller le serveur", "+lockdown", "Admin"),
            ("unlockdown", "Déverrouiller le serveur", "+unlockdown", "Admin"),
            ("modlogs", "Voir les logs de modération", "+modlogs", "Admin/Modo"),
            ("clear", "Supprimer des messages", "+clear <nombre>", "Admin/Modo"),
            ("nuke", "Supprimer tout un salon", "+nuke", "Admin"),
            ("massban", "Bannir plusieurs membres", "+massban @membre1 @membre2...", "Admin")
        ]
        
        for cmd, desc, usage, perm in commands:
            embed.add_field(
                name=f"🔹 {cmd}",
                value=f"**Description:** {desc}\n**Usage:** `{usage}`\n**Permissions:** {perm}",
                inline=False
            )
        
        await ctx.send(embed=embed)

    async def show_vocal_help(self, ctx):
        """Afficher l'aide du vocal"""
        embed = nextcord.Embed(
            title="🎤 Gestion Vocale Complète (21 commandes)",
            description="Commandes pour gérer les salons vocaux",
            color=0x1ABC9C
        )
        
        commands = [
            ("déplacer", "Déplacer un membre en vocal", "+déplacer @membre #salon", "Admin/Modo"),
            ("equilibrer", "Équilibrer les salons vocaux", "+equilibrer @catégorie <nombre>", "Admin/Modo"),
            ("equilibrer_auto", "Équilibrage automatique", "+equilibrer_auto @catégorie", "Admin/Modo"),
            ("immobiles", "Lister les membres immobiles", "+immobiles", "Admin/Modo"),
            ("force_move", "Forcer le déplacement", "+force_move @membre #salon", "Admin/Modo"),
            ("move_all_except", "Déplacer tout sauf un", "+move_all_except @admin #salon", "Admin/Modo"),
            ("move_from_category", "Déplacer d'une catégorie", "+move_from_category #cat #salon", "Admin/Modo"),
            ("shuffle_category", "Mélanger aléatoirement", "+shuffle_category #catégorie", "Admin/Modo"),
            ("gather_all", "Rassembler tout le monde", "+gather_all #salon", "Admin/Modo"),
            ("create_voice_rooms", "Créer des salons vocaux", "+create_voice_rooms #cat <nombre> <nom>", "Admin"),
            ("clone_voice_channel", "Cloner un salon vocal", "+clone_voice_channel #salon <nom>", "Admin"),
            ("swap_channels", "Échanger les membres entre salons", "+swap_channels #salon1 #salon2", "Admin"),
            ("tempvoice", "Créer un salon vocal temporaire", "+tempvoice [nom]", "Tout le monde"),
            ("voice_activity", "Activité détaillée", "+voice_activity #catégorie", "Admin/Modo"),
            ("move_afk", "Déplacer les membres AFK", "+move_afk #afk <minutes>", "Admin/Modo"),
            ("voice_backup", "Sauvegarder distribution", "+voice_backup #catégorie", "Admin"),
            ("voice_restore", "Restaurer distribution", "+voice_restore <fichier>", "Admin"),
            ("voice_limits", "Définir les limites", "+voice_limits #catégorie <max>", "Admin"),
            ("voice_cleanup", "Nettoyer les salons vides", "+voice_cleanup", "Admin/Modo")
        ]
        
        for cmd, desc, usage, perm in commands:
            embed.add_field(
                name=f"🎤 {cmd}",
                value=f"**Description:** {desc}\n**Usage:** `{usage}`\n**Permissions:** {perm}",
                inline=False
            )
        
        await ctx.send(embed=embed)

    async def show_games_help(self, ctx):
        """Afficher l'aide des jeux"""
        embed = nextcord.Embed(
            title="🎮 Jeux et Divertissement (10 commandes)",
            description="Jeux et divertissement variés",
            color=0xF39C12
        )
        
        commands = [
            ("dice", "Lancer un dé", "+dice [faces]", "Tout le monde"),
            ("coin", "Pile ou face", "+coin", "Tout le monde"),
            ("rps", "Pierre feuille ciseaux", "+rps <pierre|feuille|ciseaux>", "Tout le monde"),
            ("devinelenombre", "Jeu de devinette de nombre", "+devinelenombre", "Tout le monde"),
            ("8ball", "Boule magique 8", "+8ball <question>", "Tout le monde"),
            ("truth", "Question pour vérité", "+truth [catégorie]", "Tout le monde"),
            ("dare", "Action pour un défi", "+dare [intensité]", "Tout le monde"),
            ("wyr", "Préfères-tu (Would You Rather)", "+wyr", "Tout le monde"),
            ("rate", "Noter quelque chose", "+rate [chose]", "Tout le monde"),
            ("ship", "Calculer le 'ship' entre deux utilisateurs", "+ship [@user1] [@user2]", "Tout le monde")
        ]
        
        for cmd, desc, usage, perm in commands:
            embed.add_field(
                name=f"🎲 {cmd}",
                value=f"**Description:** {desc}\n**Usage:** `{usage}`\n**Permissions:** {perm}",
                inline=False
            )
        
        await ctx.send(embed=embed)

    async def show_community_help(self, ctx):
        """Afficher l'aide de la communauté"""
        embed = nextcord.Embed(
            title="🎉 Fonctionnalités Communautaires (10 commandes)",
            description="Fonctionnalités communautaires",
            color=0x9B59B6
        )
        
        commands = [
            ("suggest", "Faire une suggestion pour le serveur", "+suggest <suggestion>", "Tout le monde"),
            ("poll", "Créer un sondage", "+poll <question> <option1> <option2> ...", "Admin/Modo"),
            ("giveaway", "Lancer un giveaway", "+giveaway <durée> <prix>", "Admin/Modo"),
            ("reactionrole", "Ajouter un rôle par réaction", "+reactionrole <msg_id> <emoji> @rôle", "Admin"),
            ("serverstats", "Statistiques du serveur", "+serverstats", "Tout le monde"),
            ("userinfo", "Informations sur un utilisateur", "+userinfo [@membre]", "Tout le monde"),
            ("serverinfo", "Informations détaillées sur le serveur", "+serverinfo", "Tout le monde"),
            ("roleinfo", "Informations détaillées sur un rôle", "+roleinfo @rôle", "Tout le monde"),
            ("channelinfo", "Informations sur un salon", "+channelinfo [#salon]", "Tout le monde"),
            ("starboard", "Afficher la starboard du serveur", "+starboard", "Tout le monde")
        ]
        
        for cmd, desc, usage, perm in commands:
            embed.add_field(
                name=f"🎉 {cmd}",
                value=f"**Description:** {desc}\n**Usage:** `{usage}`\n**Permissions:** {perm}",
                inline=False
            )
        
        await ctx.send(embed=embed)

    async def show_utility_help(self, ctx):
        """Afficher l'aide des utilitaires"""
        embed = nextcord.Embed(
            title="🛠️ Utilitaires Avancés (12 commandes)",
            description="Commandes utilitaires diverses",
            color=0x3498db
        )
        
        commands = [
            ("afk", "Mettre son statut AFK", "+afk [raison]", "Tout le monde"),
            ("snipe", "Voir le dernier message supprimé", "+snipe", "Tout le monde"),
            ("editsnipe", "Voir le dernier message modifié", "+editsnipe", "Tout le monde"),
            ("emoji", "Informations sur un émoji", "+emoji <émoji>", "Tout le monde"),
            ("steal", "Ajouter un émoji d'un autre serveur", "+steal <émoji> [nom]", "Admin"),
            ("firstmessage", "Voir le premier message d'un salon", "+firstmessage [#salon]", "Tout le monde"),
            ("createinvite", "Créer une invitation", "+createinvite [#salon] [max_uses] [expires_in]", "Admin/Modo"),
            ("calc", "Calculatrice simple", "+calc <expression>", "Tout le monde"),
            ("remind", "Rappel (format: 1h, 30m, 1d)", "+remind <temps> <message>", "Tout le monde"),
            ("translate", "Traduire un texte", "+translate <langue> <texte>", "Tout le monde"),
            ("reverse", "Inverser un texte", "+reverse <texte>", "Tout le monde")
        ]
        
        for cmd, desc, usage, perm in commands:
            embed.add_field(
                name=f"🛠️ {cmd}",
                value=f"**Description:** {desc}\n**Usage:** `{usage}`\n**Permissions:** {perm}",
                inline=False
            )
        
        await ctx.send(embed=embed)

    async def show_fun_help(self, ctx):
        """Afficher l'aide du fun"""
        embed = nextcord.Embed(
            title="😂 Fun et Divertissement (10 commandes)",
            description="Commandes d'amusement et divertissement",
            color=0xFF69B4
        )
        
        commands = [
            ("meme", "Afficher un mème aléatoire", "+meme [catégorie]", "Tout le monde"),
            ("joke", "Raconter une blague", "+joke", "Tout le monde"),
            ("fact", "Donner un fait intéressant", "+fact", "Tout le monde"),
            ("quote", "Citer un utilisateur", "+quote [@utilisateur]", "Tout le monde"),
            ("clap", "Ajouter des applause entre les mots", "+clap <texte>", "Tout le monde"),
            ("uwu", "Transformer un texte en uwu", "+uwu <texte>", "Tout le monde"),
            ("ascii", "Créer de l'art ASCII", "+ascii <texte>", "Tout le monde"),
            ("emojify", "Transformer un texte en émojis", "+emojify <texte>", "Tout le monde"),
            ("say", "Faire parler le bot", "+say <message>", "Admin/Modo"),
            ("embed", "Créer un embed personnalisé", "+embed <titre> <description>", "Admin/Modo")
        ]
        
        for cmd, desc, usage, perm in commands:
            embed.add_field(
                name=f"😂 {cmd}",
                value=f"**Description:** {desc}\n**Usage:** `{usage}`\n**Permissions:** {perm}",
                inline=False
            )
        
        await ctx.send(embed=embed)

    async def show_extended_help(self, ctx):
        """Afficher l'aide des commandes étendues"""
        embed = nextcord.Embed(
            title="🚀 Commandes Étendues (17 commandes)",
            description="Commandes avancées et systèmes",
            color=0x9B59B6
        )
        
        commands = [
            ("todo", "Gestionnaire de tâches personnel", "+todo <action> [tâche]", "Tout le monde"),
            ("rank", "Voir le rang et XP d'un membre", "+rank [@membre]", "Tout le monde"),
            ("leaderboard", "Afficher le classement du serveur", "+leaderboard", "Tout le monde"),
            ("balance", "Voir le solde économique d'un membre", "+balance [@membre]", "Tout le monde"),
            ("daily", "Récompense quotidienne de coins", "+daily", "Tout le monde"),
            ("work", "Travailler pour gagner des coins", "+work", "Tout le monde"),
            ("play", "Jouer de la musique", "+play <recherche>", "Tout le monde"),
            ("skip", "Passer à la musique suivante", "+skip", "Tout le monde"),
            ("queue", "Voir la file d'attente musicale", "+queue", "Tout le monde"),
            ("volume", "Régler le volume de la musique", "+volume [0-100]", "Tout le monde"),
            ("weather", "Météo d'une ville", "+weather <ville>", "Tout le monde"),
            ("remindme", "Rappel personnel avancé", "+remindme <temps> <message>", "Tout le monde"),
            ("backup", "Créer une sauvegarde complète du serveur", "+backup", "Admin"),
            ("timer", "Minuteur de temps", "+timer <secondes>", "Tout le monde"),
            ("choose", "Choisir aléatoirement parmi des options", "+choose <option1> <option2> ...", "Tout le monde"),
            ("countdown", "Compte à rebours", "+countdown <secondes>", "Tout le monde"),
            ("roll", "Lancer un nombre aléatoire", "+roll [max]", "Tout le monde")
        ]
        
        for cmd, desc, usage, perm in commands:
            embed.add_field(
                name=f"🚀 {cmd}",
                value=f"**Description:** {desc}\n**Usage:** `{usage}`\n**Permissions:** {perm}",
                inline=False
            )
        
        await ctx.send(embed=embed)

    async def show_config_help(self, ctx):
        """Afficher l'aide de la configuration"""
        embed = nextcord.Embed(
            title="⚙️ Configuration Complète (10 commandes)",
            description="Personnalisation complète du bot",
            color=0x3498db
        )
        
        commands = [
            ("config", "Panneau de configuration interactif", "+config", "Admin"),
            ("setname", "Changer le nom du bot", "+setname <nom>", "Admin"),
            ("setprefix", "Changer le préfixe des commandes", "+setprefix <préfixe>", "Admin"),
            ("setbio", "Changer la bio du bot", "+setbio <bio>", "Admin"),
            ("setavatar", "Changer l'avatar du bot", "+setavatar [url]", "Admin"),
            ("setbanner", "Changer la bannière du bot", "+setbanner [url]", "Admin"),
            ("toggle", "Activer ou désactiver une fonctionnalité", "+toggle <feature>", "Admin"),
            ("setconfig", "Définir une configuration spécifique", "+setconfig <path> <value>", "Admin"),
            ("getconfig", "Afficher la configuration actuelle", "+getconfig [path]", "Admin")
        ]
        
        for cmd, desc, usage, perm in commands:
            embed.add_field(
                name=f"⚙️ {cmd}",
                value=f"**Description:** {desc}\n**Usage:** `{usage}`\n**Permissions:** {perm}",
                inline=False
            )
        
        await ctx.send(embed=embed)

    async def show_performance_help(self, ctx):
        """Afficher l'aide de la performance"""
        embed = nextcord.Embed(
            title="📊 Monitoring et Optimisation (4 commandes)",
            description="Monitoring et optimisation des performances",
            color=0x95A5A6
        )
        
        commands = [
            ("performance", "Afficher les statistiques de performance", "+performance", "Admin"),
            ("optimize", "Optimiser manuellement le bot", "+optimize", "Admin"),
            ("cache", "Informations sur le cache", "+cache", "Admin"),
            ("clearcache", "Vider le cache du bot", "+clearcache [type]", "Admin")
        ]
        
        for cmd, desc, usage, perm in commands:
            embed.add_field(
                name=f"📊 {cmd}",
                value=f"**Description:** {desc}\n**Usage:** `{usage}`\n**Permissions:** {perm}",
                inline=False
            )
        
        await ctx.send(embed=embed)

    async def search_command(self, ctx, command):
        """Rechercher une commande spécifique"""
        command = command.lower()
        
        # Base de données de toutes les commandes
        all_commands = {
            # Modération
            "warn": "Avertir un membre avec système de points",
            "kick": "Expulser un membre du serveur",
            "ban": "Bannir un membre définitivement",
            "tempban": "Bannir temporairement un membre",
            "mute": "Rendre muet un membre",
            "slowmode": "Activer le mode lent dans un salon",
            "lockdown": "Verrouiller tout le serveur",
            
            # Vocal
            "déplacer": "Déplacer un membre en vocal",
            "equilibrer": "Équilibrer les salons vocaux",
            "tempvoice": "Créer un salon vocal temporaire",
            
            # Jeux
            "dice": "Lancer un dé à 6 faces",
            "8ball": "Poser une question à la boule magique",
            "rps": "Jouer à pierre feuille ciseaux",
            
            # Utilitaires
            "afk": "Mettre son statut AFK",
            "snipe": "Voir le dernier message supprimé",
            "calc": "Calculatrice mathématique",
            "translate": "Traduire un texte",
            
            # Fun
            "meme": "Afficher un mème aléatoire",
            "joke": "Raconter une blague",
            "ascii": "Créer de l'art ASCII",
            
            # Étendu
            "todo": "Gestionnaire de tâches personnel",
            "rank": "Voir son rang et XP",
            "daily": "Récompense quotidienne",
            "work": "Travailler pour gagner des coins",
            "play": "Jouer de la musique",
            "weather": "Météo d'une ville",
            
            # Configuration
            "config": "Panneau de configuration interactif",
            "setname": "Changer le nom du bot",
            "setprefix": "Changer le préfixe des commandes",
            
            # Performance
            "performance": "Statistiques de performance",
            "optimize": "Optimiser le bot manuellement"
        }
        
        if command in all_commands:
            embed = nextcord.Embed(
                title=f"🔍 Aide: +{command}",
                description=all_commands[command],
                color=0x3498db
            )
            
            embed.add_field(
                name="📋 Usage",
                value=f"`+{command}`",
                inline=True
            )
            
            embed.add_field(
                name="🔐 Permissions",
                value="Varie selon la commande",
                inline=True
            )
            
            embed.add_field(
                name="📚 Catégorie",
                value=self.get_command_category(command),
                inline=True
            )
            
            await ctx.send(embed=embed)
        else:
            # Suggestions de commandes similaires
            suggestions = [cmd for cmd in all_commands.keys() if command in cmd or cmd in command]
            
            embed = nextcord.Embed(
                title="❌ Commande non trouvée",
                description=f"La commande `+{command}` n'existe pas.",
                color=0xE74C3C
            )
            
            if suggestions:
                embed.add_field(
                    name="💡 Suggestions",
                    value="Peut-être cherchais-tu:\n" + "\n".join([f"`+{s}`" for s in suggestions[:5]]),
                    inline=False
                )
            
            embed.add_field(
                name="📚 Utilise `+help`",
                value="Pour voir toutes les catégories disponibles",
                inline=False
            )
            
            await ctx.send(embed=embed)

    def get_command_category(self, command):
        """Obtenir la catégorie d'une commande"""
        categories = {
            "warn": "🛡️ Modération", "kick": "🛡️ Modération", "ban": "🛡️ Modération",
            "tempban": "🛡️ Modération", "mute": "🛡️ Modération", "slowmode": "🛡️ Modération",
            "lockdown": "🛡️ Modération",
            
            "déplacer": "🎤 Vocal", "equilibrer": "🎤 Vocal", "tempvoice": "🎤 Vocal",
            
            "dice": "🎮 Jeux", "8ball": "🎮 Jeux", "rps": "🎮 Jeux",
            
            "afk": "🛠️ Utilitaires", "snipe": "🛠️ Utilitaires", "calc": "🛠️ Utilitaires",
            "translate": "🛠️ Utilitaires",
            
            "meme": "😂 Fun", "joke": "😂 Fun", "ascii": "😂 Fun",
            
            "todo": "🚀 Étendu", "rank": "🚀 Étendu", "daily": "🚀 Étendu",
            "work": "🚀 Étendu", "play": "🚀 Étendu", "weather": "🚀 Étendu",
            
            "config": "⚙️ Configuration", "setname": "⚙️ Configuration",
            "setprefix": "⚙️ Configuration",
            
            "performance": "📊 Performance", "optimize": "📊 Performance"
        }
        
        return categories.get(command, "📚 Autre")

def setup(bot):
    bot.add_cog(System(bot))
