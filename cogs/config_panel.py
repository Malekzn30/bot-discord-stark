import nextcord
from nextcord.ext import commands
import asyncio
import datetime
from utils.config_manager import config_manager

class ConfigView(nextcord.ui.View):
    def __init__(self, author, cog):
        super().__init__(timeout=300)
        self.author = author
        self.cog = cog
        self.current_page = "main"
    
    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("❌ Tu ne peux pas utiliser ce menu !", ephemeral=True)
            return False
        return True
    
    @nextcord.ui.button(label="🎨 Apparence", style=nextcord.ButtonStyle.primary, row=0)
    async def appearance_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.cog.show_appearance_config(interaction, self)
    
    @nextcord.ui.button(label="⚙️ Fonctionnalités", style=nextcord.ButtonStyle.primary, row=0)
    async def features_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.cog.show_features_config(interaction, self)
    
    @nextcord.ui.button(label="🔐 Permissions", style=nextcord.ButtonStyle.primary, row=0)
    async def permissions_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.cog.show_permissions_config(interaction, self)
    
    @nextcord.ui.button(label="💬 Messages", style=nextcord.ButtonStyle.primary, row=1)
    async def messages_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.cog.show_messages_config(interaction, self)
    
    @nextcord.ui.button(label="🎤 Vocal", style=nextcord.ButtonStyle.primary, row=1)
    async def vocal_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.cog.show_vocal_config(interaction, self)
    
    @nextcord.ui.button(label="🎮 Jeux", style=nextcord.ButtonStyle.primary, row=1)
    async def games_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.cog.show_games_config(interaction, self)
    
    @nextcord.ui.button(label="💾 Sauvegarder", style=nextcord.ButtonStyle.success, row=2)
    async def save_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if config_manager.save_config():
            await interaction.response.send_message("✅ Configuration sauvegardée avec succès !", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Erreur lors de la sauvegarde !", ephemeral=True)
    
    @nextcord.ui.button(label="🔄 Réinitialiser", style=nextcord.ButtonStyle.danger, row=2)
    async def reset_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.cog.show_reset_confirm(interaction, self)
    
    @nextcord.ui.button(label="❌ Fermer", style=nextcord.ButtonStyle.secondary, row=2)
    async def close_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.edit_message(view=None)

class ConfigPanel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="config")
    @commands.has_permissions(administrator=True)
    async def config_command(self, ctx):
        """Panneau de configuration du bot"""
        embed = nextcord.Embed(
            title="⚙️ Panneau de Configuration",
            description="Configurez votre bot Stark selon vos besoins !",
            color=0x3498db
        )
        
        embed.add_field(
            name="🎨 Apparence",
            value="Personnalisez le nom, la photo de profil, la bannière, etc.",
            inline=False
        )
        
        embed.add_field(
            name="⚙️ Fonctionnalités",
            value="Activez/désactivez les fonctionnalités du bot",
            inline=False
        )
        
        embed.add_field(
            name="🔐 Permissions",
            value="Gérez les rôles et permissions",
            inline=False
        )
        
        embed.add_field(
            name="💬 Messages",
            value="Personnalisez les messages d'accueil, etc.",
            inline=False
        )
        
        embed.add_field(
            name="🎤 Vocal",
            value="Configurez les salons vocaux et l'équilibrage",
            inline=False
        )
        
        embed.add_field(
            name="🎮 Jeux",
            value="Activez les jeux et récompenses",
            inline=False
        )
        
        embed.set_footer(text="Utilisez les boutons pour naviguer")
        view = ConfigView(ctx.author, self)
        await ctx.send(embed=embed, view=view)
    
    async def show_appearance_config(self, interaction, view):
        """Afficher la configuration de l'apparence"""
        embed = nextcord.Embed(
            title="🎨 Configuration de l'Apparence",
            description="Personnalisez l'apparence du bot",
            color=0x3498db
        )
        
        current_config = {
            "Nom": config_manager.get("bot.name", "Bot Stark"),
            "Préfixe": config_manager.get("bot.prefix", "+"),
            "Description": config_manager.get("bot.description", "Bot Discord multifonctionnel"),
            "Bio": config_manager.get("appearance.bio", "Bot Discord multifonctionnel"),
            "Statut": config_manager.get("appearance.status", "online"),
            "Activité": f"{config_manager.get('appearance.activity_type', 'watching')} {config_manager.get('appearance.activity_text', 'vos serveurs')}"
        }
        
        for key, value in current_config.items():
            embed.add_field(name=key, value=f"`{value}`", inline=True)
        
        embed.add_field(
            name="🎨 Couleurs",
            value=(
                f"Primaire: `#{config_manager.get('appearance.color_scheme.primary', 0x3498db):06x}`\n"
                f"Succès: `#{config_manager.get('appearance.color_scheme.success', 0x2ECC71):06x}`\n"
                f"Attention: `#{config_manager.get('appearance.color_scheme.warning', 0xF39C12):06x}`"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🔧 Comment modifier",
            value=(
                "Utilisez les commandes suivantes :\n"
                "`+setname <nom>` - Changer le nom\n"
                "`+setprefix <prefixe>` - Changer le préfixe\n"
                "`+setbio <bio>` - Changer la bio\n"
                "`+setstatus <status>` - Changer le statut\n"
                "`+setactivity <type> <texte>` - Changer l'activité"
            ),
            inline=False
        )
        
        await interaction.response.edit_message(embed=embed, view=view)
    
    async def show_features_config(self, interaction, view):
        """Afficher la configuration des fonctionnalités"""
        embed = nextcord.Embed(
            title="⚙️ Configuration des Fonctionnalités",
            description="Activez ou désactivez les fonctionnalités",
            color=0x3498db
        )
        
        features = {
            "Modération": config_manager.get("features.moderation.enabled", True),
            "Auto-modération": config_manager.get("features.moderation.auto_mod", False),
            "Vocal": config_manager.get("features.vocal.enabled", True),
            "Équilibrage auto": config_manager.get("features.vocal.auto_balance", False),
            "Social": config_manager.get("features.social.enabled", True),
            "Notifications Live": config_manager.get("features.social.live_notifications", True),
            "Jeux": config_manager.get("features.games.enabled", True),
            "Récompenses quotidiennes": config_manager.get("features.games.daily_rewards", False)
        }
        
        for feature, enabled in features.items():
            status = "✅ Activé" if enabled else "❌ Désactivé"
            embed.add_field(name=feature, value=status, inline=True)
        
        embed.add_field(
            name="🔧 Comment modifier",
            value=(
                "Utilisez les commandes suivantes :\n"
                "`+toggle <feature>` - Activer/désactiver une fonctionnalité\n"
                "`+setconfig <path> <value>` - Définir une configuration"
            ),
            inline=False
        )
        
        await interaction.response.edit_message(embed=embed, view=view)
    
    async def show_permissions_config(self, interaction, view):
        """Afficher la configuration des permissions"""
        embed = nextcord.Embed(
            title="🔐 Configuration des Permissions",
            description="Gérez les rôles et permissions",
            color=0x3498db
        )
        
        admin_roles = config_manager.get("permissions.admin_roles", [])
        mod_roles = config_manager.get("permissions.moderator_roles", [])
        trusted_users = config_manager.get("permissions.trusted_users", [])
        
        embed.add_field(
            name="👑 Rôles Admin",
            value=f"{len(admin_roles)} rôle(s) configuré(s)" if admin_roles else "Aucun",
            inline=False
        )
        
        embed.add_field(
            name="🛡️ Rôles Modérateur",
            value=f"{len(mod_roles)} rôle(s) configuré(s)" if mod_roles else "Aucun",
            inline=False
        )
        
        embed.add_field(
            name="✅ Utilisateurs de confiance",
            value=f"{len(trusted_users)} utilisateur(s) configuré(s)" if trusted_users else "Aucun",
            inline=False
        )
        
        embed.add_field(
            name="🔧 Comment modifier",
            value=(
                "Utilisez les commandes suivantes :\n"
                "`+addadmin <@rôle>` - Ajouter un rôle admin\n"
                "`+removadmin <@rôle>` - Retirer un rôle admin\n"
                "`+addmod <@rôle>` - Ajouter un rôle modérateur\n"
                "`+trust <@utilisateur>` - Ajouter un utilisateur de confiance"
            ),
            inline=False
        )
        
        await interaction.response.edit_message(embed=embed, view=view)
    
    async def show_messages_config(self, interaction, view):
        """Afficher la configuration des messages"""
        embed = nextcord.Embed(
            title="💬 Configuration des Messages",
            description="Personnalisez les messages automatiques",
            color=0x3498db
        )
        
        messages = {
            "Message d'accueil": config_manager.get("messages.welcome_message", "Bienvenue {user} sur {server} !"),
            "Message d'au revoir": config_manager.get("messages.goodbye_message", "Au revoir {user} !"),
            "Message de niveau": config_manager.get("messages.level_up_message", "Félicitations {user}, tu as atteint le niveau {level} !")
        }
        
        for msg_type, message in messages.items():
            embed.add_field(name=msg_type, value=f"`{message[:50]}...`" if len(message) > 50 else f"`{message}`", inline=False)
        
        embed.add_field(
            name="🔧 Comment modifier",
            value=(
                "Utilisez les commandes suivantes :\n"
                "`+setwelcome <message>` - Message d'accueil\n"
                "`+setgoodbye <message>` - Message d'au revoir\n"
                "`+setlevelup <message>` - Message de niveau\n"
                "Variables: {user}, {server}, {level}"
            ),
            inline=False
        )
        
        await interaction.response.edit_message(embed=embed, view=view)
    
    async def show_vocal_config(self, interaction, view):
        """Afficher la configuration vocale"""
        embed = nextcord.Embed(
            title="🎤 Configuration Vocale",
            description="Configurez les fonctionnalités vocales",
            color=0x3498db
        )
        
        vocal_config = {
            "Salons vocaux activés": config_manager.get("features.vocal.enabled", True),
            "Équilibrage automatique": config_manager.get("features.vocal.auto_balance", False),
            "Max par salon": config_manager.get("features.vocal.max_members_per_channel", 5),
            "Salons temporaires": config_manager.get("features.vocal.create_temp_channels", False)
        }
        
        for setting, value in vocal_config.items():
            if isinstance(value, bool):
                status = "✅ Activé" if value else "❌ Désactivé"
                embed.add_field(name=setting, value=status, inline=True)
            else:
                embed.add_field(name=setting, value=f"`{value}`", inline=True)
        
        embed.add_field(
            name="🔧 Comment modifier",
            value=(
                "Utilisez les commandes suivantes :\n"
                "`+setvocalmax <nombre>` - Max membres par salon\n"
                "`+toggletempchannels` - Activer/désactiver les salons temporaires\n"
                "`+setautobalance <on/off>` - Équilibrage automatique"
            ),
            inline=False
        )
        
        await interaction.response.edit_message(embed=embed, view=view)
    
    async def show_games_config(self, interaction, view):
        """Afficher la configuration des jeux"""
        embed = nextcord.Embed(
            title="🎮 Configuration des Jeux",
            description="Configurez les fonctionnalités de jeux",
            color=0x3498db
        )
        
        games_config = {
            "Jeux activés": config_manager.get("features.games.enabled", True),
            "Récompenses quotidiennes": config_manager.get("features.games.daily_rewards", False),
            "Classements": config_manager.get("features.games.leaderboards", False)
        }
        
        for setting, value in games_config.items():
            status = "✅ Activé" if value else "❌ Désactivé"
            embed.add_field(name=setting, value=status, inline=True)
        
        embed.add_field(
            name="🔧 Comment modifier",
            value=(
                "Utilisez les commandes suivantes :\n"
                "`+togglegames` - Activer/désactiver les jeux\n"
                "`+toggledailyrewards` - Activer/désactiver les récompenses\n"
                "`+toggleleaderboards` - Activer/désactiver les classements"
            ),
            inline=False
        )
        
        await interaction.response.edit_message(embed=embed, view=view)
    
    async def show_reset_confirm(self, interaction, view):
        """Afficher la confirmation de réinitialisation"""
        embed = nextcord.Embed(
            title="⚠️ Confirmation de Réinitialisation",
            description="Êtes-vous sûr de vouloir réinitialiser toute la configuration ?\n\nCette action est **irréversible** !",
            color=0xE74C3C
        )
        
        embed.add_field(
            name="📋 Ce qui sera réinitialisé",
            value=(
                "• Toute l'apparence du bot\n"
                "• Toutes les fonctionnalités\n"
                "• Toutes les permissions\n"
                "• Tous les messages personnalisés\n"
                "• Toute la configuration vocale et jeux"
            ),
            inline=False
        )
        
        # Créer une vue temporaire pour la confirmation
        confirm_view = nextcord.ui.View(timeout=60)
        
        async def confirm_callback(interaction: nextcord.Interaction):
            if interaction.user.id != view.author.id:
                await interaction.response.send_message("❌ Tu ne peux pas utiliser ce bouton !", ephemeral=True)
                return
            
            config_manager.reset_to_default()
            await interaction.response.edit_message(
                embed=nextcord.Embed(
                    title="✅ Configuration Réinitialisée",
                    description="La configuration a été réinitialisée avec succès !",
                    color=0x2ECC71
                ),
                view=None
            )
        
        async def cancel_callback(interaction: nextcord.Interaction):
            if interaction.user.id != view.author.id:
                await interaction.response.send_message("❌ Tu ne peux pas utiliser ce bouton !", ephemeral=True)
                return
            
            await interaction.response.edit_message(
                embed=nextcord.Embed(
                    title="❌ Annulé",
                    description="La réinitialisation a été annulée.",
                    color=0xE74C3C
                ),
                view=view
            )
        
        confirm_view.add_item(
            nextcord.ui.Button(
                label="✅ Confirmer",
                style=nextcord.ButtonStyle.danger,
                callback=confirm_callback
            )
        )
        
        confirm_view.add_item(
            nextcord.ui.Button(
                label="❌ Annuler",
                style=nextcord.ButtonStyle.secondary,
                callback=cancel_callback
            )
        )
        
        await interaction.response.edit_message(embed=embed, view=confirm_view)

def setup(bot):
    bot.add_cog(ConfigPanel(bot))
