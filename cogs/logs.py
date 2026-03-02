import nextcord
from nextcord.ext import commands
import datetime
import os
import json

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ensure_data_directory()

    def ensure_data_directory(self):
        """S'assurer que le répertoire data/logs existe"""
        os.makedirs("data/logs", exist_ok=True)

    @commands.command(name="logs")
    @commands.has_permissions(administrator=True)
    async def logs_command(self, ctx, log_type: str = "all"):
        """Afficher les logs du serveur"""
        
        log_file = f"data/logs/{ctx.guild.id}.json"
        
        if not os.path.exists(log_file):
            return await ctx.send("❌ Aucun log trouvé pour ce serveur.")
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except:
            logs = []
        
        if not logs:
            return await ctx.send("❌ Aucun log disponible.")
        
        # Filtrer par type si spécifié
        if log_type.lower() != "all":
            logs = [log for log in logs if log.get("type", "").lower() == log_type.lower()]
        
        if not logs:
            return await ctx.send(f"❌ Aucun log de type `{log_type}` trouvé.")
        
        # Afficher les 20 derniers logs
        recent_logs = logs[-20:]
        
        embed = nextcord.Embed(
            title="📋 Logs du Serveur",
            description=f"Type: {log_type if log_type != 'all' else 'Tous'}",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        
        for log in recent_logs:
            timestamp = log.get("timestamp", "")
            action = log.get("action", "Inconnu")
            user = log.get("user", "Inconnu")
            details = log.get("details", "")
            
            # Limiter la longueur pour l'affichage
            if len(details) > 100:
                details = details[:97] + "..."
            
            embed.add_field(
                name=f"📝 {action}",
                value=f"**Utilisateur:** {user}\n**Détails:** {details}\n**Temps:** {timestamp}",
                inline=False
            )
        
        embed.set_footer(text=f"Total: {len(recent_logs)} logs récents")
        await ctx.send(embed=embed)

    @commands.command(name="clearlogs")
    @commands.has_permissions(administrator=True)
    async def clear_logs_command(self, ctx, log_type: str = "all"):
        """Vider les logs du serveur"""
        
        log_file = f"data/logs/{ctx.guild.id}.json"
        
        if log_type.lower() == "all":
            if os.path.exists(log_file):
                os.remove(log_file)
                await ctx.send("✅ Tous les logs ont été supprimés.")
            else:
                await ctx.send("❌ Aucun log à supprimer.")
        else:
            # Supprimer seulement un type spécifique
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                
                original_count = len(logs)
                logs = [log for log in logs if log.get("type", "").lower() != log_type.lower()]
                
                with open(log_file, 'w', encoding='utf-8') as f:
                    json.dump(logs, f, indent=2, ensure_ascii=False)
                
                removed = original_count - len(logs)
                await ctx.send(f"✅ {removed} logs de type `{log_type}` supprimés.")
                
            except FileNotFoundError:
                await ctx.send("❌ Aucun log trouvé.")

    @commands.command(name="logsettings")
    @commands.has_permissions(administrator=True)
    async def log_settings(self, ctx, setting: str, value: str = None):
        """Configurer les paramètres des logs"""
        
        settings_file = "data/logs/settings.json"
        
        # Charger les paramètres actuels
        if os.path.exists(settings_file):
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
        else:
            settings = {
                "enabled": True,
                "log_types": ["moderation", "vocal", "messages", "errors"],
                "max_logs": 1000,
                "auto_cleanup": True
            }
        
        if value is None:
            # Afficher les paramètres actuels
            embed = nextcord.Embed(
                title="⚙️ Paramètres des Logs",
                color=0x3498db
            )
            
            for key, val in settings.items():
                if isinstance(val, list):
                    val = ", ".join(val)
                embed.add_field(name=key.title(), value=str(val), inline=True)
            
            await ctx.send(embed=embed)
            return
        
        # Modifier un paramètre
        if setting.lower() in ["enabled", "auto_cleanup"]:
            settings[setting.lower()] = value.lower() in ["true", "on", "1"]
        elif setting.lower() in ["max_logs"]:
            try:
                settings[setting.lower()] = int(value)
            except ValueError:
                return await ctx.send("❌ La valeur doit être un nombre.")
        elif setting.lower() == "log_types":
            types = [t.strip() for t in value.split(",")]
            settings[setting.lower()] = types
        else:
            return await ctx.send("❌ Paramètre inconnu.")
        
        # Sauvegarder les paramètres
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        
        await ctx.send(f"✅ Paramètre `{setting}` mis à jour: `{value}`")

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        """Logger les commandes utilisées"""
        await self.log_action(ctx.guild, "command", f"{ctx.author.mention} a utilisé `{ctx.command}`")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Logger les arrivées de membres"""
        await self.log_action(member.guild, "member_join", f"{member.mention} a rejoint le serveur")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Logger les départs de membres"""
        await self.log_action(member.guild, "member_leave", f"{member.mention} a quitté le serveur")

    async def log_action(self, guild, action_type, details):
        """Ajouter une action aux logs"""
        try:
            log_file = f"data/logs/{guild.id}.json"
            
            # Charger les logs existants
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            # Ajouter le nouveau log
            new_log = {
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "type": action_type,
                "action": action_type.replace("_", " ").title(),
                "details": details,
                "user": details.split()[0] if " " in details else "System"
            }
            
            logs.append(new_log)
            
            # Limiter le nombre de logs
            settings_file = "data/logs/settings.json"
            max_logs = 1000  # Valeur par défaut
            
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    max_logs = settings.get("max_logs", 1000)
            
            if len(logs) > max_logs:
                logs = logs[-max_logs:]
            
            # Sauvegarder
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"[LOGS ERROR] {e}")

