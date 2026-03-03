import nextcord
from nextcord.ext import commands
import json
import os
import datetime
from config import AUTHORIZED_ROLE_ID

class ServerConfig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ensure_data_directory()

    def ensure_data_directory(self):
        """S'assurer que le répertoire data/config existe"""
        os.makedirs("data/config", exist_ok=True)

    def get_config_file(self, guild_id):
        """Obtenir le fichier de configuration d'un serveur"""
        return f"data/config/{guild_id}.json"

    def load_config(self, guild_id):
        """Charger la configuration d'un serveur"""
        config_file = self.get_config_file(guild_id)
        
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Configuration par défaut
            return {
                "antilink": {
                    "enabled": False,
                    "action": "delete",  # delete, warn, kick
                    "whitelist": [],
                    "exempt_roles": []
                },
                "antiinvite": {
                    "enabled": False,
                    "action": "delete",
                    "whitelist": [],
                    "exempt_roles": []
                },
                "antispam": {
                    "enabled": False,
                    "max_messages": 5,
                    "time_window": 10,  # secondes
                    "action": "mute",
                    "duration": 300  # secondes
                },
                "caps": {
                    "enabled": False,
                    "max_caps": 10,
                    "action": "warn",
                    "exempt_roles": []
                },
                "swear": {
                    "enabled": False,
                    "words": [],
                    "action": "delete",
                    "exempt_roles": []
                },
                "welcome": {
                    "enabled": False,
                    "channel_id": None,
                    "message": "Bienvenue {user} sur {server} !",
                    "role_id": None,
                    "dm_enabled": False,
                    "dm_message": "Bienvenue sur {server} !"
                },
                "goodbye": {
                    "enabled": False,
                    "channel_id": None,
                    "message": "Au revoir {user} !"
                },
                "level": {
                    "enabled": False,
                    "channel_id": None,
                    "message": "{user} a atteint le niveau {level} !",
                    "role_rewards": {}
                },
                "logs": {
                    "enabled": False,
                    "channel_id": None,
                    "events": ["join", "leave", "ban", "kick", "message_delete", "message_edit"]
                },
                "auto_roles": {
                    "enabled": False,
                    "roles": []
                },
                "tickets": {
                    "enabled": False,
                    "category_id": None,
                    "support_role_id": None,
                    "transcript_channel_id": None
                },
                "moderation": {
                    "warn_threshold": 3,
                    "kick_threshold": 5,
                    "ban_threshold": 10,
                    "auto_actions": True
                }
            }

    def save_config(self, guild_id, config):
        """Sauvegarder la configuration d'un serveur"""
        config_file = self.get_config_file(guild_id)
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def has_admin_permission(ctx):
        """Vérifier si l'utilisateur a les permissions d'administration"""
        return ctx.author.guild_permissions.administrator or any(role.id == AUTHORIZED_ROLE_ID for role in ctx.author.roles)

    class ConfigView(nextcord.ui.View):
        def __init__(self, bot, author, guild_id):
            super().__init__(timeout=300)
            self.bot = bot
            self.author = author
            self.guild_id = guild_id
            self.current_page = 0

        async def on_timeout(self):
            """Désactiver les boutons après timeout"""
            for item in self.children:
                item.disabled = True
            await self.message.edit(view=self)

        @nextcord.ui.select(
            placeholder="🔧 Choisis une catégorie de configuration...",
            min_values=1,
            max_values=1,
            row=0
        )
        async def config_select(self, select: nextcord.ui.Select, interaction: nextcord.Interaction):
            """Sélection d'une catégorie de configuration"""
            if interaction.user != self.author:
                await interaction.response.send_message("❌ Tu ne peux pas utiliser ce menu !", ephemeral=True)
                return
                
            category = select.values[0]
            await self.show_category_config(interaction, category)

        async def show_category_config(self, interaction, category):
            """Afficher la configuration d'une catégorie"""
            cog = self.bot.get_cog("ServerConfig")
            config = cog.load_config(self.guild_id)
            
            if category == "🛡️ Modération":
                await self.show_moderation_config(interaction, config)
            elif category == "🔗 Anti-Link":
                await self.show_antilink_config(interaction, config)
            elif category == "🎉 Bienvenue":
                await self.show_welcome_config(interaction, config)
            elif category == "📊 Logs":
                await self.show_logs_config(interaction, config)
            elif category == "🎭 Auto-Rôles":
                await self.show_autoroles_config(interaction, config)
            elif category == "🎫 Tickets":
                await self.show_tickets_config(interaction, config)
            elif category == "📈 Niveaux":
                await self.show_level_config(interaction, config)
            elif category == "🚫 Anti-Spam":
                await self.show_antispam_config(interaction, config)

        async def show_moderation_config(self, interaction, config):
            """Afficher la configuration de modération"""
            embed = nextcord.Embed(
                title="🛡️ Configuration - Modération",
                description="Paramètres de modération automatique",
                color=0xE74C3C
            )
            
            mod_config = config["moderation"]
            embed.add_field(
                name="⚠️ Seuils d'avertissement",
                value=f"**Warn:** {mod_config['warn_threshold']} warns\n**Kick:** {mod_config['kick_threshold']} warns\n**Ban:** {mod_config['ban_threshold']} warns",
                inline=True
            )
            
            embed.add_field(
                name="🤖 Actions automatiques",
                value=f"**Activé:** {'✅' if mod_config['auto_actions'] else '❌'}",
                inline=True
            )
            
            embed.add_field(
                name="🔧 Commandes disponibles",
                value="`+modwarns <nombre>`\n`+modkick <nombre>`\n`+modban <nombre>`\n`+modauto <on/off>`",
                inline=False
            )
            
            await interaction.response.edit_message(embed=embed, view=self)

        async def show_antilink_config(self, interaction, config):
            """Afficher la configuration anti-link"""
            embed = nextcord.Embed(
                title="🔗 Configuration - Anti-Link",
                description="Paramètres de protection contre les liens",
                color=0x3498db
            )
            
            antilink = config["antilink"]
            antiinvite = config["antiinvite"]
            
            embed.add_field(
                name="🔗 Anti-Link",
                value=f"**Activé:** {'✅' if antilink['enabled'] else '❌'}\n**Action:** {antilink['action']}",
                inline=True
            )
            
            embed.add_field(
                name="📨 Anti-Invite",
                value=f"**Activé:** {'✅' if antiinvite['enabled'] else '❌'}\n**Action:** {antiinvite['action']}",
                inline=True
            )
            
            embed.add_field(
                name="🔧 Commandes disponibles",
                value="`+antilink <on/off>`\n`+antilink_action <delete/warn/kick>`\n`+antiinvite <on/off>`\n`+antiinvite_action <delete/warn/kick>`\n`+antilink_whitelist add/remove <lien>`",
                inline=False
            )
            
            await interaction.response.edit_message(embed=embed, view=self)

        async def show_welcome_config(self, interaction, config):
            """Afficher la configuration de bienvenue"""
            embed = nextcord.Embed(
                title="🎉 Configuration - Bienvenue",
                description="Paramètres des messages de bienvenue",
                color=0x2ECC71
            )
            
            welcome = config["welcome"]
            goodbye = config["goodbye"]
            
            welcome_status = "✅" if welcome["enabled"] else "❌"
            goodbye_status = "✅" if goodbye["enabled"] else "❌"
            
            welcome_channel = f"<#{welcome['channel_id']}>" if welcome['channel_id'] else "Non configuré"
            welcome_message = welcome['message'][:50] + ('...' if len(welcome['message']) > 50 else '')
            
            embed.add_field(
                name="👋 Messages de bienvenue",
                value=f"**Activé:** {welcome_status}\n**Salon:** {welcome_channel}\n**Message:** {welcome_message}",
                inline=True
            )
            
            goodbye_channel = f"<#{goodbye['channel_id']}>" if goodbye['channel_id'] else "Non configuré"
            goodbye_message = goodbye['message'][:50] + ('...' if len(goodbye['message']) > 50 else '')
            
            embed.add_field(
                name="👋 Messages d'au revoir",
                value=f"**Activé:** {goodbye_status}\n**Salon:** {goodbye_channel}\n**Message:** {goodbye_message}",
                inline=True
            )
            
            embed.add_field(
                name="🔧 Commandes disponibles",
                value="`+welcome <on/off>`\n`+welcome_channel #salon`\n`+welcome_message <message>`\n`+goodbye <on/off>`\n`+goodbye_channel #salon`\n`+goodbye_message <message>`\n`+welcome_role @role`\n`+welcome_dm <on/off>`",
                inline=False
            )
            
            await interaction.response.edit_message(embed=embed, view=self)

        async def show_logs_config(self, interaction, config):
            """Afficher la configuration des logs"""
            embed = nextcord.Embed(
                title="📊 Configuration - Logs",
                description="Paramètres des logs de serveur",
                color=0x9B59B6
            )
            
            logs = config["logs"]
            
            logs_channel = f"<#{logs['channel_id']}>" if logs['channel_id'] else "Non configuré"
            
            embed.add_field(
                name="📊 Logs activés",
                value=f"**Activé:** {'✅' if logs['enabled'] else '❌'}\n**Salon:** {logs_channel}",
                inline=True
            )
            
            events_str = ", ".join([f"`{event}`" for event in logs["events"]])
            embed.add_field(
                name="📋 Événements enregistrés",
                value=events_str,
                inline=True
            )
            
            embed.add_field(
                name="🔧 Commandes disponibles",
                value="`+logs <on/off>`\n`+logs_channel #salon`\n`+logs_event add/remove <event>`\n`+logs_events list`",
                inline=False
            )
            
            await interaction.response.edit_message(embed=embed, view=self)

        async def show_autoroles_config(self, interaction, config):
            """Afficher la configuration des auto-rôles"""
            embed = nextcord.Embed(
                title="🎭 Configuration - Auto-Rôles",
                description="Paramètres des rôles automatiques",
                color=0xF39C12
            )
            
            autoroles = config["auto_roles"]
            
            embed.add_field(
                name="🎭 Auto-Rôles",
                value=f"**Activé:** {'✅' if autoroles['enabled'] else '❌'}\n**Nombre de rôles:** {len(autoroles['roles'])}",
                inline=True
            )
            
            if autoroles["roles"]:
                roles_str = "\n".join([f"• <@&{role_id}>" for role_id in autoroles["roles"][:5]])
                if len(autoroles["roles"]) > 5:
                    roles_str += f"\n... et {len(autoroles['roles']) - 5} autres"
                embed.add_field(
                    name="📋 Rôles configurés",
                    value=roles_str,
                    inline=True
                )
            
            embed.add_field(
                name="🔧 Commandes disponibles",
                value="`+autoroles <on/off>`\n`+autorole add @role`\n`+autorole remove @role`\n`+autoroles list`",
                inline=False
            )
            
            await interaction.response.edit_message(embed=embed, view=self)

        async def show_tickets_config(self, interaction, config):
            """Afficher la configuration des tickets"""
            embed = nextcord.Embed(
                title="🎫 Configuration - Tickets",
                description="Paramètres du système de tickets",
                color=0xE67E22
            )
            
            tickets = config["tickets"]
            
            tickets_category = f"<#{tickets['category_id']}>" if tickets['category_id'] else "Non configurée"
            tickets_support = f"<@&{tickets['support_role_id']}>" if tickets['support_role_id'] else "Non configuré"
            tickets_transcript = f"<#{tickets['transcript_channel_id']}>" if tickets['transcript_channel_id'] else "Non configuré"
            
            embed.add_field(
                name="🎫 Tickets",
                value=f"**Activé:** {'✅' if tickets['enabled'] else '❌'}\n**Catégorie:** {tickets_category}\n**Rôle support:** {tickets_support}",
                inline=True
            )
            
            embed.add_field(
                name="📄 Transcriptions",
                value=f"**Salon:** {tickets_transcript}",
                inline=True
            )
            
            embed.add_field(
                name="🔧 Commandes disponibles",
                value="`+tickets <on/off>`\n`+tickets_category #catégorie`\n`+tickets_role @role`\n`+tickets_transcript #salon`",
                inline=False
            )
            
            await interaction.response.edit_message(embed=embed, view=self)

        async def show_level_config(self, interaction, config):
            """Afficher la configuration des niveaux"""
            embed = nextcord.Embed(
                title="📈 Configuration - Niveaux",
                description="Paramètres du système de niveaux",
                color=0x2ECC71
            )
            
            level = config["level"]
            
            level_channel = f"<#{level['channel_id']}>" if level['channel_id'] else "Non configuré"
            
            embed.add_field(
                name="📈 Système de niveaux",
                value=f"**Activé:** {'✅' if level['enabled'] else '❌'}\n**Salon:** {level_channel}",
                inline=True
            )
            
            if level["role_rewards"]:
                rewards_str = "\n".join([f"• Niveau {lvl}: <@&{role_id}>" for lvl, role_id in list(level["role_rewards"].items())[:5]])
                if len(level["role_rewards"]) > 5:
                    rewards_str += f"\n... et {len(level['role_rewards']) - 5} autres"
                embed.add_field(
                    name="🎁 Récompenses de rôles",
                    value=rewards_str,
                    inline=True
                )
            
            embed.add_field(
                name="🔧 Commandes disponibles",
                value="`+level <on/off>`\n`+level_channel #salon`\n`+level_message <message>`\n`+level_reward <niveau> @role`\n`+level_rewards list`",
                inline=False
            )
            
            await interaction.response.edit_message(embed=embed, view=self)

        async def show_antispam_config(self, interaction, config):
            """Afficher la configuration anti-spam"""
            embed = nextcord.Embed(
                title="🚫 Configuration - Anti-Spam",
                description="Paramètres de protection contre le spam",
                color=0xE74C3C
            )
            
            antispam = config["antispam"]
            caps = config["caps"]
            swear = config["swear"]
            
            embed.add_field(
                name="🚫 Anti-Spam",
                value=f"**Activé:** {'✅' if antispam['enabled'] else '❌'}\n**Max messages:** {antispam['max_messages']}/{antispam['time_window']}s\n**Action:** {antispam['action']}",
                inline=True
            )
            
            embed.add_field(
                name="🔤 Anti-Caps",
                value=f"**Activé:** {'✅' if caps['enabled'] else '❌'}\n**Max caps:** {caps['max_caps']}\n**Action:** {caps['action']}",
                inline=True
            )
            
            embed.add_field(
                name="🤬 Anti-Insultes",
                value=f"**Activé:** {'✅' if swear['enabled'] else '❌'}\n**Mots:** {len(swear['words'])} configurés\n**Action:** {swear['action']}",
                inline=True
            )
            
            embed.add_field(
                name="🔧 Commandes disponibles",
                value="`+antispam <on/off>`\n`+antispam_limit <nombre> <secondes>`\n`+antispam_action <mute/kick/warn>`\n`+caps <on/off>`\n`+caps_limit <nombre>`\n`+swear <on/off>`\n`+swear_add <mot>`\n`+swear_remove <mot>`",
                inline=False
            )
            
            await interaction.response.edit_message(embed=embed, view=self)

    @commands.command(name="config")
    @commands.check(has_admin_permission)
    async def config_menu(self, ctx):
        """Menu interactif de configuration du serveur"""
        
        # Créer la vue de configuration
        view = self.ConfigView(self.bot, ctx.author, ctx.guild.id)
        
        # Créer l'embed principal
        embed = nextcord.Embed(
            title="⚙️ Configuration du Serveur",
            description="**Menu interactif pour configurer ton serveur**\n\n👇 **Choisis une catégorie ci-dessous**",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        
        # Statistiques
        config = self.load_config(ctx.guild.id)
        enabled_count = sum(1 for key, value in config.items() if isinstance(value, dict) and value.get("enabled", False))
        
        embed.add_field(
            name="📊 Statistiques",
            value=f"**Modules activés:** {enabled_count}/11\n**Total de modules:** 11",
            inline=False
        )
        
        embed.add_field(
            name="🎯 Comment utiliser",
            value="1. **Sélectionne une catégorie** dans le menu déroulant\n2. **Configure** les paramètres avec les commandes\n3. **Sauvegarde** automatique",
            inline=False
        )
        
        embed.set_footer(text=f"Demandé par {ctx.author.name} • Utilise +help config pour voir toutes les commandes")
        
        # Configurer le sélecteur
        view.config_select.options = [
            nextcord.SelectOption(
                label="🛡️ Modération",
                description="Configuration des seuils et actions automatiques",
                emoji="🛡️"
            ),
            nextcord.SelectOption(
                label="🔗 Anti-Link",
                description="Protection contre les liens et invitations",
                emoji="🔗"
            ),
            nextcord.SelectOption(
                label="🎉 Bienvenue",
                description="Messages de bienvenue et d'au revoir",
                emoji="🎉"
            ),
            nextcord.SelectOption(
                label="📊 Logs",
                description="Configuration des logs de serveur",
                emoji="📊"
            ),
            nextcord.SelectOption(
                label="🎭 Auto-Rôles",
                description="Rôles automatiques pour les nouveaux membres",
                emoji="🎭"
            ),
            nextcord.SelectOption(
                label="🎫 Tickets",
                description="Système de support par tickets",
                emoji="🎫"
            ),
            nextcord.SelectOption(
                label="📈 Niveaux",
                description="Système de niveaux et récompenses",
                emoji="📈"
            ),
            nextcord.SelectOption(
                label="🚫 Anti-Spam",
                description="Protection contre le spam, caps et insultes",
                emoji="🚫"
            )
        ]
        
        # Envoyer le message
        view.message = await ctx.send(embed=embed, view=view)

    # ===== COMMANDES DE CONFIGURATION =====

    # Anti-Link
    @commands.command(name="antilink")
    @commands.check(has_admin_permission)
    async def antilink_command(self, ctx, state: str):
        """Activer/désactiver l'anti-link"""
        config = self.load_config(ctx.guild.id)
        
        if state.lower() in ["on", "true", "1"]:
            config["antilink"]["enabled"] = True
            await ctx.send("✅ Anti-link activé")
        elif state.lower() in ["off", "false", "0"]:
            config["antilink"]["enabled"] = False
            await ctx.send("❌ Anti-link désactivé")
        else:
            await ctx.send("❌ Utilisation: `+antilink <on/off>`")
            return
            
        self.save_config(ctx.guild.id, config)

    @commands.command(name="antiinvite")
    @commands.check(has_admin_permission)
    async def antiinvite_command(self, ctx, state: str):
        """Activer/désactiver l'anti-invite"""
        config = self.load_config(ctx.guild.id)
        
        if state.lower() in ["on", "true", "1"]:
            config["antiinvite"]["enabled"] = True
            await ctx.send("✅ Anti-invite activé")
        elif state.lower() in ["off", "false", "0"]:
            config["antiinvite"]["enabled"] = False
            await ctx.send("❌ Anti-invite désactivé")
        else:
            await ctx.send("❌ Utilisation: `+antiinvite <on/off>`")
            return
            
        self.save_config(ctx.guild.id, config)

    # Welcome/Goodbye
    @commands.command(name="welcome")
    @commands.check(has_admin_permission)
    async def welcome_command(self, ctx, state: str):
        """Activer/désactiver les messages de bienvenue"""
        config = self.load_config(ctx.guild.id)
        
        if state.lower() in ["on", "true", "1"]:
            config["welcome"]["enabled"] = True
            await ctx.send("✅ Messages de bienvenue activés")
        elif state.lower() in ["off", "false", "0"]:
            config["welcome"]["enabled"] = False
            await ctx.send("❌ Messages de bienvenue désactivés")
        else:
            await ctx.send("❌ Utilisation: `+welcome <on/off>`")
            return
            
        self.save_config(ctx.guild.id, config)

    @commands.command(name="welcome_channel")
    @commands.check(has_admin_permission)
    async def welcome_channel_command(self, ctx, channel: nextcord.TextChannel):
        """Définir le salon de bienvenue"""
        config = self.load_config(ctx.guild.id)
        config["welcome"]["channel_id"] = channel.id
        self.save_config(ctx.guild.id, config)
        await ctx.send(f"✅ Salon de bienvenue défini sur {channel.mention}")

    @commands.command(name="welcome_message")
    @commands.check(has_admin_permission)
    async def welcome_message_command(self, ctx, *, message: str):
        """Définir le message de bienvenue"""
        config = self.load_config(ctx.guild.id)
        config["welcome"]["message"] = message
        self.save_config(ctx.guild.id, config)
        await ctx.send("✅ Message de bienvenue mis à jour")

    @commands.command(name="goodbye")
    @commands.check(has_admin_permission)
    async def goodbye_command(self, ctx, state: str):
        """Activer/désactiver les messages d'au revoir"""
        config = self.load_config(ctx.guild.id)
        
        if state.lower() in ["on", "true", "1"]:
            config["goodbye"]["enabled"] = True
            await ctx.send("✅ Messages d'au revoir activés")
        elif state.lower() in ["off", "false", "0"]:
            config["goodbye"]["enabled"] = False
            await ctx.send("❌ Messages d'au revoir désactivés")
        else:
            await ctx.send("❌ Utilisation: `+goodbye <on/off>`")
            return
            
        self.save_config(ctx.guild.id, config)

    @commands.command(name="goodbye_channel")
    @commands.check(has_admin_permission)
    async def goodbye_channel_command(self, ctx, channel: nextcord.TextChannel):
        """Définir le salon d'au revoir"""
        config = self.load_config(ctx.guild.id)
        config["goodbye"]["channel_id"] = channel.id
        self.save_config(ctx.guild.id, config)
        await ctx.send(f"✅ Salon d'au revoir défini sur {channel.mention}")

    @commands.command(name="goodbye_message")
    @commands.check(has_admin_permission)
    async def goodbye_message_command(self, ctx, *, message: str):
        """Définir le message d'au revoir"""
        config = self.load_config(ctx.guild.id)
        config["goodbye"]["message"] = message
        self.save_config(ctx.guild.id, config)
        await ctx.send("✅ Message d'au revoir mis à jour")

    # Auto-Roles
    @commands.command(name="autoroles")
    @commands.check(has_admin_permission)
    async def autoroles_command(self, ctx, state: str):
        """Activer/désactiver les auto-rôles"""
        config = self.load_config(ctx.guild.id)
        
        if state.lower() in ["on", "true", "1"]:
            config["auto_roles"]["enabled"] = True
            await ctx.send("✅ Auto-rôles activés")
        elif state.lower() in ["off", "false", "0"]:
            config["auto_roles"]["enabled"] = False
            await ctx.send("❌ Auto-rôles désactivés")
        else:
            await ctx.send("❌ Utilisation: `+autoroles <on/off>`")
            return
            
        self.save_config(ctx.guild.id, config)

    @commands.command(name="autorole")
    @commands.check(has_admin_permission)
    async def autorole_command(self, ctx, action: str, role: nextcord.Role = None):
        """Ajouter/supprimer un auto-rôle"""
        config = self.load_config(ctx.guild.id)
        
        if action.lower() == "add":
            if not role:
                await ctx.send("❌ Utilisation: `+autorole add @role`")
                return
            if role.id not in config["auto_roles"]["roles"]:
                config["auto_roles"]["roles"].append(role.id)
                await ctx.send(f"✅ Rôle {role.mention} ajouté aux auto-rôles")
            else:
                await ctx.send("❌ Ce rôle est déjà dans les auto-rôles")
                
        elif action.lower() == "remove":
            if not role:
                await ctx.send("❌ Utilisation: `+autorole remove @role`")
                return
            if role.id in config["auto_roles"]["roles"]:
                config["auto_roles"]["roles"].remove(role.id)
                await ctx.send(f"✅ Rôle {role.mention} retiré des auto-rôles")
            else:
                await ctx.send("❌ Ce rôle n'est pas dans les auto-rôles")
        else:
            await ctx.send("❌ Utilisation: `+autorole <add/remove> @role`")
            return
            
        self.save_config(ctx.guild.id, config)

    # Logs
    @commands.command(name="logs")
    @commands.check(has_admin_permission)
    async def logs_command(self, ctx, state: str):
        """Activer/désactiver les logs"""
        config = self.load_config(ctx.guild.id)
        
        if state.lower() in ["on", "true", "1"]:
            config["logs"]["enabled"] = True
            await ctx.send("✅ Logs activés")
        elif state.lower() in ["off", "false", "0"]:
            config["logs"]["enabled"] = False
            await ctx.send("❌ Logs désactivés")
        else:
            await ctx.send("❌ Utilisation: `+logs <on/off>`")
            return
            
        self.save_config(ctx.guild.id, config)

    @commands.command(name="logs_channel")
    @commands.check(has_admin_permission)
    async def logs_channel_command(self, ctx, channel: nextcord.TextChannel):
        """Définir le salon de logs"""
        config = self.load_config(ctx.guild.id)
        config["logs"]["channel_id"] = channel.id
        self.save_config(ctx.guild.id, config)
        await ctx.send(f"✅ Salon de logs défini sur {channel.mention}")

def setup(bot):
    bot.add_cog(ServerConfig(bot))
