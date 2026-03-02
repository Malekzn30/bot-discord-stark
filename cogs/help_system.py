import nextcord
from nextcord.ext import commands
import asyncio

class HelpSelectView(nextcord.ui.View):
    def __init__(self, author, cog):
        super().__init__(timeout=180)
        self.author = author
        self.cog = cog
        self.current_category = None
    
    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("❌ Tu ne peux pas utiliser ce menu !", ephemeral=True)
            return False
        return True
    
    @nextcord.ui.select(
        placeholder="📚 Choisissez une catégorie",
        options=[
            nextcord.SelectOption(
                label="🛡️ Modération",
                description="Gestion du serveur et modération avancée",
                emoji="🛡️"
            ),
            nextcord.SelectOption(
                label="🎤 Vocal",
                description="Gestion complète des salons vocaux",
                emoji="🎤"
            ),
            nextcord.SelectOption(
                label="🎮 Jeux",
                description="Jeux et divertissement variés",
                emoji="🎮"
            ),
            nextcord.SelectOption(
                label="🎉 Communauté",
                description="Fonctionnalités communautaires",
                emoji="🎉"
            ),
            nextcord.SelectOption(
                label="🛠️ Utilitaires",
                description="Commandes utilitaires diverses",
                emoji="🛠️"
            ),
            nextcord.SelectOption(
                label="😂 Fun",
                description="Commandes d'amusement et divertissement",
                emoji="😂"
            ),
            nextcord.SelectOption(
                label="🚀 Étendu",
                description="Commandes avancées et systèmes",
                emoji="🚀"
            ),
            nextcord.SelectOption(
                label="⚙️ Configuration",
                description="Personnalisation complète du bot",
                emoji="⚙️"
            ),
            nextcord.SelectOption(
                label="📊 Performance",
                description="Monitoring et optimisation",
                emoji="📊"
            )
        ]
    )
    async def category_select(self, select: nextcord.ui.Select, interaction: nextcord.Interaction):
        category = select.values[0]
        self.current_category = category
        
        # Créer les vues spécifiques à chaque catégorie
        if "Configuration" in category:
            view = ConfigHelpView(self.author, self.cog)
            await self.cog.show_config_help(interaction, view)
        else:
            view = CategoryHelpView(self.author, self.cog, category)
            await self.cog.show_category_help(interaction, category, view)

class CategoryHelpView(nextcord.ui.View):
    def __init__(self, author, cog, category):
        super().__init__(timeout=180)
        self.author = author
        self.cog = cog
        self.category = category
    
    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("❌ Tu ne peux pas utiliser ce menu !", ephemeral=True)
            return False
        return True
    
    @nextcord.ui.button(label="◀️ Retour", style=nextcord.ButtonStyle.secondary)
    async def back_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        view = HelpSelectView(self.author, self.cog)
        await self.cog.show_main_help(interaction, view)
    
    @nextcord.ui.button(label="❌ Fermer", style=nextcord.ButtonStyle.danger)
    async def close_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.edit_message(view=None)

class ConfigHelpView(CategoryHelpView):
    def __init__(self, author, cog):
        super().__init__(author, cog, "Configuration")
    
    @nextcord.ui.button(label="🎨 Apparence", style=nextcord.ButtonStyle.primary, row=1)
    async def appearance_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.cog.show_appearance_detailed_help(interaction, self)
    
    @nextcord.ui.button(label="⚙️ Fonctionnalités", style=nextcord.ButtonStyle.primary, row=1)
    async def features_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.cog.show_features_detailed_help(interaction, self)
    
    @nextcord.ui.button(label="🔐 Permissions", style=nextcord.ButtonStyle.primary, row=1)
    async def permissions_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.cog.show_permissions_detailed_help(interaction, self)

class HelpSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="help")
    async def help_command(self, ctx, command: str = None):
        """Système d'aide avec menu sélecteur"""
        
        if command is not None:
            # Aide détaillée pour une commande spécifique
            await self.show_command_help(ctx, command)
            return
        
        # Menu principal avec sélecteur
        view = HelpSelectView(ctx.author, self)
        await self.show_main_help(ctx, view)
    
    async def show_main_help(self, ctx_or_interaction, view):
        """Afficher le menu principal d'aide"""
        embed = nextcord.Embed(
            title="🤖 Bot Stark - Système d'Aide",
            description="Bienvenue sur le système d'aide interactif !\n\nChoisissez une catégorie ci-dessous pour explorer les commandes.",
            color=0x3498db
        )
        
        embed.add_field(
            name="📚 Catégories disponibles",
            value=(
                "🛡️ **Modération** - Gestion du serveur\n"
                "📊 **Administration** - Logs et configuration\n"
                "🎤 **Vocal** - Salons vocaux et équilibrage\n"
                "📬 **Communication** - Messages et DM\n"
                "📱 **Social** - Lives et recherche\n"
                "🔒 **Sécurité** - Anti-liens et permissions\n"
                "🎮 **Jeux** - Divertissement et jeux\n"
                "⚙️ **Configuration** - Personnalisation du bot"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🔍 Comment utiliser",
            value=(
                "1. **Sélectionnez une catégorie** avec le menu déroulant\n"
                "2. **Explorez les commandes** dans la catégorie choisie\n"
                "3. **Utilisez `+help <commande>`** pour une aide détaillée\n\n"
                "💡 **Tip**: Utilisez `+config` pour personnaliser le bot !"
            ),
            inline=False
        )
        
        embed.set_footer(text="Bot Stark v1.0.0 | Fait avec ❤️ par 𝐒𝐭𝐚𝐫𝐊𝟗𝟐☆🇵🇸")
        
        if isinstance(ctx_or_interaction, nextcord.Interaction):
            await ctx_or_interaction.response.edit_message(embed=embed, view=view)
        else:
            await ctx_or_interaction.send(embed=embed, view=view)
    
    async def show_category_help(self, interaction, category, view):
        """Afficher l'aide d'une catégorie spécifique"""
        category_data = self.get_category_data(category)
        
        if not category_data:
            await interaction.response.send_message("❌ Catégorie non trouvée", ephemeral=True)
            return
        
        embed = nextcord.Embed(
            title=f"{category_data['emoji']} {category}",
            description=category_data['description'],
            color=category_data['color']
        )
        
        for cmd_name, cmd_info in category_data['commands'].items():
            field_value = (
                f"📝 **Description**: {cmd_info['description']}\n"
                f"⚙️ **Utilisation**: `{cmd_info['usage']}`\n"
                f"💡 **Exemple**: `{cmd_info['example']}`\n"
                f"🔒 **Permissions**: {cmd_info['permissions']}"
            )
            embed.add_field(name=f"🔧 {cmd_name}", value=field_value, inline=False)
        
        embed.set_footer(text=f"Catégorie: {category} | Utilise +help <commande> pour plus de détails")
        
        await interaction.response.edit_message(embed=embed, view=view)
    
    async def show_config_help(self, interaction, view):
        """Afficher l'aide de configuration"""
        embed = nextcord.Embed(
            title="⚙️ Configuration du Bot",
            description="Personnalisez entièrement votre bot Stark !",
            color=0x3498db
        )
        
        embed.add_field(
            name="🎨 Apparence",
            value=(
                "**Commandes**:\n"
                "`+setname <nom>` - Changer le nom du bot\n"
                "`+setprefix <prefixe>` - Changer le préfixe\n"
                "`+setbio <bio>` - Changer la bio\n"
                "`+setavatar <url>` - Changer l'avatar\n"
                "`+setbanner <url>` - Changer la bannière"
            ),
            inline=False
        )
        
        embed.add_field(
            name="⚙️ Fonctionnalités",
            value=(
                "**Commandes**:\n"
                "`+toggle <feature>` - Activer/désactiver\n"
                "`+setconfig <path> <value>` - Configuration avancée\n"
                "`+config` - Panneau de configuration interactif"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🔐 Permissions",
            value=(
                "**Commandes**:\n"
                "`+addadmin <@rôle>` - Ajouter admin\n"
                "`+addmod <@rôle>` - Ajouter modérateur\n"
                "`+trust <@utilisateur>` - Utilisateur de confiance\n"
                "`+blacklist <@utilisateur>` - Liste noire"
            ),
            inline=False
        )
        
        embed.add_field(
            name="💬 Messages",
            value=(
                "**Commandes**:\n"
                "`+setwelcome <message>` - Message d'accueil\n"
                "`+setgoodbye <message>` - Message d'au revoir\n"
                "`+setlevelup <message>` - Message de niveau\n"
                "**Variables**: {user}, {server}, {level}"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🎤 Vocal",
            value=(
                "**Commandes**:\n"
                "`+setvocalmax <nombre>` - Max par salon\n"
                "`+toggleautobalance` - Équilibrage auto\n"
                "`+toggletempchannels` - Salons temporaires"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🎮 Jeux",
            value=(
                "**Commandes**:\n"
                "`+togglegames` - Activer/désactiver les jeux\n"
                "`+toggledailyrewards` - Récompenses quotidiennes\n"
                "`+toggleleaderboards` - Classements"
            ),
            inline=False
        )
        
        embed.set_footer(text="Configuration | Utilise +config pour le panneau interactif")
        
        await interaction.response.edit_message(embed=embed, view=view)
    
    async def show_appearance_detailed_help(self, interaction, view):
        """Afficher l'aide détaillée de l'apparence"""
        embed = nextcord.Embed(
            title="🎨 Configuration de l'Apparence",
            description="Personnalisez l'apparence du bot en détail",
            color=0x3498db
        )
        
        commands = {
            "setname": {
                "usage": "+setname <nom>",
                "description": "Changer le nom du bot",
                "example": "+setname Mon Bot Personnalisé"
            },
            "setprefix": {
                "usage": "+setprefix <prefixe>",
                "description": "Changer le préfixe des commandes",
                "example": "+setprefix !"
            },
            "setbio": {
                "usage": "+setbio <bio>",
                "description": "Changer la bio du bot",
                "example": "+setbio Bot de modération avancé"
            },
            "setavatar": {
                "usage": "+setavatar <url_image>",
                "description": "Changer l'avatar du bot",
                "example": "+setavatar https://example.com/avatar.png"
            },
            "setbanner": {
                "usage": "+setbanner <url_image>",
                "description": "Changer la bannière du bot",
                "example": "+setbanner https://example.com/banner.png"
            },
            "setstatus": {
                "usage": "+setstatus <online|idle|dnd|invisible>",
                "description": "Changer le statut du bot",
                "example": "+setstatus dnd"
            },
            "setactivity": {
                "usage": "+setactivity <playing|watching|listening|competing> <texte>",
                "description": "Changer l'activité du bot",
                "example": "+setactivity watching vos serveurs"
            }
        }
        
        for cmd_name, cmd_info in commands.items():
            field_value = (
                f"📝 **Description**: {cmd_info['description']}\n"
                f"⚙️ **Utilisation**: `{cmd_info['usage']}`\n"
                f"💡 **Exemple**: `{cmd_info['example']}`"
            )
            embed.add_field(name=f"🔧 +{cmd_name}", value=field_value, inline=False)
        
        await interaction.response.edit_message(embed=embed, view=view)
    
    async def show_features_detailed_help(self, interaction, view):
        """Afficher l'aide détaillée des fonctionnalités"""
        embed = nextcord.Embed(
            title="⚙️ Configuration des Fonctionnalités",
            description="Activez ou désactivez les fonctionnalités du bot",
            color=0x3498db
        )
        
        features = {
            "moderation": "Modération et gestion du serveur",
            "automod": "Modération automatique",
            "vocal": "Gestion des salons vocaux",
            "autobalance": "Équilibrage automatique des salons vocaux",
            "social": "Fonctionnalités sociales (lives, etc.)",
            "livenotifications": "Notifications de live TikTok",
            "games": "Jeux et divertissement",
            "dailyrewards": "Récompenses quotidiennes",
            "leaderboards": "Classements et statistiques"
        }
        
        embed.add_field(
            name="🎛️ Fonctionnalités disponibles",
            value="\n".join([f"• **{name}**: {desc}" for name, desc in features.items()]),
            inline=False
        )
        
        embed.add_field(
            name="🔧 Comment utiliser",
            value=(
                "**Activer/Désactiver**:\n"
                "`+toggle <feature>` - Active ou désactive une fonctionnalité\n\n"
                "**Configuration avancée**:\n"
                "`+setconfig <path> <value>` - Définit une valeur spécifique\n\n"
                "**Exemples**:\n"
                "`+toggle moderation` - Active la modération\n"
                "`+setconfig features.vocal.max_members_per_channel 10` - Limite à 10 par salon"
            ),
            inline=False
        )
        
        await interaction.response.edit_message(embed=embed, view=view)
    
    async def show_permissions_detailed_help(self, interaction, view):
        """Afficher l'aide détaillée des permissions"""
        embed = nextcord.Embed(
            title="🔐 Configuration des Permissions",
            description="Gérez les rôles et permissions du bot",
            color=0x3498db
        )
        
        commands = {
            "addadmin": {
                "usage": "+addadmin <@rôle>",
                "description": "Ajouter un rôle administrateur",
                "example": "+addadmin @Admin"
            },
            "removeadmin": {
                "usage": "+removeadmin <@rôle>",
                "description": "Retirer un rôle administrateur",
                "example": "+removeadmin @Admin"
            },
            "addmod": {
                "usage": "+addmod <@rôle>",
                "description": "Ajouter un rôle modérateur",
                "example": "+addmod @Modérateur"
            },
            "removemod": {
                "usage": "+removemod <@rôle>",
                "description": "Retirer un rôle modérateur",
                "example": "+removemod @Modérateur"
            },
            "trust": {
                "usage": "+trust <@utilisateur>",
                "description": "Ajouter un utilisateur de confiance",
                "example": "+trust @User"
            },
            "untrust": {
                "usage": "+untrust <@utilisateur>",
                "description": "Retirer un utilisateur de confiance",
                "example": "+untrust @User"
            },
            "blacklist": {
                "usage": "+blacklist <@utilisateur>",
                "description": "Ajouter un utilisateur à la liste noire",
                "example": "+blacklist @User"
            },
            "unblacklist": {
                "usage": "+unblacklist <@utilisateur>",
                "description": "Retirer un utilisateur de la liste noire",
                "example": "+unblacklist @User"
            }
        }
        
        for cmd_name, cmd_info in commands.items():
            field_value = (
                f"📝 **Description**: {cmd_info['description']}\n"
                f"⚙️ **Utilisation**: `{cmd_info['usage']}`\n"
                f"💡 **Exemple**: `{cmd_info['example']}`"
            )
            embed.add_field(name=f"🔧 +{cmd_name}", value=field_value, inline=False)
        
        await interaction.response.edit_message(embed=embed, view=view)
    
    async def show_command_help(self, ctx, command):
        """Afficher l'aide détaillée pour une commande spécifique"""
        # Implémentation similaire à celle existante mais améliorée
        await ctx.send(f"Aide détaillée pour la commande `{command}` - En cours de développement...")
    
    def get_category_data(self, category):
        """Récupérer les données d'une catégorie"""
        categories = {
            "🛡️ Modération": {
                "emoji": "🛡️",
                "description": "Commandes pour gérer et modérer le serveur",
                "color": 0xE74C3C,
                "commands": {
                    "warn": {
                        "description": "Avertir un membre avec système de points",
                        "usage": "+warn @membre <raison>",
                        "example": "+warn @User Spam",
                        "permissions": "Admin/Modo"
                    },
                    "warns": {
                        "description": "Voir les warns d'un membre",
                        "usage": "+warns [@membre]",
                        "example": "+warns @User",
                        "permissions": "Admin/Modo"
                    },
                    "clearwarns": {
                        "description": "Supprimer tous les warns d'un membre",
                        "usage": "+clearwarns @membre",
                        "example": "+clearwarns @User",
                        "permissions": "Admin"
                    },
                    "mute": {
                        "description": "Rendre muet un membre",
                        "usage": "+mute @membre [durée] <raison>",
                        "example": "+mute @User 1h Spam",
                        "permissions": "Admin/Modo"
                    },
                    "unmute": {
                        "description": "Rendre la parole à un membre",
                        "usage": "+unmute @membre",
                        "example": "+unmute @User",
                        "permissions": "Admin/Modo"
                    },
                    "tempban": {
                        "description": "Bannir temporairement un membre",
                        "usage": "+tempban @membre <durée> <raison>",
                        "example": "+tempban @User 1d Spam",
                        "permissions": "Admin"
                    },
                    "kick": {
                        "description": "Expulser un membre",
                        "usage": "+kick @membre <raison>",
                        "example": "+kick @User Non respect des règles",
                        "permissions": "Admin/Modo"
                    },
                    "ban": {
                        "description": "Bannir un membre",
                        "usage": "+ban @membre <raison>",
                        "example": "+ban @User Infraction grave",
                        "permissions": "Admin"
                    },
                    "slowmode": {
                        "description": "Activer le mode lent",
                        "usage": "+slowmode [secondes]",
                        "example": "+slowmode 5",
                        "permissions": "Admin/Modo"
                    },
                    "lockdown": {
                        "description": "Verrouiller le serveur",
                        "usage": "+lockdown",
                        "example": "+lockdown",
                        "permissions": "Admin"
                    },
                    "unlockdown": {
                        "description": "Déverrouiller le serveur",
                        "usage": "+unlockdown",
                        "example": "+unlockdown",
                        "permissions": "Admin"
                    }
                }
            },
            "🎤 Vocal": {
                "emoji": "🎤",
                "description": "Gestion des salons vocaux et équilibrage",
                "color": 0x1ABC9C,
                "commands": {
                    "déplacer": {
                        "description": "Déplacer un membre en vocal",
                        "usage": "+déplacer @membre #salon",
                        "example": "+déplacer @User #Général",
                        "permissions": "Admin/Modo"
                    },
                    "equilibrer": {
                        "description": "Équilibrer les salons vocaux",
                        "usage": "+equilibrer @catégorie <nombre>",
                        "example": "+equilibrer #Gaming 3",
                        "permissions": "Admin/Modo"
                    },
                    "immobiles": {
                        "description": "Lister les membres immobiles",
                        "usage": "+immobiles",
                        "example": "+immobiles",
                        "permissions": "Admin/Modo"
                    },
                    "force_move": {
                        "description": "Forcer le déplacement",
                        "usage": "+force_move @membre #salon",
                        "example": "+force_move @User #Général",
                        "permissions": "Admin/Modo"
                    },
                    "gather_all": {
                        "description": "Rassembler tout le monde",
                        "usage": "+gather_all #salon",
                        "example": "+gather_all #Réunion",
                        "permissions": "Admin/Modo"
                    },
                    "create_voice_rooms": {
                        "description": "Créer des salons vocaux",
                        "usage": "+create_voice_rooms @catégorie <nombre> <nom>",
                        "example": "+create_voice_rooms #Gaming 5 Team",
                        "permissions": "Admin"
                    },
                    "clone_voice_channel": {
                        "description": "Cloner un salon vocal",
                        "usage": "+clone_voice_channel #salon <nom>",
                        "example": "+clone_voice_channel #Gaming Clone",
                        "permissions": "Admin"
                    },
                    "swap_channels": {
                        "description": "Échanger les membres entre salons",
                        "usage": "+swap_channels #salon1 #salon2",
                        "example": "+swap_channels #Team1 #Team2",
                        "permissions": "Admin"
                    },
                    "tempvoice": {
                        "description": "Créer un salon vocal temporaire",
                        "usage": "+tempvoice [nom]",
                        "example": "+tempvoice Salon Privé",
                        "permissions": "Tout le monde"
                    }
                }
            },
            "🎮 Jeux": {
                "emoji": "🎮",
                "description": "Jeux et divertissement",
                "color": 0xF39C12,
                "commands": {
                    "dice": {
                        "description": "Lancer un dé",
                        "usage": "+dice [faces]",
                        "example": "+dice 6",
                        "permissions": "Tout le monde"
                    },
                    "coin": {
                        "description": "Pile ou face",
                        "usage": "+coin",
                        "example": "+coin",
                        "permissions": "Tout le monde"
                    },
                    "rps": {
                        "description": "Pierre feuille ciseaux",
                        "usage": "+rps <pierre|feuille|ciseaux>",
                        "example": "+rps pierre",
                        "permissions": "Tout le monde"
                    },
                    "devinelenombre": {
                        "description": "Jeu de devinette de nombre",
                        "usage": "+devinelenombre",
                        "example": "+devinelenombre",
                        "permissions": "Tout le monde"
                    },
                    "8ball": {
                        "description": "Boule magique 8",
                        "usage": "+8ball <question>",
                        "example": "+8ball Vais-je réussir ?",
                        "permissions": "Tout le monde"
                    },
                    "truth": {
                        "description": "Question pour vérité",
                        "usage": "+truth [catégorie]",
                        "example": "+truth spicy",
                        "permissions": "Tout le monde"
                    },
                    "dare": {
                        "description": "Action pour un défi",
                        "usage": "+dare [intensité]",
                        "example": "+dare hard",
                        "permissions": "Tout le monde"
                    },
                    "wyr": {
                        "description": "Préfères-tu (Would You Rather)",
                        "usage": "+wyr",
                        "example": "+wyr",
                        "permissions": "Tout le monde"
                    },
                    "rate": {
                        "description": "Noter quelque chose",
                        "usage": "+rate [chose]",
                        "example": "+rate @User",
                        "permissions": "Tout le monde"
                    },
                    "ship": {
                        "description": "Calculer le 'ship' entre deux utilisateurs",
                        "usage": "+ship [@user1] [@user2]",
                        "example": "+ship @User1 @User2",
                        "permissions": "Tout le monde"
                    }
                }
            },
            "🎉 Communauté": {
                "emoji": "🎉",
                "description": "Fonctionnalités communautaires",
                "color": 0x9B59B6,
                "commands": {
                    "suggest": {
                        "description": "Faire une suggestion pour le serveur",
                        "usage": "+suggest <suggestion>",
                        "example": "+suggest Ajouter un salon de mèmes",
                        "permissions": "Tout le monde"
                    },
                    "poll": {
                        "description": "Créer un sondage",
                        "usage": "+poll <question> <option1> <option2> ...",
                        "example": "+poll 'Quel est le meilleur ?' 'Option 1' 'Option 2'",
                        "permissions": "Admin/Modo"
                    },
                    "giveaway": {
                        "description": "Lancer un giveaway",
                        "usage": "+giveaway <durée> <prix>",
                        "example": "+giveaway 1h Nitro Classic",
                        "permissions": "Admin/Modo"
                    },
                    "reactionrole": {
                        "description": "Ajouter un rôle par réaction",
                        "usage": "+reactionrole <message_id> <emoji> @rôle",
                        "example": "+reactionrole 123456789 🎮 @Gamer",
                        "permissions": "Admin"
                    },
                    "serverstats": {
                        "description": "Statistiques du serveur",
                        "usage": "+serverstats",
                        "example": "+serverstats",
                        "permissions": "Tout le monde"
                    },
                    "userinfo": {
                        "description": "Informations sur un utilisateur",
                        "usage": "+userinfo [@membre]",
                        "example": "+userinfo @User",
                        "permissions": "Tout le monde"
                    },
                    "serverinfo": {
                        "description": "Informations détaillées sur le serveur",
                        "usage": "+serverinfo",
                        "example": "+serverinfo",
                        "permissions": "Tout le monde"
                    },
                    "roleinfo": {
                        "description": "Informations détaillées sur un rôle",
                        "usage": "+roleinfo @rôle",
                        "example": "+roleinfo @Admin",
                        "permissions": "Tout le monde"
                    },
                    "channelinfo": {
                        "description": "Informations sur un salon",
                        "usage": "+channelinfo [#salon]",
                        "example": "+channelinfo #général",
                        "permissions": "Tout le monde"
                    },
                    "starboard": {
                        "description": "Afficher la starboard du serveur",
                        "usage": "+starboard",
                        "example": "+starboard",
                        "permissions": "Tout le monde"
                    }
                }
            },
            "🛠️ Utilitaires": {
                "emoji": "🛠️",
                "description": "Commandes utilitaires diverses",
                "color": 0x3498db,
                "commands": {
                    "afk": {
                        "description": "Mettre son statut AFK",
                        "usage": "+afk [raison]",
                        "example": "+afk Pause déjeuner",
                        "permissions": "Tout le monde"
                    },
                    "snipe": {
                        "description": "Voir le dernier message supprimé",
                        "usage": "+snipe",
                        "example": "+snipe",
                        "permissions": "Tout le monde"
                    },
                    "editsnipe": {
                        "description": "Voir le dernier message modifié",
                        "usage": "+editsnipe",
                        "example": "+editsnipe",
                        "permissions": "Tout le monde"
                    },
                    "emoji": {
                        "description": "Informations sur un émoji",
                        "usage": "+emoji <émoji>",
                        "example": "+emoji 😊",
                        "permissions": "Tout le monde"
                    },
                    "steal": {
                        "description": "Ajouter un émoji d'un autre serveur",
                        "usage": "+steal <émoji> [nom]",
                        "example": "+steal 😊 CoolEmoji",
                        "permissions": "Admin"
                    },
                    "firstmessage": {
                        "description": "Voir le premier message d'un salon",
                        "usage": "+firstmessage [#salon]",
                        "example": "+firstmessage #général",
                        "permissions": "Tout le monde"
                    },
                    "createinvite": {
                        "description": "Créer une invitation",
                        "usage": "+createinvite [#salon] [max_uses] [expires_in]",
                        "example": "+createinvite #général 5 24",
                        "permissions": "Admin/Modo"
                    },
                    "calc": {
                        "description": "Calculatrice simple",
                        "usage": "+calc <expression>",
                        "example": "+calc 2+2*3",
                        "permissions": "Tout le monde"
                    },
                    "remind": {
                        "description": "Rappel (format: 1h, 30m, 1d)",
                        "usage": "+remind <temps> <message>",
                        "example": "+remind 1h Réunion importante",
                        "permissions": "Tout le monde"
                    },
                    "translate": {
                        "description": "Traduire un texte",
                        "usage": "+translate <langue> <texte>",
                        "example": "+translate fr Hello world",
                        "permissions": "Tout le monde"
                    }
                }
            },
            "😂 Fun": {
                "emoji": "😂",
                "description": "Commandes d'amusement et divertissement",
                "color": 0xFF69B4,
                "commands": {
                    "meme": {
                        "description": "Afficher un mème aléatoire",
                        "usage": "+meme [catégorie]",
                        "example": "+meme gaming",
                        "permissions": "Tout le monde"
                    },
                    "joke": {
                        "description": "Raconter une blague",
                        "usage": "+joke",
                        "example": "+joke",
                        "permissions": "Tout le monde"
                    },
                    "fact": {
                        "description": "Donner un fait intéressant",
                        "usage": "+fact",
                        "example": "+fact",
                        "permissions": "Tout le monde"
                    },
                    "quote": {
                        "description": "Citer un utilisateur",
                        "usage": "+quote [@utilisateur]",
                        "example": "+quote @User",
                        "permissions": "Tout le monde"
                    },
                    "reverse": {
                        "description": "Inverser un texte",
                        "usage": "+reverse <texte>",
                        "example": "+reverse Bonjour",
                        "permissions": "Tout le monde"
                    },
                    "clap": {
                        "description": "Ajouter des applause entre les mots",
                        "usage": "+clap <texte>",
                        "example": "+clap C'est super",
                        "permissions": "Tout le monde"
                    },
                    "uwu": {
                        "description": "Transformer un texte en uwu",
                        "usage": "+uwu <texte>",
                        "example": "+uwu Hello world",
                        "permissions": "Tout le monde"
                    },
                    "ascii": {
                        "description": "Créer de l'art ASCII",
                        "usage": "+ascii <texte>",
                        "example": "+ascii HELLO",
                        "permissions": "Tout le monde"
                    },
                    "emojify": {
                        "description": "Transformer un texte en émojis",
                        "usage": "+emojify <texte>",
                        "example": "+emojify HELLO",
                        "permissions": "Tout le monde"
                    }
                }
            },
            "⚙️ Configuration": {
                "emoji": "⚙️",
                "description": "Personnalisation du bot",
                "color": 0x3498db,
                "commands": {
                    "config": {
                        "description": "Panneau de configuration interactif",
                        "usage": "+config",
                        "example": "+config",
                        "permissions": "Admin"
                    },
                    "setname": {
                        "description": "Changer le nom du bot",
                        "usage": "+setname <nom>",
                        "example": "+setname Mon Bot",
                        "permissions": "Admin"
                    },
                    "setprefix": {
                        "description": "Changer le préfixe des commandes",
                        "usage": "+setprefix <préfixe>",
                        "example": "+setprefix !",
                        "permissions": "Admin"
                    },
                    "setbio": {
                        "description": "Changer la bio du bot",
                        "usage": "+setbio <bio>",
                        "example": "+setbot Bot de modération",
                        "permissions": "Admin"
                    },
                    "setavatar": {
                        "description": "Changer l'avatar du bot",
                        "usage": "+setavatar [url]",
                        "example": "+setavatar https://example.com/img.png",
                        "permissions": "Admin"
                    },
                    "setbanner": {
                        "description": "Changer la bannière du bot",
                        "usage": "+setbanner [url]",
                        "example": "+setbanner https://example.com/banner.png",
                        "permissions": "Admin"
                    },
                    "toggle": {
                        "description": "Activer ou désactiver une fonctionnalité",
                        "usage": "+toggle <feature>",
                        "example": "+toggle moderation",
                        "permissions": "Admin"
                    },
                    "setconfig": {
                        "description": "Définir une configuration spécifique",
                        "usage": "+setconfig <path> <value>",
                        "example": "+setconfig features.vocal.max_members 10",
                        "permissions": "Admin"
                    },
                    "getconfig": {
                        "description": "Afficher la configuration actuelle",
                        "usage": "+getconfig [path]",
                        "example": "+getconfig bot.name",
                        "permissions": "Admin"
                    }
                }
            },
            "📊 Performance": {
                "emoji": "📊",
                "description": "Monitoring et optimisation des performances",
                "color": 0x95A5A6,
                "commands": {
                    "performance": {
                        "description": "Afficher les statistiques de performance",
                        "usage": "+performance",
                        "example": "+performance",
                        "permissions": "Admin"
                    },
                    "optimize": {
                        "description": "Optimiser manuellement le bot",
                        "usage": "+optimize",
                        "example": "+optimize",
                        "permissions": "Admin"
                    },
                    "cache": {
                        "description": "Informations sur le cache",
                        "usage": "+cache",
                        "example": "+cache",
                        "permissions": "Admin"
                    },
                    "clearcache": {
                        "description": "Vider le cache du bot",
                        "usage": "+clearcache [type]",
                        "example": "+clearcache all",
                        "permissions": "Admin"
                    }
                }
            },
            "🚀 Étendu": {
                "emoji": "🚀",
                "description": "Commandes avancées et systèmes",
                "color": 0x9B59B6,
                "commands": {
                    "todo": {
                        "description": "Gestionnaire de tâches personnel",
                        "usage": "+todo <action> [tâche]",
                        "example": "+todo add Faire les courses",
                        "permissions": "Tout le monde"
                    },
                    "rank": {
                        "description": "Voir le rang et XP d'un membre",
                        "usage": "+rank [@membre]",
                        "example": "+rank @User",
                        "permissions": "Tout le monde"
                    },
                    "leaderboard": {
                        "description": "Afficher le classement du serveur",
                        "usage": "+leaderboard",
                        "example": "+leaderboard",
                        "permissions": "Tout le monde"
                    },
                    "balance": {
                        "description": "Voir le solde économique d'un membre",
                        "usage": "+balance [@membre]",
                        "example": "+balance @User",
                        "permissions": "Tout le monde"
                    },
                    "daily": {
                        "description": "Récompense quotidienne de coins",
                        "usage": "+daily",
                        "example": "+daily",
                        "permissions": "Tout le monde"
                    },
                    "work": {
                        "description": "Travailler pour gagner des coins",
                        "usage": "+work",
                        "example": "+work",
                        "permissions": "Tout le monde"
                    },
                    "play": {
                        "description": "Jouer de la musique",
                        "usage": "+play <recherche>",
                        "example": "+play Never Gonna Give You Up",
                        "permissions": "Tout le monde"
                    },
                    "skip": {
                        "description": "Passer à la musique suivante",
                        "usage": "+skip",
                        "example": "+skip",
                        "permissions": "Tout le monde"
                    },
                    "queue": {
                        "description": "Voir la file d'attente musicale",
                        "usage": "+queue",
                        "example": "+queue",
                        "permissions": "Tout le monde"
                    },
                    "volume": {
                        "description": "Régler le volume de la musique",
                        "usage": "+volume [0-100]",
                        "example": "+volume 50",
                        "permissions": "Tout le monde"
                    },
                    "weather": {
                        "description": "Météo d'une ville",
                        "usage": "+weather <ville>",
                        "example": "+weather Paris",
                        "permissions": "Tout le monde"
                    },
                    "remindme": {
                        "description": "Rappel personnel avancé",
                        "usage": "+remindme <temps> <message>",
                        "example": "+remindme 1h Réunion importante",
                        "permissions": "Tout le monde"
                    },
                    "backup": {
                        "description": "Créer une sauvegarde complète du serveur",
                        "usage": "+backup",
                        "example": "+backup",
                        "permissions": "Admin"
                    },
                    "timer": {
                        "description": "Minuteur de temps",
                        "usage": "+timer <secondes>",
                        "example": "+timer 60",
                        "permissions": "Tout le monde"
                    },
                    "choose": {
                        "description": "Choisir aléatoirement parmi des options",
                        "usage": "+choose <option1> <option2> ...",
                        "example": "+choose Pizza Sushi Burger",
                        "permissions": "Tout le monde"
                    },
                    "countdown": {
                        "description": "Compte à rebours",
                        "usage": "+countdown <secondes>",
                        "example": "+countdown 10",
                        "permissions": "Tout le monde"
                    },
                    "roll": {
                        "description": "Lancer un nombre aléatoire",
                        "usage": "+roll [max]",
                        "example": "+roll 100",
                        "permissions": "Tout le monde"
                    }
                }
            }
        }
        
        return categories.get(category)

def setup(bot):
    bot.add_cog(HelpSystem(bot))