def setup(bot):
    bot.add_cog(Logs(bot))
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
        
        # Récupérer le bot depuis le member
        bot = member.guild.me
        
        await send_log(
            bot,
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
        """Configuration interactive des logs avec menu sélecteur et configuration multiple"""
        
        # Créer l'embed principal
        embed = nextcord.Embed(
            title="🔧 Configuration des Logs",
            description="Configure facilement les logs avec ce menu interactif !\n\n**Étapes :**\n1. Sélectionne une catégorie dans le menu\n2. Envoie le salon (#salon) dans le chat\n3. Confirme avec ✅ ou ajoute une autre catégorie avec ➕",
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
        
        embed.set_footer(text="Made by 𝐒𝐭𝐚𝐫𝐊𝟗𝟐☆🇵🇸")
        
        # Créer le menu déroulant
        select = nextcord.ui.Select(
            placeholder="🔍 Choisis une catégorie de logs...",
            options=[
                nextcord.SelectOption(
                    label="Warn",
                    description="Logs des avertissements",
                    emoji="⚠️",
                    value="warn"
                ),
                nextcord.SelectOption(
                    label="Commands",
                    description="Logs des commandes utilisées",
                    emoji="📘",
                    value="commands"
                ),
                nextcord.SelectOption(
                    label="Moderation",
                    description="Logs de modération",
                    emoji="🛡️",
                    value="moderation"
                ),
                nextcord.SelectOption(
                    label="Voice",
                    description="Logs des activités vocales",
                    emoji="🎙️",
                    value="voice"
                ),
                nextcord.SelectOption(
                    label="Messages",
                    description="Logs des messages",
                    emoji="💬",
                    value="messages"
                ),
                nextcord.SelectOption(
                    label="Security",
                    description="Logs de sécurité",
                    emoji="🔒",
                    value="security"
                ),
                nextcord.SelectOption(
                    label="Admin",
                    description="Logs admin",
                    emoji="⚙️",
                    value="admin"
                ),
                nextcord.SelectOption(
                    label="Server",
                    description="Logs serveur",
                    emoji="🌐",
                    value="server"
                ),
                nextcord.SelectOption(
                    label="Roles",
                    description="Logs des rôles",
                    emoji="🏷️",
                    value="roles"
                ),
                nextcord.SelectOption(
                    label="Nicknames",
                    description="Logs des pseudos",
                    emoji="📝",
                    value="nicknames"
                ),
                nextcord.SelectOption(
                    label="Automod",
                    description="Logs auto-modération",
                    emoji="🤖",
                    value="automod"
                ),
                nextcord.SelectOption(
                    label="System",
                    description="Logs système",
                    emoji="📊",
                    value="system"
                ),
                nextcord.SelectOption(
                    label="Join",
                    description="Logs des arrivées",
                    emoji="🎉",
                    value="join"
                )
            ]
        )
        
        # Créer la vue pour la configuration
        class LogsSetupView(nextcord.ui.View):
            def __init__(self):
                super().__init__(timeout=300)  # 5 minutes
                self.selected_category = None
                self.configured_categories = []  # Liste des catégories configurées
                self.waiting_for_channel = False
                self.message = None
                
            async def select_callback(self, interaction: nextcord.Interaction, select: nextcord.ui.Select):
                self.selected_category = select.values[0]
                self.waiting_for_channel = True
                
                # Mettre à jour l'embed pour demander le salon
                new_embed = interaction.message.embeds[0]
                new_embed.description = f"🔍 **Catégorie sélectionnée :** `{self.selected_category}`\n\n**Envoie maintenant le salon (#salon) dans le chat**\n\n*Exemple : #logs*"
                
                await interaction.response.edit_message(embed=new_embed, view=self)
            
            @nextcord.ui.button(label="✅ Confirmer", style=nextcord.ButtonStyle.success, custom_id="confirm", disabled=True)
            async def confirm_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                # Sauvegarder toutes les configurations
                saved_count = 0
                for category, channel_id in self.configured_categories:
                    LOG_CHANNELS[category] = channel_id
                    saved_count += 1
                
                save_config(LOG_CHANNELS)
                
                # Envoyer la confirmation
                confirm_embed = nextcord.Embed(
                    title="✅ Configuration enregistrée !",
                    description=f"**{saved_count}** catégories de logs configurées avec succès !",
                    color=0x2ECC71
                )
                
                # Lister toutes les configurations
                for category, channel_id in self.configured_categories:
                    channel = ctx.guild.get_channel(channel_id)
                    if channel:
                        icon = CATEGORY_ICONS.get(category, "📄")
                        confirm_embed.add_field(
                            name=f"{icon} {category.title()}",
                            value=f"📝 {channel.mention}",
                            inline=True
                        )
                
                confirm_embed.set_footer(text="Utilise `+logs_status` pour voir toute ta configuration")
                
                await interaction.response.edit_message(embed=confirm_embed, view=None)
            
            @nextcord.ui.button(label="➕ Ajouter une autre", style=nextcord.ButtonStyle.secondary, custom_id="add_more", disabled=True)
            async def add_more_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                # Réinitialiser pour ajouter une autre catégorie
                self.selected_category = None
                self.waiting_for_channel = False
                button.disabled = True
                self.children[0].disabled = False  # Réactiver le select
                
                # Mettre à jour l'embed
                new_embed = interaction.message.embeds[0]
                new_embed.description = "🔧 **Ajoute une autre catégorie de logs !**\n\n1. Sélectionne une catégorie dans le menu\n2. Envoie le salon (#salon) dans le chat\n3. Confirme avec ✅ ou ajoute une autre catégorie avec ➕"
                
                await interaction.response.edit_message(embed=new_embed, view=self)
            
            @nextcord.ui.button(label="❌ Annuler", style=nextcord.ButtonStyle.danger, custom_id="cancel")
            async def cancel_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                cancel_embed = nextcord.Embed(
                    title="❌ Configuration annulée",
                    description="La configuration a été annulée. Utilise `+logs_setup` pour recommencer.",
                    color=0xE74C3C
                )
                await interaction.response.edit_message(embed=cancel_embed, view=None)
        
        # Assigner le callback au select
        view = LogsSetupView()
        select.callback = lambda interaction: view.select_callback(interaction, select)
        
        # Ajouter le select à la vue
        view.add_item(select)
        
        # Envoyer le message initial
        message = await ctx.send(embed=embed, view=view)
        view.message = message
        
        # Écouter les messages pour le salon
        def check_channel(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel and view.waiting_for_channel
        
        while not view.is_finished():
            try:
                msg = await ctx.bot.wait_for("message", timeout=300.0, check=check_channel)
                
                if view.waiting_for_channel and view.selected_category:
                    # Parser le salon depuis le message
                    if msg.channel_mentions:
                        channel = msg.channel_mentions[0]
                        
                        # Ajouter à la liste des configurations
                        view.configured_categories.append((view.selected_category, channel.id))
                        
                        # Mettre à jour l'embed
                        current_embed = view.message.embeds[0]
                        
                        # Ajouter la catégorie configurée à la description
                        icon = CATEGORY_ICONS.get(view.selected_category, "📄")
                        current_embed.description += f"\n✅ **{icon} {view.selected_category.title()}** → {channel.mention}"
                        
                        # Réinitialiser pour la prochaine sélection
                        view.selected_category = None
                        view.waiting_for_channel = False
                        
                        # Activer les boutons appropriés
                        view.children[0].disabled = False  # Réactiver le select
                        view.children[1].disabled = False  # Activer confirmer
                        view.children[2].disabled = False  # Activer ajouter une autre
                        
                        await view.message.edit(embed=current_embed, view=view)
                        
                        # Supprimer le message de l'utilisateur
                        await msg.delete()
                        
                    else:
                        await ctx.send("❌ Veuillez mentionner un salon valide (ex: #logs)", delete_after=5)
                        await msg.delete()
                        
            except asyncio.TimeoutError:
                if not view.is_finished():
                    timeout_embed = nextcord.Embed(
                        title="⏰ Temps écoulé",
                        description="La configuration a été annulée pour inactivité.",
                        color=0xE74C3C
                    )
                    await view.message.edit(embed=timeout_embed, view=None)
                break

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
