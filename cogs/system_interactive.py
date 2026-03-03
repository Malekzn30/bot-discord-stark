import nextcord
from nextcord.ext import commands
import asyncio
import datetime
from config import AUTHORIZED_ROLE_ID

class SystemInteractive(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    class HelpView(nextcord.ui.View):
        def __init__(self, bot, author):
            super().__init__(timeout=180)  # 3 minutes timeout
            self.bot = bot
            self.author = author
            self.current_page = 0
            self.current_category = None
            
        async def on_timeout(self):
            """Désactiver les boutons après timeout"""
            for item in self.children:
                item.disabled = True
            await self.message.edit(view=self)

        @nextcord.ui.select(
            placeholder="🎯 Choisis une catégorie...",
            min_values=1,
            max_values=1,
            row=0
        )
        async def category_select(self, select: nextcord.ui.Select, interaction: nextcord.Interaction):
            """Sélection d'une catégorie"""
            if interaction.user != self.author:
                await interaction.response.send_message("❌ Tu ne peux pas utiliser ce menu !", ephemeral=True)
                return
                
            category_map = {
                "🛡️ Modération": "moderation",
                "🎤 Vocal": "vocal", 
                "🎮 Jeux": "games",
                "🎉 Communauté": "community",
                "🛠️ Utilitaires": "utility",
                "😂 Fun": "fun",
                "🚀 Étendu": "extended",
                "⚙️ Configuration": "config",
                "📊 Performance": "performance"
            }
            
            selected = select.values[0]
            self.current_category = category_map.get(selected, selected.lower())
            self.current_page = 0
            
            await self.update_help_message(interaction)

        @nextcord.ui.button(label="⬅️ Précédent", style=nextcord.ButtonStyle.secondary, row=1)
        async def previous_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
            """Page précédente"""
            if interaction.user != self.author:
                await interaction.response.send_message("❌ Tu ne peux pas utiliser ce menu !", ephemeral=True)
                return
                
            if self.current_page > 0:
                self.current_page -= 1
                await self.update_help_message(interaction)

        @nextcord.ui.button(label="➡️ Suivant", style=nextcord.ButtonStyle.secondary, row=1)
        async def next_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
            """Page suivante"""
            if interaction.user != self.author:
                await interaction.response.send_message("❌ Tu ne peux pas utiliser ce menu !", ephemeral=True)
                return
                
            self.current_page += 1
            await self.update_help_message(interaction)

        @nextcord.ui.button(label="🔙 Retour", style=nextcord.ButtonStyle.primary, row=1)
        async def back_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
            """Retour au menu principal"""
            if interaction.user != self.author:
                await interaction.response.send_message("❌ Tu ne peux pas utiliser ce menu !", ephemeral=True)
                return
                
            self.current_category = None
            self.current_page = 0
            await self.show_main_menu(interaction)

        async def update_help_message(self, interaction):
            """Mettre à jour le message d'aide"""
            if self.current_category == "moderation":
                await self.show_moderation_help(interaction)
            elif self.current_category == "vocal":
                await self.show_vocal_help(interaction)
            elif self.current_category == "games":
                await self.show_games_help(interaction)
            elif self.current_category == "community":
                await self.show_community_help(interaction)
            elif self.current_category == "utility":
                await self.show_utility_help(interaction)
            elif self.current_category == "fun":
                await self.show_fun_help(interaction)
            elif self.current_category == "extended":
                await self.show_extended_help(interaction)
            elif self.current_category == "config":
                await self.show_config_help(interaction)
            elif self.current_category == "performance":
                await self.show_performance_help(interaction)
            else:
                await self.show_main_menu(interaction)

        async def show_main_menu(self, interaction):
            """Afficher le menu principal"""
            embed = nextcord.Embed(
                title="🤖 Bot Stark - Menu Interactif",
                description="**150+ Commandes** organisées par catégories\n\n👇 **Choisis une catégorie ci-dessous**",
                color=0x3498db,
                timestamp=datetime.datetime.now()
            )
            
            embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
            
            # Statistiques
            embed.add_field(
                name="📊 Statistiques",
                value=f"**Total:** 152+ commandes\n**Catégories:** 9\n**Prefixe:** `+`\n**Permissions:** Configurables",
                inline=False
            )
            
            # Instructions
            embed.add_field(
                name="🎯 Comment utiliser",
                value="1. **Sélectionne une catégorie** dans le menu déroulant\n2. **Navigue** entre les pages avec les boutons\n3. **Retour** au menu principal avec le bouton 🔙",
                inline=False
            )
            
            embed.set_footer(text=f"Demandé par {self.author.name} • Utilise +help <commande> pour l'aide spécifique")
            
            # Mettre à jour le sélecteur
            self.category_select.options = [
                nextcord.SelectOption(
                    label="🛡️ Modération",
                    description="15 commandes de modération avancée",
                    emoji="🛡️"
                ),
                nextcord.SelectOption(
                    label="🎤 Vocal",
                    description="23 commandes de gestion vocale",
                    emoji="🎤"
                ),
                nextcord.SelectOption(
                    label="🎮 Jeux",
                    description="10 commandes de jeux et divertissement",
                    emoji="🎮"
                ),
                nextcord.SelectOption(
                    label="🎉 Communauté",
                    description="10 commandes communautaires",
                    emoji="🎉"
                ),
                nextcord.SelectOption(
                    label="🛠️ Utilitaires",
                    description="12 commandes utilitaires",
                    emoji="🛠️"
                ),
                nextcord.SelectOption(
                    label="😂 Fun",
                    description="10 commandes d'amusement",
                    emoji="😂"
                ),
                nextcord.SelectOption(
                    label="🚀 Étendu",
                    description="17 commandes avancées",
                    emoji="🚀"
                ),
                nextcord.SelectOption(
                    label="⚙️ Configuration",
                    description="10 commandes de configuration",
                    emoji="⚙️"
                ),
                nextcord.SelectOption(
                    label="📊 Performance",
                    description="4 commandes de monitoring",
                    emoji="📊"
                )
            ]
            
            # Mettre à jour les boutons
            self.previous_button.disabled = True
            self.next_button.disabled = True
            self.back_button.disabled = True
            
            await interaction.response.edit_message(embed=embed, view=self)

        async def show_moderation_help(self, interaction):
            """Afficher l'aide de la modération avec pagination"""
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
                ("antiraid", "Activer l'anti-raid", "+antiraid", "Admin")
            ]
            
            await self.show_paginated_commands(interaction, "🛡️ Modération Avancée", commands, 0x3498db)

        async def show_vocal_help(self, interaction):
            """Afficher l'aide du vocal avec pagination"""
            commands = [
                ("déplacer", "Déplacer un membre en vocal", "+déplacer @membre #salon", "Admin/Modo"),
                ("lockmember", "Bloquer un membre dans son salon vocal", "+lockmember @membre", "Admin/Modo"),
                ("unlockmember", "Débloquer un membre vocal", "+unlockmember @membre", "Admin/Modo"),
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
                ("voice_cleanup", "Nettoyer les salons vides", "+voice_cleanup", "Admin/Modo"),
                ("lockvoice", "Verrouiller un salon vocal", "+lockvoice #salon", "Admin/Modo"),
                ("unlockvoice", "Déverrouiller un salon vocal", "+unlockvoice #salon", "Admin/Modo"),
                ("moove", "Déplacer un membre (alias)", "+moove @membre #salon", "Admin/Modo")
            ]
            
            await self.show_paginated_commands(interaction, "🎤 Gestion Vocale Complète", commands, 0x1ABC9C)

        async def show_games_help(self, interaction):
            """Afficher l'aide des jeux avec pagination"""
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
            
            await self.show_paginated_commands(interaction, "🎮 Jeux et Divertissement", commands, 0xF39C12)

        async def show_community_help(self, interaction):
            """Afficher l'aide communautaire avec pagination"""
            commands = [
                ("suggest", "Faire une suggestion", "+suggest <idée>", "Tout le monde"),
                ("poll", "Créer un sondage", "+poll <question> [options]", "Admin/Modo"),
                ("giveaway", "Lancer un giveaway", "+giveaway <temps> <prix>", "Admin/Modo"),
                ("vote", "Voter pour une suggestion", "+vote <numéro>", "Tout le monde"),
                ("suggestions", "Voir les suggestions", "+suggestions", "Tout le monde"),
                ("announce", "Faire une annonce", "+announce <message>", "Admin/Modo"),
                ("welcome", "Message de bienvenue", "+welcome @membre", "Admin/Modo"),
                ("goodbye", "Message d'au revoir", "+goodbye @membre", "Admin/Modo"),
                ("birthday", "Enregistrer un anniversaire", "+birthday @membre <date>", "Tout le monde"),
                ("birthdays", "Voir les anniversaires", "+birthdays", "Tout le monde")
            ]
            
            await self.show_paginated_commands(interaction, "🎉 Fonctionnalités Communautaires", commands, 0x9B59B6)

        async def show_utility_help(self, interaction):
            """Afficher l'aide des utilitaires avec pagination"""
            commands = [
                ("afk", "Mettre son statut AFK", "+afk [raison]", "Tout le monde"),
                ("snipe", "Voir le dernier message supprimé", "+snipe", "Tout le monde"),
                ("calc", "Calculatrice", "+calc <expression>", "Tout le monde"),
                ("translate", "Traduire un texte", "+translate <langue> <texte>", "Tout le monde"),
                ("weather", "Météo d'une ville", "+weather <ville>", "Tout le monde"),
                ("urban", "Définition Urban Dictionary", "+urban <terme>", "Tout le monde"),
                ("remind", "Créer un rappel", "+remind <temps> <message>", "Tout le monde"),
                ("reminders", "Voir ses rappels", "+reminders", "Tout le monde"),
                ("timer", "Démarrer un minuteur", "+timer <temps>", "Tout le monde"),
                ("stopwatch", "Chronomètre", "+stopwatch", "Tout le monde"),
                ("countdown", "Compte à rebours", "+countdown <temps>", "Admin/Modo"),
                ("ping", "Voir la latence du bot", "+ping", "Tout le monde")
            ]
            
            await self.show_paginated_commands(interaction, "🛠️ Commandes Utilitaires", commands, 0x3498db)

        async def show_fun_help(self, interaction):
            """Afficher l'aide fun avec pagination"""
            commands = [
                ("meme", "Afficher un mème aléatoire", "+meme", "Tout le monde"),
                ("joke", "Blague aléatoire", "+joke", "Tout le monde"),
                ("ascii", "Convertir en texte ASCII", "+ascii <texte>", "Tout le monde"),
                ("emoji", "Afficher un emoji en grand", "+emoji <emoji>", "Tout le monde"),
                ("flip", "Retourner du texte", "+flip <texte>", "Tout le monde"),
                ("say", "Faire parler le bot", "+say <message>", "Admin/Modo"),
                ("reverse", "Écrire à l'envers", "+reverse <texte>", "Tout le monde"),
                ("zalgofy", "Texte en Zalgo", "+zalgofy <texte>", "Tout le monde"),
                ("vaporwave", "Texte en vaporwave", "+vaporwave <texte>", "Tout le monde"),
                ("clap", "Texte avec clap", "+clap <texte>", "Tout le monde")
            ]
            
            await self.show_paginated_commands(interaction, "😂 Commandes d'Amusement", commands, 0xE91E63)

        async def show_extended_help(self, interaction):
            """Afficher l'aide étendue avec pagination"""
            commands = [
                ("todo", "Gérer sa liste de tâches", "+todo <add/remove/list>", "Tout le monde"),
                ("rank", "Voir son rang", "+rank [@membre]", "Tout le monde"),
                ("play", "Jouer de la musique", "+play <titre/URL>", "Tout le monde"),
                ("skip", "Passer la musique", "+skip", "Tout le monde"),
                ("queue", "Voir la file d'attente", "+queue", "Tout le monde"),
                ("stop", "Arrêter la musique", "+stop", "Tout le monde"),
                ("volume", "Régler le volume", "+volume <0-100>", "Tout le monde"),
                ("weather", "Météo d'une ville", "+weather <ville>", "Tout le monde"),
                ("news", "Dernières actualités", "+news [sujet]", "Tout le monde"),
                ("crypto", "Prix des cryptomonnaies", "+crypto <monnaie>", "Tout le monde"),
                ("stock", "Prix des actions", "+stock <symbole>", "Tout le monde"),
                ("translate", "Traduire un texte", "+translate <langue> <texte>", "Tout le monde"),
                ("wiki", "Rechercher sur Wikipédia", "+wiki <terme>", "Tout le monde"),
                ("youtube", "Rechercher sur YouTube", "+youtube <terme>", "Tout le monde"),
                ("google", "Rechercher sur Google", "+google <terme>", "Tout le monde"),
                ("image", "Rechercher une image", "+image <terme>", "Tout le monde"),
                ("gif", "Rechercher un GIF", "+gif <terme>", "Tout le monde")
            ]
            
            await self.show_paginated_commands(interaction, "🚀 Commandes Étendues", commands, 0x2ECC71)

        async def show_config_help(self, interaction):
            """Afficher l'aide de configuration avec pagination"""
            commands = [
                ("config", "Menu de configuration", "+config", "Admin"),
                ("setname", "Changer le nom du bot", "+setname <nom>", "Admin"),
                ("setavatar", "Changer l'avatar du bot", "+setavatar <URL>", "Admin"),
                ("setprefix", "Changer le préfixe", "+setprefix <préfixe>", "Admin"),
                ("setwelcome", "Configurer le message de bienvenue", "+setwelcome <message>", "Admin"),
                ("setgoodbye", "Configurer le message d'au revoir", "+setgoodbye <message>", "Admin"),
                ("setlogs", "Configurer les logs", "+setlogs #salon", "Admin"),
                ("autorole", "Configurer les rôles automatiques", "+autorole @rôle", "Admin"),
                ("levelup", "Configurer les niveaux", "+levelup <on/off>", "Admin"),
                ("backup", "Sauvegarder la configuration", "+backup", "Admin")
            ]
            
            await self.show_paginated_commands(interaction, "⚙️ Configuration du Bot", commands, 0x95A5A6)

        async def show_performance_help(self, interaction):
            """Afficher l'aide performance avec pagination"""
            commands = [
                ("performance", "Voir les performances du bot", "+performance", "Admin"),
                ("optimize", "Optimiser le bot", "+optimize", "Admin"),
                ("restart", "Redémarrer le bot", "+restart", "Admin"),
                ("stats", "Voir les statistiques", "+stats", "Admin")
            ]
            
            await self.show_paginated_commands(interaction, "📊 Monitoring et Performance", commands, 0xE67E22)

        async def show_paginated_commands(self, interaction, title, commands, color):
            """Afficher les commandes avec pagination (5 par page)"""
            commands_per_page = 5
            total_pages = (len(commands) + commands_per_page - 1) // commands_per_page
            
            # S'assurer que la page actuelle est valide
            if self.current_page >= total_pages:
                self.current_page = total_pages - 1
            if self.current_page < 0:
                self.current_page = 0
            
            # Calculer les commandes pour cette page
            start_idx = self.current_page * commands_per_page
            end_idx = start_idx + commands_per_page
            page_commands = commands[start_idx:end_idx]
            
            embed = nextcord.Embed(
                title=f"{title} (Page {self.current_page + 1}/{total_pages})",
                description=f"**{len(commands)} commandes au total**",
                color=color,
                timestamp=datetime.datetime.now()
            )
            
            for cmd, desc, usage, perm in page_commands:
                embed.add_field(
                    name=f"🔹 {cmd}",
                    value=f"**Description:** {desc}\n**Usage:** `{usage}`\n**Permissions:** {perm}",
                    inline=False
                )
            
            embed.set_footer(text=f"Demandé par {self.author.name} • Page {self.current_page + 1}/{total_pages}")
            
            # Mettre à jour l'état des boutons
            self.previous_button.disabled = (self.current_page == 0)
            self.next_button.disabled = (self.current_page >= total_pages - 1)
            self.back_button.disabled = False
            
            await interaction.response.edit_message(embed=embed, view=self)

    @commands.command(name="help")
    async def help_interactive(self, ctx):
        """Système d'aide interactif avec menu déroulant et pagination"""
        
        # Créer la vue interactive
        view = self.HelpView(self.bot, ctx.author)
        
        # Envoyer le message initial
        await view.show_main_menu(ctx)
        view.message = await ctx.fetch_message(ctx.channel.last_message_id)

def setup(bot):
    bot.add_cog(SystemInteractive(bot))
