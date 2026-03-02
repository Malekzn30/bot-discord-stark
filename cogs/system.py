import nextcord
from nextcord.ext import commands
import asyncio
import datetime
from config import AUTHORIZED_ROLE_ID

class HelpView(nextcord.ui.View):
    def __init__(self, pages, author):
        super().__init__(timeout=180)
        self.pages = pages
        self.current_page = 0
        self.author = author
    
    async def update_message(self, interaction: nextcord.Interaction):
        embed = self.pages[self.current_page]
        await interaction.response.edit_message(embed=embed, view=self)
    
    @nextcord.ui.button(label="◀️", style=nextcord.ButtonStyle.secondary)
    async def previous_page(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("❌ Tu ne peux pas utiliser ce menu !", ephemeral=True)
            return
        
        self.current_page = (self.current_page - 1) % len(self.pages)
        await self.update_message(interaction)
    
    @nextcord.ui.button(label="▶️", style=nextcord.ButtonStyle.secondary)
    async def next_page(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("❌ Tu ne peux pas utiliser ce menu !", ephemeral=True)
            return
        
        self.current_page = (self.current_page + 1) % len(self.pages)
        await self.update_message(interaction)
    
    @nextcord.ui.button(label="🏠", style=nextcord.ButtonStyle.primary)
    async def home_page(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("❌ Tu ne peux pas utiliser ce menu !", ephemeral=True)
            return
        
        self.current_page = 0
        await self.update_message(interaction)
    
    @nextcord.ui.button(label="❌", style=nextcord.ButtonStyle.danger)
    async def stop_help(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("❌ Tu ne peux pas utiliser ce menu !", ephemeral=True)
            return
        
        await interaction.response.edit_message(view=None)

def has_role():
    async def predicate(ctx):
        role = ctx.guild.get_role(AUTHORIZED_ROLE_ID)
        return role in ctx.author.roles
    return commands.check(predicate)

class System(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx, command: str = None):
        """Système d'aide complet avec catégories et pages"""
        
        if command is None:
            # Créer les pages du help
            pages = []
            
            # Page 1: Accueil
            home_embed = nextcord.Embed(
                title="🤖 Bot Stark - Menu d'Aide",
                description="Bienvenue sur le menu d'aide du Bot Stark !\n\nUtilise les boutons pour naviguer entre les catégories.",
                color=0x3498db
            )
            
            home_embed.add_field(
                name="📚 Catégories disponibles",
                value=(
                    "🛡️ **Modération** - Gestion du serveur\n"
                    "📊 **Administration** - Logs et configuration\n"
                    "🎤 **Vocal** - Gestion des salons vocaux\n"
                    "📬 **Communication** - Messages et DM\n"
                    "📱 **Social** - Lives et recherche\n"
                    "🔒 **Sécurité** - Anti-liens et permissions\n"
                    "🎮 **Jeux** - Divertissement\n"
                    "ℹ️ **Informations** - Commandes utiles"
                ),
                inline=False
            )
            
            home_embed.add_field(
                name="🔍 Comment utiliser",
                value=(
                    "`+help` - Afficher ce menu\n"
                    "`+help <commande>` - Aide détaillée sur une commande\n"
                    "`+help <catégorie>` - Voir une catégorie spécifique"
                ),
                inline=False
            )
            
            home_embed.set_footer(text=f"Total: 21 commandes dans 8 catégories | Utilise les boutons pour naviguer")
            home_embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
            pages.append(home_embed)
            
            # Page 2: Modération
            mod_embed = nextcord.Embed(
                title="🛡️ Modération",
                description="Commandes pour gérer et modérer le serveur",
                color=0xE74C3C
            )
            
            mod_commands = {
                "warn": {
                    "description": "Avertir un membre",
                    "utilisation": "`+warn @membre <raison>`",
                    "exemple": "`+warn @User Spam dans le chat`",
                    "permissions": "Rôle autorisé"
                },
                "kick": {
                    "description": "Expulser un membre",
                    "utilisation": "`+kick @membre <raison>`",
                    "exemple": "`+kick @User Non respect des règles`",
                    "permissions": "Rôle autorisé"
                },
                "ban": {
                    "description": "Bannir un membre",
                    "utilisation": "`+ban @membre <raison>`",
                    "exemple": "`+ban @User Infraction grave`",
                    "permissions": "Rôle autorisé"
                },
                "tempban": {
                    "description": "Bannir temporairement",
                    "utilisation": "`+tempban @membre <temps> <raison>`",
                    "exemple": "`+tempban @User 7j Spam`",
                    "permissions": "Rôle autorisé"
                },
                "mute": {
                    "description": "Rendre muet",
                    "utilisation": "`+mute @membre <temps> <raison>`",
                    "exemple": "`+mute @User 10h Haine`",
                    "permissions": "Rôle autorisé"
                },
                "timeout": {
                    "description": "Mettre en timeout",
                    "utilisation": "`+timeout @membre <temps> <raison>`",
                    "exemple": "`+timeout @User 5m Calmez-vous`",
                    "permissions": "Rôle autorisé"
                },
                "clear": {
                    "description": "Supprimer des messages",
                    "utilisation": "`+clear <nombre>`",
                    "exemple": "`+clear 10`",
                    "permissions": "Rôle autorisé"
                },
                "lock": {
                    "description": "Verrouiller un salon",
                    "utilisation": "`+lock`",
                    "exemple": "`+lock`",
                    "permissions": "Rôle autorisé"
                },
                "unlock": {
                    "description": "Déverrouiller un salon",
                    "utilisation": "`+unlock`",
                    "exemple": "`+unlock`",
                    "permissions": "Rôle autorisé"
                }
            }
            
            for cmd_name, cmd_info in mod_commands.items():
                field_value = (
                    f"📝 **Description**: {cmd_info['description']}\n"
                    f"⚙️ **Utilisation**: {cmd_info['utilisation']}\n"
                    f"💡 **Exemple**: {cmd_info['exemple']}\n"
                    f"🔒 **Permissions**: {cmd_info['permissions']}"
                )
                mod_embed.add_field(name=f"🔧 +{cmd_name}", value=field_value, inline=False)
            
            mod_embed.set_footer(text="Page 2/9 - Modération")
            pages.append(mod_embed)
            
            # Page 3: Administration
            admin_embed = nextcord.Embed(
                title="📊 Administration",
                description="Commandes d'administration et de configuration",
                color=0x9B59B6
            )
            
            admin_commands = {
                "logs_setup": {
                    "description": "Configurer les logs du serveur",
                    "utilisation": "`+logs_setup`",
                    "exemple": "`+logs_setup` (menu interactif)",
                    "permissions": "Rôle autorisé"
                },
                "logs_status": {
                    "description": "Voir l'état des logs",
                    "utilisation": "`+logs_status`",
                    "exemple": "`+logs_status`",
                    "permissions": "Rôle autorisé"
                },
                "embed": {
                    "description": "Créer un embed personnalisé",
                    "utilisation": "`+embed <titre> | description`",
                    "exemple": "`+embed Règles | Respectez les règles du serveur`",
                    "permissions": "Rôle autorisé"
                },
                "ping": {
                    "description": "Vérifier la latence du bot",
                    "utilisation": "`+ping`",
                    "exemple": "`+ping`",
                    "permissions": "Tout le monde"
                }
            }
            
            for cmd_name, cmd_info in admin_commands.items():
                field_value = (
                    f"📝 **Description**: {cmd_info['description']}\n"
                    f"⚙️ **Utilisation**: {cmd_info['utilisation']}\n"
                    f"💡 **Exemple**: {cmd_info['exemple']}\n"
                    f"🔒 **Permissions**: {cmd_info['permissions']}"
                )
                admin_embed.add_field(name=f"🔧 +{cmd_name}", value=field_value, inline=False)
            
            admin_embed.set_footer(text="Page 3/9 - Administration")
            pages.append(admin_embed)
            
            # Page 4: Vocal (partie 1)
            voice1_embed = nextcord.Embed(
                title="🎤 Vocal - Gestion",
                description="Commandes pour la gestion des salons vocaux",
                color=0x1ABC9C
            )
            
            voice1_commands = {
                "déplacer": {
                    "description": "Déplacer un membre en vocal",
                    "utilisation": "`+déplacer @membre #salon`",
                    "exemple": "`+déplacer @User #Général`",
                    "permissions": "Rôle autorisé"
                },
                "equilibrer": {
                    "description": "Équilibrer les membres dans les salons",
                    "utilisation": "`+equilibrer @catégorie <nombre>`",
                    "exemple": "`+equilibrer #Gaming 3`",
                    "permissions": "Rôle autorisé"
                },
                "equilibrer_auto": {
                    "description": "Équilibrage automatique intelligent",
                    "utilisation": "`+equilibrer_auto @catégorie`",
                    "exemple": "`+equilibrer_auto #Gaming`",
                    "permissions": "Rôle autorisé"
                },
                "stats_vocal": {
                    "description": "Statistiques des salons vocaux",
                    "utilisation": "`+stats_vocal @catégorie`",
                    "exemple": "`+stats_vocal #Gaming`",
                    "permissions": "Rôle autorisé"
                },
                "optimiser_vocal": {
                    "description": "Optimiser automatiquement la distribution",
                    "utilisation": "`+optimiser_vocal @catégorie`",
                    "exemple": "`+optimiser_vocal #Gaming`",
                    "permissions": "Rôle autorisé"
                }
            }
            
            for cmd_name, cmd_info in voice1_commands.items():
                field_value = (
                    f"📝 **Description**: {cmd_info['description']}\n"
                    f"⚙️ **Utilisation**: {cmd_info['utilisation']}\n"
                    f"💡 **Exemple**: {cmd_info['exemple']}\n"
                    f"🔒 **Permissions**: {cmd_info['permissions']}"
                )
                voice1_embed.add_field(name=f"🔧 +{cmd_name}", value=field_value, inline=False)
            
            voice1_embed.set_footer(text="Page 4/9 - Vocal (1/3)")
            pages.append(voice1_embed)
            
            # Page 5: Vocal (partie 2)
            voice2_embed = nextcord.Embed(
                title="🎤 Vocal - Avancé",
                description="Commandes vocales avancées",
                color=0x1ABC9C
            )
            
            voice2_commands = {
                "immobiles": {
                    "description": "Lister les membres qui ne peuvent pas être déplacés",
                    "utilisation": "`+immobiles`",
                    "exemple": "`+immobiles`",
                    "permissions": "Rôle autorisé"
                },
                "force_move": {
                    "description": "Forcer le déplacement malgré les restrictions",
                    "utilisation": "`+force_move @membre #salon`",
                    "exemple": "`+force_move @User #Général`",
                    "permissions": "Rôle autorisé"
                },
                "move_all_except": {
                    "description": "Déplacer tous les membres sauf un",
                    "utilisation": "`+move_all_except @exception #salon`",
                    "exemple": "`+move_all_except @Admin #Réunion`",
                    "permissions": "Rôle autorisé"
                },
                "move_from_category": {
                    "description": "Déplacer depuis une catégorie",
                    "utilisation": "`+move_from_category @source #cible`",
                    "exemple": "`+move_from_category #Gaming #Général`",
                    "permissions": "Rôle autorisé"
                },
                "shuffle_category": {
                    "description": "Mélanger aléatoirement dans une catégorie",
                    "utilisation": "`+shuffle_category @catégorie`",
                    "exemple": "`+shuffle_category #Gaming`",
                    "permissions": "Rôle autorisé"
                }
            }
            
            for cmd_name, cmd_info in voice2_commands.items():
                field_value = (
                    f"📝 **Description**: {cmd_info['description']}\n"
                    f"⚙️ **Utilisation**: {cmd_info['utilisation']}\n"
                    f"💡 **Exemple**: {cmd_info['exemple']}\n"
                    f"🔒 **Permissions**: {cmd_info['permissions']}"
                )
                voice2_embed.add_field(name=f"🔧 +{cmd_name}", value=field_value, inline=False)
            
            voice2_embed.set_footer(text="Page 5/9 - Vocal (2/3)")
            pages.append(voice2_embed)
            
            # Page 6: Vocal (partie 3) et Communication
            voice3_comm_embed = nextcord.Embed(
                title="🎤 Vocal - Création & 📬 Communication",
                description="Commandes de création vocale et communication",
                color=0x1ABC9C
            )
            
            # Vocal création
            vocal_creation = {
                "gather_all": {
                    "description": "Rassembler tout le monde",
                    "utilisation": "`+gather_all #salon`",
                    "exemple": "`+gather_all #Réunion`",
                    "permissions": "Rôle autorisé"
                },
                "create_voice_rooms": {
                    "description": "Créer plusieurs salons vocaux",
                    "utilisation": "`+create_voice_rooms @catégorie <nombre> <nom>`",
                    "exemple": "`+create_voice_rooms #Gaming 5 Team`",
                    "permissions": "Rôle autorisé"
                },
                "clone_voice_channel": {
                    "description": "Cloner un salon vocal",
                    "utilisation": "`+clone_voice_channel #salon <nom>`",
                    "exemple": "`+clone_voice_channel #Gaming Clone`",
                    "permissions": "Rôle autorisé"
                },
                "swap_channels": {
                    "description": "Échanger les membres entre salons",
                    "utilisation": "`+swap_channels #salon1 #salon2`",
                    "exemple": "`+swap_channels #Team1 #Team2`",
                    "permissions": "Rôle autorisé"
                }
            }
            
            for cmd_name, cmd_info in vocal_creation.items():
                field_value = (
                    f"📝 **Description**: {cmd_info['description']}\n"
                    f"⚙️ **Utilisation**: {cmd_info['utilisation']}\n"
                    f"💡 **Exemple**: {cmd_info['exemple']}\n"
                    f"🔒 **Permissions**: {cmd_info['permissions']}"
                )
                voice3_comm_embed.add_field(name=f"🔧 +{cmd_name}", value=field_value, inline=False)
            
            # Communication
            comm_commands = {
                "dmall": {
                    "description": "Envoyer un DM massif",
                    "utilisation": "`+dmall <texte|embed> <contenu>`",
                    "exemple": "`+dmall embed \"Titre\" \"Description\"`",
                    "permissions": "Rôle autorisé"
                },
                "dmtest": {
                    "description": "Tester un DM",
                    "utilisation": "`+dmtest <texte|embed> <contenu>`",
                    "exemple": "`+dmtest embed \"Test\" \"Message test\"`",
                    "permissions": "Rôle autorisé"
                }
            }
            
            for cmd_name, cmd_info in comm_commands.items():
                field_value = (
                    f"📝 **Description**: {cmd_info['description']}\n"
                    f"⚙️ **Utilisation**: {cmd_info['utilisation']}\n"
                    f"💡 **Exemple**: {cmd_info['exemple']}\n"
                    f"🔒 **Permissions**: {cmd_info['permissions']}"
                )
                voice3_comm_embed.add_field(name=f"📧 +{cmd_name}", value=field_value, inline=False)
            
            voice3_comm_embed.set_footer(text="Page 6/9 - Vocal (3/3) & Communication")
            pages.append(voice3_comm_embed)
            
            # Page 7: Social et Sécurité
            social_sec_embed = nextcord.Embed(
                title="📱 Social & 🔒 Sécurité",
                description="Commandes sociales et de sécurité",
                color=0x3498db
            )
            
            social_commands = {
                "live": {
                    "description": "Annoncer un live TikTok",
                    "utilisation": "`+live <message>`",
                    "exemple": "`+live \"Je suis en live ! Venez !\"`",
                    "permissions": "Rôle autorisé"
                },
                "stoplive": {
                    "description": "Arrêter le live",
                    "utilisation": "`+stoplive`",
                    "exemple": "`+stoplive`",
                    "permissions": "Rôle autorisé"
                },
                "finduser": {
                    "description": "Chercher un utilisateur",
                    "utilisation": "`+finduser <pseudo>`",
                    "exemple": "`+finduser laz`",
                    "permissions": "Tout le monde"
                },
                "find": {
                    "description": "Chercher des messages",
                    "utilisation": "`+find <texte>`",
                    "exemple": "`+find \"message important\"`",
                    "permissions": "Tout le monde"
                }
            }
            
            for cmd_name, cmd_info in social_commands.items():
                field_value = (
                    f"📝 **Description**: {cmd_info['description']}\n"
                    f"⚙️ **Utilisation**: {cmd_info['utilisation']}\n"
                    f"💡 **Exemple**: {cmd_info['exemple']}\n"
                    f"🔒 **Permissions**: {cmd_info['permissions']}"
                )
                social_sec_embed.add_field(name=f"🔧 +{cmd_name}", value=field_value, inline=False)
            
            # Sécurité
            security_commands = {
                "whitelist": {
                    "description": "Gérer la whitelist des domaines",
                    "utilisation": "`+whitelist <list|add|remove> <domaine>`",
                    "exemple": "`+whitelist add example.com`",
                    "permissions": "Rôle autorisé"
                },
                "roles": {
                    "description": "Gérer les rôles autorisés",
                    "utilisation": "`+roles <list|add|remove> @rôle`",
                    "exemple": "`+roles add @Modérateur`",
                    "permissions": "Rôle autorisé"
                },
                "checkperms": {
                    "description": "Vérifier les permissions",
                    "utilisation": "`+checkperms @membre`",
                    "exemple": "`+checkperms @User`",
                    "permissions": "Tout le monde"
                }
            }
            
            for cmd_name, cmd_info in security_commands.items():
                field_value = (
                    f"📝 **Description**: {cmd_info['description']}\n"
                    f"⚙️ **Utilisation**: {cmd_info['utilisation']}\n"
                    f"💡 **Exemple**: {cmd_info['exemple']}\n"
                    f"🔒 **Permissions**: {cmd_info['permissions']}"
                )
                social_sec_embed.add_field(name=f"🔐 +{cmd_name}", value=field_value, inline=False)
            
            social_sec_embed.set_footer(text="Page 7/9 - Social & Sécurité")
            pages.append(social_sec_embed)
            
            # Page 8: Jeux
            games_embed = nextcord.Embed(
                title="🎮 Jeux & Divertissement",
                description="Commandes de jeux et divertissement",
                color=0xF39C12
            )
            
            games_commands = {
                "devinelenombre": {
                    "description": "Jeu de devinette de nombre",
                    "utilisation": "`+devinelenombre`",
                    "exemple": "`+devinelenombre`",
                    "permissions": "Tout le monde"
                },
                "dice": {
                    "description": "Lancer un dé",
                    "utilisation": "`+dice <nombre>`",
                    "exemple": "`+dice 6`",
                    "permissions": "Tout le monde"
                },
                "coin": {
                    "description": "Pile ou face",
                    "utilisation": "`+coin`",
                    "exemple": "`+coin`",
                    "permissions": "Tout le monde"
                },
                "rps": {
                    "description": "Pierre feuille ciseaux",
                    "utilisation": "`+rps <pierre|feuille|ciseaux>`",
                    "exemple": "`+rps pierre`",
                    "permissions": "Tout le monde"
                }
            }
            
            for cmd_name, cmd_info in games_commands.items():
                field_value = (
                    f"📝 **Description**: {cmd_info['description']}\n"
                    f"⚙️ **Utilisation**: {cmd_info['utilisation']}\n"
                    f"💡 **Exemple**: {cmd_info['exemple']}\n"
                    f"🔒 **Permissions**: {cmd_info['permissions']}"
                )
                games_embed.add_field(name=f"🎲 +{cmd_name}", value=field_value, inline=False)
            
            games_embed.set_footer(text="Page 8/9 - Jeux")
            pages.append(games_embed)
            
            # Page 9: Informations et commandes vocales restantes
            info_embed = nextcord.Embed(
                title="ℹ️ Informations & 🎤 Vocal Avancé",
                description="Commandes d'information et vocales avancées",
                color=0x95A5A6
            )
            
            # Commandes vocales avancées restantes
            advanced_voice = {
                "voice_activity": {
                    "description": "Activité vocale détaillée",
                    "utilisation": "`+voice_activity [@catégorie]`",
                    "exemple": "`+voice_activity #Gaming`",
                    "permissions": "Rôle autorisé"
                },
                "move_afk": {
                    "description": "Déplacer les membres AFK",
                    "utilisation": "`+move_afk #salon <minutes>`",
                    "exemple": "`+move_afk #AFK 15`",
                    "permissions": "Rôle autorisé"
                },
                "voice_backup": {
                    "description": "Sauvegarder distribution vocale",
                    "utilisation": "`+voice_backup [@catégorie]`",
                    "exemple": "`+voice_backup #Gaming`",
                    "permissions": "Rôle autorisé"
                },
                "voice_restore": {
                    "description": "Restaurer distribution vocale",
                    "utilisation": "`+voice_restore [fichier]`",
                    "exemple": "`+voice_restore backup_gaming.json`",
                    "permissions": "Rôle autorisé"
                },
                "voice_limits": {
                    "description": "Gérer limites de salon",
                    "utilisation": "`+voice_limits #salon <limite>`",
                    "exemple": "`+voice_limits #Team 5`",
                    "permissions": "Rôle autorisé"
                },
                "voice_cleanup": {
                    "description": "Nettoyer les salons vocaux",
                    "utilisation": "`+voice_cleanup [@catégorie]`",
                    "exemple": "`+voice_cleanup #Gaming`",
                    "permissions": "Rôle autorisé"
                }
            }
            
            for cmd_name, cmd_info in advanced_voice.items():
                field_value = (
                    f"📝 **Description**: {cmd_info['description']}\n"
                    f"⚙️ **Utilisation**: {cmd_info['utilisation']}\n"
                    f"💡 **Exemple**: {cmd_info['exemple']}\n"
                    f"🔒 **Permissions**: {cmd_info['permissions']}"
                )
                info_embed.add_field(name=f"🎤 +{cmd_name}", value=field_value, inline=False)
            
            info_embed.add_field(
                name="📊 Statistiques du bot",
                value=(
                    f"🔧 **Total commandes**: 21\n"
                    f"📚 **Catégories**: 8\n"
                    f"👥 **Permissions**: 2 niveaux\n"
                    f"🎮 **Jeux**: 4 disponibles\n"
                    f"🎤 **Vocal**: 21 commandes\n"
                    f"🛡️ **Modération**: 9 commandes"
                ),
                inline=False
            )
            
            info_embed.set_footer(text="Page 9/9 - Informations & Vocal Avancé")
            pages.append(info_embed)
            
            # Envoyer la première page avec le menu de navigation
            view = HelpView(pages, ctx.author)
            await ctx.send(embed=pages[0], view=view)
            
        else:
            # Aide détaillée pour une commande spécifique
            command = command.lower()
            
            # Dictionnaire complet des commandes avec descriptions détaillées
            detailed_helps = {
                "warn": {
                    "name": "🔧 Warn",
                    "description": "Avertir un membre du serveur",
                    "utilisation": "`+warn @membre <raison>`",
                    "exemple": "`+warn @User Spam dans le chat`",
                    "permissions": "Rôle autorisé",
                    "details": (
                        "Cette commande permet d'avertir un membre qui ne respecte pas les règles.\n"
                        "L'avertissement est enregistré et peut être consulté par les modérateurs.\n"
                        "Les avertissements excessifs peuvent mener à des sanctions plus sévères."
                    )
                },
                "kick": {
                    "name": "🔧 Kick",
                    "description": "Expulser temporairement un membre",
                    "utilisation": "`+kick @membre <raison>`",
                    "exemple": "`+kick @User Non respect des règles`",
                    "permissions": "Rôle autorisé",
                    "details": (
                        "Expulse le membre du serveur. Il pourra revenir avec une invitation.\n"
                        "Le kick est enregistré dans les logs de modération.\n"
                        "Utilisé pour les infractions mineures ou les avertissements ignorés."
                    )
                },
                "live": {
                    "name": "📱 Live",
                    "description": "Annoncer un live TikTok",
                    "utilisation": "`+live <message>`",
                    "exemple": "`+live \"Je suis en live ! Venez nombreux !\"`",
                    "permissions": "Rôle autorisé",
                    "details": (
                        "Crée une annonce stylisée pour votre live TikTok.\n"
                        "Ajoute automatiquement le rôle live à l'utilisateur.\n"
                        "Ping le rôle configuré pour les notifications live.\n"
                        "Si aucun message n'est fourni, utilise un message par défaut."
                    )
                },
                "equilibrer": {
                    "name": "🎤 Équilibrer",
                    "description": "Équilibrer les membres dans les salons vocaux",
                    "utilisation": "`+equilibrer @catégorie <nombre_par_salon>`",
                    "exemple": "`+equilibrer #Gaming 3`",
                    "permissions": "Rôle autorisé",
                    "details": (
                        "Distribue équitablement les membres dans les salons vocaux.\n"
                        "Crée automatiquement des salons si nécessaire.\n"
                        "Le nombre par salon doit être entre 2 et 5.\n"
                        "Mélange aléatoirement pour éviter les groupes fixes."
                    )
                },
                "whitelist": {
                    "name": "🔒 Whitelist",
                    "description": "Gérer les domaines autorisés",
                    "utilisation": "`+whitelist <list|add|remove> <domaine>`",
                    "exemple": "`+whitelist add example.com`",
                    "permissions": "Rôle autorisé",
                    "details": (
                        "Gère la liste des domaines autorisés dans les messages.\n"
                        "Les liens vers des domaines non whitelistés sont supprimés.\n"
                        "Actions disponibles: list, add, remove, clear.\n"
                        "Les utilisateurs sont temporairement muets (5s) en cas d'infraction."
                    )
                }
            }
            
            if command in detailed_helps:
                cmd_info = detailed_helps[command]
                
                embed = nextcord.Embed(
                    title=cmd_info["name"],
                    description=cmd_info["description"],
                    color=0x3498db
                )
                
                embed.add_field(
                    name="⚙️ Utilisation",
                    value=cmd_info["utilisation"],
                    inline=False
                )
                
                embed.add_field(
                    name="💡 Exemple",
                    value=cmd_info["exemple"],
                    inline=False
                )
                
                embed.add_field(
                    name="🔒 Permissions requises",
                    value=cmd_info["permissions"],
                    inline=False
                )
                
                embed.add_field(
                    name="📋 Détails",
                    value=cmd_info["details"],
                    inline=False
                )
                
                embed.set_footer(text=f"Aide pour +{command} | Utilise +help pour voir toutes les commandes")
                
                await ctx.send(embed=embed)
                
            else:
                # Chercher des commandes similaires
                similar = [cmd for cmd in detailed_helps.keys() if command in cmd or cmd.startswith(command)]
                
                if similar:
                    embed = nextcord.Embed(
                        title="❌ Commande introuvable",
                        description=f"La commande `+{command}` n'existe pas.\n\nCommandes similaires trouvées :",
                        color=0xE74C3C
                    )
                    
                    similar_text = "\n".join([f"• `+{cmd}`" for cmd in similar[:5]])
                    embed.add_field(name="💡 Suggestions", value=similar_text, inline=False)
                    
                    embed.add_field(
                        name="🔍 Recherche",
                        value="Utilise `+help` pour voir toutes les commandes disponibles",
                        inline=False
                    )
                    
                    await ctx.send(embed=embed)
                else:
                    embed = nextcord.Embed(
                        title="❌ Commande introuvable",
                        description=f"La commande `+{command}` n'existe pas.",
                        color=0xE74C3C
                    )
                    
                    embed.add_field(
                        name="💡 Solution",
                        value="Utilise `+help` pour voir toutes les commandes disponibles",
                        inline=False
                    )
                    
                    await ctx.send(embed=embed)

    async def show_command_list(self, ctx):
        """Afficher la liste des commandes avec descriptions"""
        
        # Organiser les commandes par catégorie
        categories = {
            "🛡️ Modération": ["warn", "kick", "ban", "tempban", "mute", "timeout", "clear", "lock", "unlock"],
            "📊 Logs & Administration": ["logs_setup", "logs_status", "embed", "ping"],
            "🎤 Vocal & Équilibrage": ["déplacer", "equilibrer", "equilibrer_auto", "stats_vocal", "optimiser_vocal", "immobiles", "force_move", "move_all_except", "move_from_category", "shuffle_category", "gather_all", "create_voice_rooms", "clone_voice_channel", "swap_channels", "voice_activity", "move_afk", "voice_backup", "voice_restore", "voice_limits", "voice_cleanup"],
            "📬 Messages & Communication": ["dmall", "dmtest"],
            "🎮 Jeux & Divertissement": ["devinelenombre", "dice", "coin", "rps"],
            "📱 Social & Recherche": ["live", "stoplive", "finduser", "find"],
            "🔒 Anti-modération": ["whitelist"],
            "🔐 Gestion des rôles": ["roles", "checkperms"]
        }
        
        embed = nextcord.Embed(
            title="🤖 Commandes du Bot Stark",
            description="Voici toutes les commandes disponibles avec leurs descriptions.\nUtilise `+help <commande>` pour plus de détails.",
            color=0x3498db
        )
        
        for category_name, commands_list in categories.items():
            commands_text = ""
            for cmd in commands_list:
                # Récupérer la description courte
                descriptions = {
                    "warn": "Avertir un membre",
                    "kick": "Expulser un membre", 
                    "ban": "Bannir un membre",
                    "tempban": "Bannir temporairement",
                    "mute": "Rendre muet un membre",
                    "timeout": "Mettre en timeout",
                    "clear": "Supprimer des messages",
                    "lock": "Verrouiller un salon",
                    "unlock": "Déverrouiller un salon",
                    "logs_setup": "Configurer les logs",
                    "logs_status": "Voir les logs",
                    "embed": "Créer un embed",
                    "ping": "Vérifier la latence",
                    "déplacer": "Déplacer en vocal",
                    "equilibrer": "Équilibrer les salons vocaux",
                    "equilibrer_auto": "Équilibrage automatique",
                    "stats_vocal": "Statistiques vocales",
                    "optimiser_vocal": "Optimiser les salons vocaux",
                    "immobiles": "Lister les membres immobiles",
                    "force_move": "Forcer le déplacement",
                    "move_all_except": "Déplacer tous sauf un",
                    "move_from_category": "Déplacer depuis catégorie",
                    "shuffle_category": "Mélanger catégorie",
                    "gather_all": "Rassembler tout le monde",
                    "create_voice_rooms": "Créer des salons vocaux",
                    "clone_voice_channel": "Cloner un salon vocal",
                    "swap_channels": "Échanger les salons",
                    "voice_activity": "Activité vocale détaillée",
                    "move_afk": "Déplacer les AFK",
                    "voice_backup": "Sauvegarder distribution vocale",
                    "voice_restore": "Restaurer distribution vocale",
                    "voice_limits": "Gérer limites de salon",
                    "voice_cleanup": "Nettoyer les salons vocaux",
                    "dmall": "Envoyer un DM massif",
                    "dmtest": "Tester un DM",
                    "devinelenombre": "Jeu de devinette",
                    "dice": "Lancer un dé",
                    "coin": "Pile ou face",
                    "rps": "Pierre feuille ciseaux",
                    "live": "Annoncer un live TikTok",
                    "stoplive": "Arrêter le live",
                    "finduser": "Chercher un utilisateur",
                    "find": "Chercher des messages",
                    "whitelist": "Gérer les domaines autorisés",
                    "roles": "Gérer les rôles autorisés",
                    "checkperms": "Vérifier les permissions"
                }
                
                desc = descriptions.get(cmd, "Description non disponible")
                commands_text += f"• `+{cmd}` - {desc}\n"
            
            if commands_text:
                embed.add_field(name=category_name, value=commands_text, inline=False)
        
        embed.add_field(
            name="🎯 Comment utiliser",
            value="`+help` - Voir cette liste\n`+help <commande>` - Aide détaillée sur une commande\n\nExemple : `+help warn`",
            inline=False
        )
        
        embed.set_footer(text=f"Demandé par {ctx.author.name} | Made by 𝐒𝐭𝐚𝐫𝐊𝟗𝟐☆🇵🇸")
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        
        await ctx.send(embed=embed)

    @commands.command(name="ping")
    async def ping(self, ctx):
        """Mesurer la latence du bot"""
        start_time = datetime.datetime.now()
        message = await ctx.send("🏓 Pong !")
        end_time = datetime.datetime.now()
        
        latency = (end_time - start_time).total_seconds() * 1000
        api_latency = round(self.bot.latency * 1000, 2)
        
        embed = nextcord.Embed(
            title="🏓 Pong !",
            description=f"Latence du bot : **{latency:.2f}ms**\nLatence API : **{api_latency}ms**",
            color=0x3498db
        )
        
        await message.edit(embed=embed)

    @commands.command(name="embed")
    @has_role()
    async def create_embed(self, ctx, title: str, *, description: str = None):
        """Créer un embed personnalisé"""
        if not description:
            return await ctx.send("❌ Veuillez fournir une description.")
        
        embed = nextcord.Embed(
            title=title,
            description=description,
            color=0x3498db
        )
        
        embed.set_footer(text=f"Créé par {ctx.author.name}")
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(System(bot))
