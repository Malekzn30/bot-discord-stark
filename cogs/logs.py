import nextcord
from nextcord.ext import commands
from datetime import datetime, timedelta
import os
import json
import asyncio
import logging
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# ============================================================
# SYSTÈME DE LOGS UNIFIÉ
# ============================================================

# Créer le dossier logs s'il n'existe pas
LOGS_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

# Configuration du logging
def setup_logging():
    """Configurer le système de logs"""
    
    # Nom du fichier avec la date du jour
    log_filename = f"bot_{datetime.now().strftime('%Y%m%d')}.log"
    log_filepath = os.path.join(LOGS_DIR, log_filename)
    
    # Configuration du logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filepath, encoding='utf-8'),
            logging.StreamHandler()  # Aussi dans la console
        ]
    )
    
    # Créer un logger spécifique pour le bot
    logger = logging.getLogger('BotStark')
    
    return logger

# Fonction pour logger les événements de bienvenue
def log_welcome(member, action, details=""):
    """Logger les événements de bienvenue"""
    logger = logging.getLogger('BotStark')
    
    if action == "join":
        logger.info(f"JOIN - {member.name} (ID: {member.id}) a rejoint {member.guild.name}")
        # Envoyer aussi un embed dans le channel de logs join si configuré
        try:
            import asyncio
            from utils.embeds import create_embed
            
            # Créer un embed pour le join
            embed = create_embed("🎉 Nouveau Membre", f"{member.mention} a rejoint le serveur !", member.guild, None)
            embed.add_field(name="👤 Membre", value=f"{member} (ID: {member.id})", inline=False)
            embed.add_field(name="📅 Compte créé", value=member.created_at.strftime("%d/%m/%Y"), inline=False)
            embed.set_thumbnail(url=member.display_avatar.url)
            
            # Envoyer de manière asynchrone
            asyncio.create_task(send_log_async(member, embed))
        except Exception as e:
            logger.error(f"Erreur envoi log join: {e}")
            
    elif action == "member_count":
        logger.info(f"COUNT - Total membres: {details} | Membres humains: {details}")
    elif action == "public_sent":
        logger.info(f"WELCOME_PUBLIC - Message envoyé dans {details}")
    elif action == "public_error":
        logger.error(f"WELCOME_PUBLIC_ERROR - {details}")
    elif action == "dm_attempt":
        logger.info(f"WELCOME_DM - Tentative DM à {member.name}")
    elif action == "dm_sent":
        logger.info(f"WELCOME_DM - DM envoyé à {member.name}")
    elif action == "dm_blocked":
        logger.warning(f"WELCOME_DM_BLOCKED - DM bloqué pour {member.name} - {details}")
    elif action == "dm_error":
        logger.error(f"WELCOME_DM_ERROR - {member.name} - {details}")
    elif action == "invite_created":
        logger.info(f"INVITE - Lien créé: {details}")

async def send_log_async(member, embed):
    """Fonction asynchrone pour envoyer le log de join"""
    try:
        # Importer ici pour éviter les imports circulaires
        from cogs.logs import send_log
        
        await send_log(
            member.guild.me,  # bot
            "join",
            "NOUVEAU MEMBRE",
            {
                "Membre": f"{member} (ID: {member.id})",
                "Serveur": member.guild.name,
                "Compte créé": member.created_at.strftime("%d/%m/%Y"),
                "Rejoint le": member.joined_at.strftime("%d/%m/%Y")
            }
        )
    except Exception as e:
        print(f"Erreur send_log_async: {e}")

# Fonction pour logger les commandes
def log_command(ctx, command_name, details=""):
    """Logger les commandes utilisées"""
    logger = logging.getLogger('BotStark')
    
    logger.info(f"COMMAND - {ctx.author.name} a utilisé +{command_name} dans #{ctx.channel.name} - {details}")

# Fonction pour logger les erreurs
def log_error(error_type, details):
    """Logger les erreurs"""
    logger = logging.getLogger('BotStark')
    
    logger.error(f"ERROR - {error_type} - {details}")

# Fonction pour logger les événements vocaux
def log_voice(action, details=""):
    """Logger les événements vocaux"""
    logger = logging.getLogger('BotStark')
    
    logger.info(f"VOICE - {action} - {details}")

