import nextcord
from nextcord.ext import commands
import aiohttp
import io
from utils.config_manager import config_manager

class BotCustomization(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="setname")
    @commands.has_permissions(administrator=True)
    async def set_name(self, ctx, *, name: str):
        """Changer le nom du bot"""
        if len(name) < 2 or len(name) > 32:
            return await ctx.send("❌ Le nom doit contenir entre 2 et 32 caractères.")
        
        try:
            await self.bot.user.edit(username=name)
            config_manager.set("bot.name", name)
            await ctx.send(f"✅ Nom du bot changé en **{name}**")
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="setprefix")
    @commands.has_permissions(administrator=True)
    async def set_prefix(self, ctx, prefix: str):
        """Changer le préfixe des commandes"""
        if len(prefix) != 1:
            return await ctx.send("❌ Le préfixe doit être un seul caractère.")
        
        config_manager.set("bot.prefix", prefix)
        await ctx.send(f"✅ Préfixe changé en **{prefix}**")
    
    @commands.command(name="setbio")
    @commands.has_permissions(administrator=True)
    async def set_bio(self, ctx, *, bio: str):
        """Changer la bio du bot"""
        if len(bio) > 500:
            return await ctx.send("❌ La bio ne peut pas dépasser 500 caractères.")
        
        config_manager.set("appearance.bio", bio)
        await ctx.send(f"✅ Bio changée en: **{bio}**")
    
    @commands.command(name="setavatar")
    @commands.has_permissions(administrator=True)
    async def set_avatar(self, ctx, url: str = None):
        """Changer l'avatar du bot"""
        if not url:
            # Si pas d'URL, vérifier si une pièce jointe
            if not ctx.message.attachments:
                return await ctx.send("❌ Veuillez fournir une URL ou joindre une image.")
            
            attachment = ctx.message.attachments[0]
            if not attachment.content_type.startswith('image/'):
                return await ctx.send("❌ Le fichier doit être une image.")
            
            image_bytes = await attachment.read()
        else:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status != 200:
                            return await ctx.send("❌ Impossible de télécharger l'image.")
                        image_bytes = await response.read()
            except:
                return await ctx.send("❌ URL invalide.")
        
        try:
            await self.bot.user.edit(avatar=io.BytesIO(image_bytes))
            config_manager.set("appearance.profile_picture", url)
            await ctx.send("✅ Avatar changé avec succès !")
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="setbanner")
    @commands.has_permissions(administrator=True)
    async def set_banner(self, ctx, url: str = None):
        """Changer la bannière du bot"""
        if not url:
            if not ctx.message.attachments:
                return await ctx.send("❌ Veuillez fournir une URL ou joindre une image.")
            
            attachment = ctx.message.attachments[0]
            if not attachment.content_type.startswith('image/'):
                return await ctx.send("❌ Le fichier doit être une image.")
            
            image_bytes = await attachment.read()
        else:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status != 200:
                            return await ctx.send("❌ Impossible de télécharger l'image.")
                        image_bytes = await response.read()
            except:
                return await ctx.send("❌ URL invalide.")
        
        try:
            await self.bot.user.edit(banner=io.BytesIO(image_bytes))
            config_manager.set("appearance.banner", url)
            await ctx.send("✅ Bannière changée avec succès !")
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="setstatus")
    @commands.has_permissions(administrator=True)
    async def set_status(self, ctx, status: str):
        """Changer le statut du bot"""
        valid_statuses = {"online": nextcord.Status.online, "idle": nextcord.Status.idle, 
                         "dnd": nextcord.Status.dnd, "invisible": nextcord.Status.invisible}
        
        if status.lower() not in valid_statuses:
            return await ctx.send("❌ Statuts valides: online, idle, dnd, invisible")
        
        await self.bot.change_presence(status=valid_statuses[status.lower()])
        config_manager.set("appearance.status", status.lower())
        await ctx.send(f"✅ Statut changé en **{status}**")
    
    @commands.command(name="setactivity")
    @commands.has_permissions(administrator=True)
    async def set_activity(self, ctx, activity_type: str, *, text: str):
        """Changer l'activité du bot"""
        valid_types = {"playing": nextcord.ActivityType.playing, 
                      "watching": nextcord.ActivityType.watching,
                      "listening": nextcord.ActivityType.listening,
                      "competing": nextcord.ActivityType.competing}
        
        if activity_type.lower() not in valid_types:
            return await ctx.send("❌ Types valides: playing, watching, listening, competing")
        
        activity = nextcord.Activity(type=valid_types[activity_type.lower()], name=text)
        await self.bot.change_presence(activity=activity)
        config_manager.set("appearance.activity_type", activity_type.lower())
        config_manager.set("appearance.activity_text", text)
        await ctx.send(f"✅ Activité changée en **{activity_type} {text}**")
    
    @commands.command(name="toggle")
    @commands.has_permissions(administrator=True)
    async def toggle_feature(self, ctx, feature: str):
        """Activer ou désactiver une fonctionnalité"""
        feature_map = {
            "moderation": "features.moderation.enabled",
            "automod": "features.moderation.auto_mod",
            "vocal": "features.vocal.enabled",
            "autobalance": "features.vocal.auto_balance",
            "social": "features.social.enabled",
            "livenotifications": "features.social.live_notifications",
            "games": "features.games.enabled",
            "dailyrewards": "features.games.daily_rewards",
            "leaderboards": "features.games.leaderboards"
        }
        
        if feature.lower() not in feature_map:
            return await ctx.send("❌ Fonctionnalité invalide. Utilise `+help toggle` pour voir la liste.")
        
        path = feature_map[feature.lower()]
        current_value = config_manager.get(path, False)
        new_value = not current_value
        
        config_manager.set(path, new_value)
        status = "activée" if new_value else "désactivée"
        await ctx.send(f"✅ Fonctionnalité **{feature}** {status}")
    
    @commands.command(name="setconfig")
    @commands.has_permissions(administrator=True)
    async def set_config(self, ctx, path: str, *, value: str):
        """Définir une configuration spécifique"""
        try:
            # Essayer de convertir en type approprié
            if value.lower() in ("true", "false"):
                value = value.lower() == "true"
            elif value.isdigit():
                value = int(value)
            elif value.replace(".", "").isdigit():
                value = float(value)
            
            config_manager.set(path, value)
            await ctx.send(f"✅ Configuration `{path}` définie sur `{value}`")
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="getconfig")
    @commands.has_permissions(administrator=True)
    async def get_config(self, ctx, path: str = None):
        """Afficher la configuration actuelle"""
        if path:
            value = config_manager.get(path)
            await ctx.send(f"📋 `{path}` = `{value}`")
        else:
            # Afficher la configuration principale
            embed = nextcord.Embed(
                title="⚙️ Configuration Actuelle",
                color=0x3498db
            )
            
            embed.add_field(
                name="🤖 Bot",
                value=f"Nom: `{config_manager.get('bot.name')}`\nPréfixe: `{config_manager.get('bot.prefix')}`",
                inline=False
            )
            
            embed.add_field(
                name="🎨 Apparence",
                value=f"Bio: `{config_manager.get('appearance.bio')}`\nStatut: `{config_manager.get('appearance.status')}`",
                inline=False
            )
            
            embed.add_field(
                name="⚙️ Fonctionnalités",
                value=f"Modération: `{config_manager.get('features.moderation.enabled')}`\n"
                       f"Vocal: `{config_manager.get('features.vocal.enabled')}`\n"
                       f"Jeux: `{config_manager.get('features.games.enabled')}`",
                inline=False
            )
            
            await ctx.send(embed=embed)
    
    # Commandes de permissions
    @commands.command(name="addadmin")
    @commands.has_permissions(administrator=True)
    async def add_admin(self, ctx, role: nextcord.Role):
        """Ajouter un rôle administrateur"""
        admin_roles = config_manager.get("permissions.admin_roles", [])
        if role.id in admin_roles:
            return await ctx.send("❌ Ce rôle est déjà administrateur.")
        
        admin_roles.append(role.id)
        config_manager.set("permissions.admin_roles", admin_roles)
        await ctx.send(f"✅ Rôle {role.mention} ajouté comme administrateur")
    
    @commands.command(name="removeadmin")
    @commands.has_permissions(administrator=True)
    async def remove_admin(self, ctx, role: nextcord.Role):
        """Retirer un rôle administrateur"""
        admin_roles = config_manager.get("permissions.admin_roles", [])
        if role.id not in admin_roles:
            return await ctx.send("❌ Ce rôle n'est pas administrateur.")
        
        admin_roles.remove(role.id)
        config_manager.set("permissions.admin_roles", admin_roles)
        await ctx.send(f"✅ Rôle {role.mention} retiré des administrateurs")
    
    @commands.command(name="addmod")
    @commands.has_permissions(administrator=True)
    async def add_mod(self, ctx, role: nextcord.Role):
        """Ajouter un rôle modérateur"""
        mod_roles = config_manager.get("permissions.moderator_roles", [])
        if role.id in mod_roles:
            return await ctx.send("❌ Ce rôle est déjà modérateur.")
        
        mod_roles.append(role.id)
        config_manager.set("permissions.moderator_roles", mod_roles)
        await ctx.send(f"✅ Rôle {role.mention} ajouté comme modérateur")
    
    @commands.command(name="removemod")
    @commands.has_permissions(administrator=True)
    async def remove_mod(self, ctx, role: nextcord.Role):
        """Retirer un rôle modérateur"""
        mod_roles = config_manager.get("permissions.moderator_roles", [])
        if role.id not in mod_roles:
            return await ctx.send("❌ Ce rôle n'est pas modérateur.")
        
        mod_roles.remove(role.id)
        config_manager.set("permissions.moderator_roles", mod_roles)
        await ctx.send(f"✅ Rôle {role.mention} retiré des modérateurs")
    
    # Commandes de messages
    @commands.command(name="setwelcome")
    @commands.has_permissions(administrator=True)
    async def set_welcome(self, ctx, *, message: str):
        """Définir le message de bienvenue"""
        config_manager.set("messages.welcome_message", message)
        await ctx.send(f"✅ Message de bienvenue défini: `{message}`")
    
    @commands.command(name="setgoodbye")
    @commands.has_permissions(administrator=True)
    async def set_goodbye(self, ctx, *, message: str):
        """Définir le message d'au revoir"""
        config_manager.set("messages.goodbye_message", message)
        await ctx.send(f"✅ Message d'au revoir défini: `{message}`")
    
    @commands.command(name="setlevelup")
    @commands.has_permissions(administrator=True)
    async def set_level_up(self, ctx, *, message: str):
        """Définir le message de niveau supérieur"""
        config_manager.set("messages.level_up_message", message)
        await ctx.send(f"✅ Message de niveau défini: `{message}`")

def setup(bot):
    bot.add_cog(BotCustomization(bot))