# Fonction pour logger les événements de modération
def log_moderation(action, moderator, target, reason=""):
    """Logger les événements de modération"""
    logger = logging.getLogger('BotStark')
    
    if reason:
        logger.info(f"MOD - {moderator} a {action} {target} - Raison: {reason}")
    else:
        logger.info(f"MOD - {moderator} a {action} {target}")

# Fonction pour logger les événements système
def log_system(action, details=""):
    """Logger les événements système"""
    logger = logging.getLogger('BotStark')
    
    logger.info(f"SYSTEM - {action} - {details}")

# Fonction pour logger les événements de jeux
def log_game(game_name, player, result=""):
    """Logger les événements de jeux"""
    logger = logging.getLogger('BotStark')
    
    if result:
        logger.info(f"GAME - {player} a joué à {game_name} - Résultat: {result}")
    else:
        logger.info(f"GAME - {player} a lancé {game_name}")

# ============================================================
# CONFIGURATION JSON PERSISTANTE
# ============================================================

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "logs_config.json")

LOG_CATEGORIES = [
    "warn",
    "commands",
    "moderation",
    "voice",
    "messages",
    "security",
    "admin",
    "server",
    "roles",
    "nicknames",
    "automod",
    "system",
    "join"
]

DEFAULT_LOG_CHANNELS = {cat: None for cat in LOG_CATEGORIES}

def load_config():
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w") as f:
            json.dump(DEFAULT_LOG_CHANNELS, f, indent=4)
        return DEFAULT_LOG_CHANNELS

    try:
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"❌ Erreur load_config: {e}")
        return DEFAULT_LOG_CHANNELS

def save_config(config):
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"❌ Erreur save_config: {e}")

LOG_CHANNELS = load_config()

# ============================================================
# FONCTION DE LOG ULTRA DÉTAILLÉE (NIVEAU PREMIUM)
# ============================================================

CATEGORY_ICONS = {
    "warn": "⚠️",
    "commands": "📘",
    "moderation": "🛡️",
    "voice": "🎙️",
    "messages": "💬",
    "security": "🔒",
    "admin": "⚙️",
    "server": "🌐",
    "roles": "🏷️",
    "nicknames": "📝",
    "automod": "🤖",
    "system": "📊",
    "join": "🎉"
}

CATEGORY_COLORS = {
    "warn": 0xFFAA00,
    "commands": 0x3498db,
    "moderation": 0xE74C3C,
    "voice": 0x9B59B6,
    "messages": 0x2ECC71,
    "security": 0xC0392B,
    "admin": 0x95A5A6,
    "server": 0x1ABC9C,
    "roles": 0xF1C40F,
    "nicknames": 0xE67E22,
    "automod": 0x8E44AD,
    "system": 0x34495E,
    "join": 0x2ECC71
}

async def send_log(bot, category: str, title: str, fields: dict, ctx=None, audit_id=None):
    """
    Envoie un log ultra détaillé dans la catégorie choisie.
    fields = { "Auteur": "...", "Cible": "...", "Salon": "...", etc. }
    """

    channel_id = LOG_CHANNELS.get(category)
    if not channel_id:
        print(f"⚠️ Aucun canal configuré pour la catégorie '{category}'")
        return

    channel = bot.get_channel(channel_id)
    if not channel:
        print(f"❌ Canal {channel_id} introuvable pour '{category}'")
        return

    icon = CATEGORY_ICONS.get(category, "📄")
    color = CATEGORY_COLORS.get(category, 0x3498db)

    embed = nextcord.Embed(
        title=f"{icon} {title}",
        color=color,
        timestamp=datetime.utcnow()
    )

    # Ajout des champs détaillés
    for name, value in fields.items():
        embed.add_field(name=name, value=str(value), inline=False)

    # Ajout de l'Audit Log ID si disponible
    if audit_id:
        embed.add_field(name="🔍 Audit ID", value=str(audit_id), inline=False)

    embed.set_footer(text=f"Catégorie : {category}")

    try:
        await channel.send(embed=embed)
    except Exception as e:
        print(f"❌ Erreur envoi log: {e}")

# ============================================================
# AUDIT LOG HELPER (RÉCUPÈRE L'AUTEUR RÉEL DE L'ACTION)
# ============================================================

async def get_audit_entry(guild, action_type, target_id):
    """
    Récupère l'entrée d'audit log correspondant à une action.
    action_type = nextcord.AuditLogAction.<ACTION>
    target_id = ID de la cible
    """

    await asyncio.sleep(0.5)

    try:
        async for entry in guild.audit_logs(limit=5, action=action_type):
            if entry.target and entry.target.id == target_id:
                return entry
    except Exception as e:
        print(f"❌ Erreur get_audit_entry: {e}")

    return None

# ============================================================
# LOGS MODÉRATION — TIMEOUT / KICK / BAN / ROLES / NICKNAMES
# ============================================================

class LogsModeration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # TIMEOUT / UNTIMEOUT (détecté automatiquement)
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.timeout == after.timeout:
            return

        if after.timeout:
            # TIMEOUT APPLIQUÉ
            entry = await get_audit_entry(after.guild, nextcord.AuditLogAction.member_update, after.id)
            await send_log(
                self.bot,
                "timeout",
                "TIMEOUT APPLIQUÉ",
                {
                    "Membre": f"{after} (ID: {after.id})",
                    "Durée": str(after.timeout_until - datetime.utcnow()) if after.timeout_until else "Indéfini",
                    "Modérateur": entry.user if entry else "Inconnu"
                },
                audit_id=entry.id if entry else None
            )
        else:
            # TIMEOUT RETIRÉ
            entry = await get_audit_entry(after.guild, nextcord.AuditLogAction.member_update, after.id)
            await send_log(
                self.bot,
                "moderation",
                "TIMEOUT RETIRÉ",
                {
                    "Membre": f"{after} (ID: {after.id})",
                    "Modérateur": entry.user if entry else "Inconnu"
                },
                audit_id=entry.id if entry else None
            )

    # KICK
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await asyncio.sleep(0.5)
        entry = await get_audit_entry(member.guild, nextcord.AuditLogAction.kick, member.id)
        if entry and entry.action == nextcord.AuditLogAction.kick:
            await send_log(
                self.bot,
                "moderation",
                "MEMBRE KICKÉ",
                {
                    "Membre": f"{member} (ID: {member.id})",
                    "Modérateur": entry.user,
                    "Raison": entry.reason or "Non spécifiée"
                },
                audit_id=entry.id
            )

    # BAN
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        entry = await get_audit_entry(guild, nextcord.AuditLogAction.ban, user.id)
        await send_log(
            self.bot,
            "moderation",
            "MEMBRE BANNI",
            {
                "Utilisateur": f"{user} (ID: {user.id})",
                "Modérateur": entry.user if entry else "Inconnu",
                "Raison": entry.reason if entry else "Non spécifiée"
            },
            audit_id=entry.id if entry else None
        )

    # UNBAN
    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        entry = await get_audit_entry(guild, nextcord.AuditLogAction.unban, user.id)
        await send_log(
            self.bot,
            "moderation",
            "MEMBRE DÉBANNI",
            {
                "Utilisateur": f"{user} (ID: {user.id})",
                "Modérateur": entry.user if entry else "Inconnu"
            },
            audit_id=entry.id if entry else None
        )

# ============================================================
# LOGS VOCAUX — MUTE / UNMUTE / MOVE / JOIN / LEAVE
# ============================================================

class LogsVoice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel != after.channel:
            if after.channel is None:
                await send_log(
                    self.bot,
                    "voice",
                    "MEMBRE A QUITTÉ LE VOCAL",
                    {
                        "Membre": f"{member} (ID: {member.id})",
                        "Salon": before.channel.name if before.channel else "Inconnu",
                        "Durée": "Voir logs Discord"
                    }
                )
            else:
                await send_log(
                    self.bot,
                    "voice",
                    "MEMBRE A REJOINT LE VOCAL",
                    {
                        "Membre": f"{member} (ID: {member.id})",
                        "Salon": after.channel.name
                    }
                )

# ============================================================
# LOGS MESSAGES — DELETE / EDIT (ULTRA PREMIUM)
# ============================================================

class LogsMessages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # MESSAGE SUPPRIMÉ
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return

        await send_log(
            self.bot,
            "messages",
            "MESSAGE SUPPRIMÉ",
            {
                "Auteur": f"{message.author} (ID: {message.author.id})",
                "Salon": f"{message.channel.mention}",
                "Contenu": message.content[:1024] or "(vide)",
                "Lien": f"[Voir le message](https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id})"
            }
        )

    # MESSAGE ÉDITÉ
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content:
            return

        await send_log(
            self.bot,
            "messages",
            "MESSAGE ÉDITÉ",
            {
                "Auteur": f"{before.author} (ID: {before.author.id})",
                "Salon": f"{before.channel.mention}",
                "Avant": before.content[:512] or "(vide)",
                "Après": after.content[:512] or "(vide)"
            }
        )

# ============================================================
# COMMANDES DE CONFIGURATION DES LOGS
# ============================================================

class LogsConfig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="logs_setup")
    @commands.has_permissions(administrator=True)
    async def logs_setup_interactive(self, ctx):
        """Configuration interactive des logs avec boutons et menu déroulant"""
        
        # Créer l'embed principal
        embed = nextcord.Embed(
            title="🔧 Configuration des Logs",
            description="Configure facilement les logs avec ce menu interactif !",
            color=0x3498db
        )
        
        embed.add_field(
            name="📋 Catégories disponibles",
            value="⚠️ `warn` - Avertissements\n"
                  "📘 `commands` - Commandes utilisées\n"
                  "🛡️ `moderation` - Actions de modération\n"
                  "🎙️ `voice` - Activités vocales\n"
                  "💬 `messages` - Messages supprimés/édités\n"
                  "🔒 `security` - Événements de sécurité\n"
                  "⚙️ `admin` - Actions admin\n"
                  "🌐 `server` - Changements serveur\n"
                  "🏷️ `roles` - Modifications de rôles\n"
                  "📝 `nicknames` - Changements de pseudos\n"
                  "🤖 `automod` - Modération automatique\n"
                  "📊 `system` - Événements système\n"
                  "🎉 `join` - Nouveaux membres",
            inline=False
        )
        
        embed.add_field(
            name="🎯 Comment utiliser",
            value="1. Sélectionne une catégorie dans le menu\n"
                  "2. Choisis un channel avec les boutons\n"
                  "3. Confirme avec le bouton ✅\n"
                  "4. Les logs sont automatiquement sauvegardés !",
            inline=False
        )
        
        embed.set_footer(text="Made by 𝐒𝐭𝐚𝐫𝐊𝟗𝟐☆🇵🇸")
        
        # Créer le menu déroulant
        select = nextcord.ui.Select(
            placeholder="🔍 Choisis une catégorie de logs...",
            options=[
                nextcord.SelectOption(
                    label="⚠️ Warn",
                    description="Logs des avertissements",
                    emoji="⚠️",
                    value="warn"
                ),
                nextcord.SelectOption(
                    label="📘 Commands",
                    description="Logs des commandes utilisées",
                    emoji="�",
                    value="commands"
                ),
                nextcord.SelectOption(
                    label="🛡️ Moderation",
                    description="Logs de modération",
                    emoji="🛡️",
                    value="moderation"
                ),
                nextcord.SelectOption(
                    label="🎙️ Voice",
                    description="Logs des activités vocales",
                    emoji="🎙️",
                    value="voice"
                ),
                nextcord.SelectOption(
                    label="💬 Messages",
                    description="Logs des messages",
                    emoji="💬",
                    value="messages"
                ),
                nextcord.SelectOption(
                    label="🔒 Security",
                    description="Logs de sécurité",
                    emoji="🔒",
                    value="security"
                ),
                nextcord.SelectOption(
                    label="⚙️ Admin",
                    description="Logs admin",
                    emoji="⚙️",
                    value="admin"
                ),
                nextcord.SelectOption(
                    label="🌐 Server",
                    description="Logs serveur",
                    emoji="🌐",
                    value="server"
                ),
                nextcord.SelectOption(
                    label="🏷️ Roles",
                    description="Logs des rôles",
                    emoji="🏷️",
                    value="roles"
                ),
                nextcord.SelectOption(
                    label="📝 Nicknames",
                    description="Logs des pseudos",
                    emoji="📝",
                    value="nicknames"
                ),
                nextcord.SelectOption(
                    label="🤖 Automod",
                    description="Logs auto-modération",
                    emoji="🤖",
                    value="automod"
                ),
                nextcord.SelectOption(
                    label="📊 System",
                    description="Logs système",
                    emoji="📊",
                    value="system"
                ),
                nextcord.SelectOption(
                    label="🎉 Join",
                    description="Logs des arrivées",
                    emoji="🎉",
                    value="join"
                )
            ]
        )
        
        # Créer les vues pour les channels
        class LogsView(nextcord.ui.View):
            def __init__(self):
                super().__init__(timeout=180)  # 3 minutes
                self.selected_category = None
                self.selected_channel = None
                
            async def select_callback(self, interaction: nextcord.Interaction, select: nextcord.ui.Select):
                self.selected_category = select.values[0]
                
                # Mettre à jour l'embed pour montrer la sélection
                new_embed = interaction.message.embeds[0]
                new_embed.description = f"🔍 **Catégorie sélectionnée :** `{self.selected_category}`\n\nMaintenant choisis un channel ci-dessous :"
                
                # Activer les boutons de channels
                for child in self.children:
                    if isinstance(child, nextcord.ui.Button) and child.custom_id.startswith("channel_"):
                        child.disabled = False
                
                await interaction.response.edit_message(embed=new_embed, view=self)
            
            @nextcord.ui.button(label="#général", style=nextcord.ButtonStyle.secondary, custom_id="channel_general", disabled=True)
            async def general_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                channel = nextcord.utils.get(ctx.guild.text_channels, name="général")
                if channel:
                    self.selected_channel = channel
                    button.style = nextcord.ButtonStyle.success
                    button.disabled = True
                    # Désactiver les autres boutons
                    for child in self.children:
                        if isinstance(child, nextcord.ui.Button) and child.custom_id != button.custom_id:
                            child.disabled = True
                    await interaction.response.edit_message(view=self)
                else:
                    await interaction.response.send_message("❌ Channel #général introuvable", ephemeral=True)
            
            @nextcord.ui.button(label="#logs", style=nextcord.ButtonStyle.secondary, custom_id="channel_logs", disabled=True)
            async def logs_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                channel = nextcord.utils.get(ctx.guild.text_channels, name="logs")
                if channel:
                    self.selected_channel = channel
                    button.style = nextcord.ButtonStyle.success
                    button.disabled = True
                    # Désactiver les autres boutons
                    for child in self.children:
                        if isinstance(child, nextcord.ui.Button) and child.custom_id != button.custom_id:
                            child.disabled = True
                    await interaction.response.edit_message(view=self)
                else:
                    await interaction.response.send_message("❌ Channel #logs introuvable", ephemeral=True)
            
            @nextcord.ui.button(label="#modération", style=nextcord.ButtonStyle.secondary, custom_id="channel_moderation", disabled=True)
            async def moderation_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                channel = nextcord.utils.get(ctx.guild.text_channels, name="modération")
                if channel:
                    self.selected_channel = channel
                    button.style = nextcord.ButtonStyle.success
                    button.disabled = True
                    # Désactiver les autres boutons
                    for child in self.children:
                        if isinstance(child, nextcord.ui.Button) and child.custom_id != button.custom_id:
                            child.disabled = True
                    await interaction.response.edit_message(view=self)
                else:
                    await interaction.response.send_message("❌ Channel #modération introuvable", ephemeral=True)
            
            @nextcord.ui.button(label="✅ Confirmer", style=nextcord.ButtonStyle.success, custom_id="confirm", disabled=True)
            async def confirm_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                if self.selected_category and self.selected_channel:
                    # Sauvegarder la configuration
                    LOG_CHANNELS[self.selected_category] = self.selected_channel.id
                    save_config(LOG_CHANNELS)
                    
                    # Envoyer la confirmation
                    confirm_embed = nextcord.Embed(
                        title="✅ Configuration enregistrée !",
                        description=f"Les logs **{self.selected_category}** seront envoyés dans {self.selected_channel.mention}",
                        color=0x2ECC71
                    )
                    confirm_embed.add_field(
                        name="📊 Résumé",
                        value=f"📂 Catégorie : `{self.selected_category}`\n"
                              f"📝 Channel : {self.selected_channel.mention}\n"
                              f"💾 Sauvegardé : ✅",
                        inline=False
                    )
                    confirm_embed.set_footer(text="Utilise `+logs_status` pour voir toute ta configuration")
                    
                    await interaction.response.edit_message(embed=confirm_embed, view=None)
                else:
                    await interaction.response.send_message("❌ Veuillez sélectionner une catégorie et un channel", ephemeral=True)
            
            @nextcord.ui.button(label="❌ Annuler", style=nextcord.ButtonStyle.danger, custom_id="cancel")
            async def cancel_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                cancel_embed = nextcord.Embed(
                    title="❌ Configuration annulée",
                    description="La configuration a été annulée. Utilise `+logs_setup` pour recommencer.",
                    color=0xE74C3C
                )
                await interaction.response.edit_message(embed=cancel_embed, view=None)
        
        # Assigner le callback au select
        select.callback = lambda interaction: LogsView.select_callback(None, interaction, select)
        
        # Créer la vue et ajouter le select
        view = LogsView()
        view.add_item(select)
        
        await ctx.send(embed=embed, view=view)

    # ------------------------------------------------------------
    # /logs reset <catégorie>
    # ------------------------------------------------------------
    @commands.command(name="logs_reset")
    async def logs_reset(self, ctx, category: str):

        category = category.lower()

        if category not in LOG_CATEGORIES:
            valid = ", ".join(LOG_CATEGORIES)
            return await ctx.send(
                embed=nextcord.Embed(
                    title="❌ Catégorie invalide",
                    description=f"Catégories valides :\n```\n{valid}\n```",
                    color=0xE74C3C
                )
            )

        LOG_CHANNELS[category] = None
        save_config(LOG_CHANNELS)

        await ctx.send(
            embed=nextcord.Embed(
                title="♻️ Log réinitialisé",
                description=f"La catégorie **{category}** n’a plus de salon assigné.",
                color=0xF1C40F
            )
        )

    # ------------------------------------------------------------
    # /logs status
    # ------------------------------------------------------------
    @commands.command(name="logs_status")
    async def logs_status(self, ctx):

        embed = nextcord.Embed(
            title="📊 État des logs",
            description="Voici la configuration actuelle des logs :",
            color=0x3498db
        )

        for cat in LOG_CATEGORIES:
            channel_id = LOG_CHANNELS.get(cat)
            channel = ctx.guild.get_channel(channel_id) if channel_id else None

            embed.add_field(
                name=f"{CATEGORY_ICONS.get(cat, '📄')} {cat}",
                value=channel.mention if channel else "❌ Aucun salon",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name="logs_clear")
    @commands.has_permissions(administrator=True)
    async def logs_clear(self, ctx, category: str = None):
        if not category:
            return await ctx.send("❌ Utilise : `+logs_clear <catégorie>`")
        
        category = category.lower()
        if category not in LOG_CATEGORIES:
            return await ctx.send(f"❌ Catégorie invalide. Valides: {', '.join(LOG_CATEGORIES)}")
        
        LOG_CHANNELS[category] = None
        save_config(LOG_CHANNELS)
        await ctx.send(f"🗑️ Logs {category} effa cés.")

    @commands.command(name="logs_list_categories")
    async def logs_list_categories(self, ctx):
        desc = ""
        for cat in LOG_CATEGORIES:
            icon = CATEGORY_ICONS.get(cat, "📄")
            desc += f"{icon} `{cat}`\n"
        embed = nextcord.Embed(title="📋 Catégories de logs disponibles", description=desc, color=0x3498db)
        await ctx.send(embed=embed)
# ============================================================
# SETUP FINAL DU COG — ASSEMBLAGE COMPLET
# ============================================================

def setup(bot):
    bot.add_cog(LogsModeration(bot))
    bot.add_cog(LogsVoice(bot))
    bot.add_cog(LogsMessages(bot))
    bot.add_cog(LogsConfig(bot))
