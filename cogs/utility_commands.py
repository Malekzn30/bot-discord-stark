import nextcord
from nextcord.ext import commands
import asyncio
import datetime
import random
import aiohttp
import io

class UtilityCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reminders = {}
        self.afk_users = {}
    
    # ============= COMMANDES D'INFORMATION =============
    @commands.command(name="serverinfo")
    async def server_info(self, ctx):
        """Informations détaillées sur le serveur"""
        guild = ctx.guild
        
        embed = nextcord.Embed(
            title=f"📊 {guild.name}",
            description=guild.description or "Aucune description",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.set_footer(text=f"ID: {guild.id}")
        
        # Informations générales
        owner = guild.owner if guild.owner else await guild.fetch_member(guild.owner_id)
        embed.add_field(
            name="📝 Informations",
            value=f"**Propriétaire:** {owner.mention if owner else 'Inconnu'}\n"
                   f"**ID:** {guild.id}\n"
                   f"**Région:** {guild.region}\n"
                   f"**Créé le:** {guild.created_at.strftime('%d/%m/%Y')}\n"
                   f"**Boosts:** {guild.premium_tier} (Niveau {guild.premium_subscription_count})",
            inline=False
        )
        
        # Statistiques
        total_members = len(guild.members)
        online_members = len([m for m in guild.members if m.status != nextcord.Status.offline])
        bots = len([m for m in guild.members if m.bot])
        humans = total_members - bots
        
        embed.add_field(
            name="👥 Membres",
            value=f"**Total:** {total_members}\n"
                   f"**Humains:** {humans}\n"
                   f"**Bots:** {bots}\n"
                   f"**En ligne:** {online_members}",
            inline=True
        )
        
        # Salons et catégories
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        
        embed.add_field(
            name="📝 Salons",
            value=f"**Texte:** {text_channels}\n"
                   f"**Vocal:** {voice_channels}\n"
                   f"**Catégories:** {categories}",
            inline=True
        )
        
        # Autres
        roles = len(guild.roles)
        emojis = len(guild.emojis)
        stickers = len(guild.stickers)
        
        embed.add_field(
            name="🎭 Autres",
            value=f"**Rôles:** {roles}\n"
                   f"**Émojis:** {emojis}/100\n"
                   f"**Stickers:** {stickers}",
            inline=True
        )
        
        # Fonctionnalités
        features = []
        if guild.features:
            feature_map = {
                "COMMUNITY": "🏘️ Communauté",
                "NEWS": "📰 Actualités", 
                "WELCOME_SCREEN_ENABLED": "👋 Écran de bienvenue",
                "MEMBER_VERIFICATION_GATE_ENABLED": "✅ Vérification",
                "PREMIUM_TIER_3": "💎 Boost Niveau 3",
                "PREMIUM_TIER_2": "💎 Boost Niveau 2",
                "PREMIUM_TIER_1": "💎 Boost Niveau 1"
            }
            
            for feature in guild.features:
                if feature in feature_map:
                    features.append(feature_map[feature])
        
        if features:
            embed.add_field(
                name="✨ Fonctionnalités",
                value=" | ".join(features[:10]),
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="roleinfo")
    async def role_info(self, ctx, role: nextcord.Role):
        """Informations détaillées sur un rôle"""
        embed = nextcord.Embed(
            title=f"🎭 Informations sur {role.name}",
            color=role.color,
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(
            name="📝 Informations",
            value=f"**Nom:** {role.name}\n"
                   f"**ID:** {role.id}\n"
                   f"**Couleur:** {role.color}\n"
                   f"**Position:** {role.position}\n"
                   f"**Mentionnable:** {'Oui' if role.mentionable else 'Non'}\n"
                   f"**Hoist:** {'Oui' if role.hoist else 'Non'}\n"
                   f"**Géré:** {'Oui' if role.managed else 'Non'}",
            inline=False
        )
        
        # Permissions
        if role.permissions.administrator:
            perms_text = "🔑 Administrateur (toutes les permissions)"
        else:
            important_perms = []
            perm_map = {
                "kick_members": ("Expulser", "👢"),
                "ban_members": ("Bannir", "🔨"),
                "manage_messages": ("Gérer messages", "📝"),
                "manage_roles": ("Gérer rôles", "🎭"),
                "manage_channels": ("Gérer salons", "📢"),
                "mention_everyone": ("Mentionner everyone", "📢")
            }
            
            for perm, (name, emoji) in perm_map.items():
                if getattr(role.permissions, perm):
                    important_perms.append(f"{emoji} {name}")
            
            perms_text = "\n".join(important_perms) if important_perms else "Aucune permission spéciale"
        
        embed.add_field(name="🔐 Permissions", value=perms_text, inline=False)
        
        # Membres avec ce rôle
        members_with_role = len([m for m in ctx.guild.members if role in m.roles])
        embed.add_field(name="👥 Membres", value=f"{members_with_role} membre(s)", inline=True)
        
        embed.set_footer(text=f"Créé le {role.created_at.strftime('%d/%m/%Y %H:%M') if role.created_at else 'Inconnu'}")
        
        await ctx.send(embed=embed)
    
    # ============= COMMANDES UTILITAIRES =============
    @commands.command(name="afk")
    async def afk(self, ctx, *, reason: str = "AFK"):
        """Mettre son statut AFK"""
        self.afk_users[ctx.author.id] = {
            "reason": reason,
            "since": datetime.datetime.now()
        }
        
        await ctx.send(f"✅ {ctx.author.mention} est maintenant AFK: **{reason}**")
        
        # Changer le pseudo si possible
        try:
            await ctx.author.edit(nick=f"[AFK] {ctx.author.display_name}")
        except:
            pass
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        # Vérifier si un utilisateur AFK parle
        if message.author.id in self.afk_users:
            del self.afk_users[message.author.id]
            
            # Remettre le pseudo normal
            try:
                await message.author.edit(nick=message.author.display_name.replace("[AFK] ", ""))
            except:
                pass
            
            await message.channel.send(f"👋 {message.author.mention} n'est plus AFK !")
        
        # Mentionner les utilisateurs AFK
        for user_id in self.afk_users:
            if f"<@{user_id}>" in message.content or f"<@!{user_id}>" in message.content:
                afk_data = self.afk_users[user_id]
                time_afk = datetime.datetime.now() - afk_data["since"]
                
                await message.channel.send(
                    f"💤 {message.author.mention}, {self.bot.get_user(user_id).mention} est AFK: "
                    f"**{afk_data['reason']}** (depuis {time_afk.seconds//60} minutes)"
                )
    
    @commands.command(name="snipe")
    async def snipe(self, ctx):
        """Voir le dernier message supprimé"""
        if not hasattr(self, 'last_deleted_message'):
            return await ctx.send("❌ Aucun message supprimé récemment.")
        
        msg = self.last_deleted_message
        embed = nextcord.Embed(
            title="🔍 Message Supprimé",
            description=msg.content,
            color=0xE74C3C,
            timestamp=msg.created_at
        )
        
        embed.set_author(name=msg.author.name, icon_url=msg.author.display_avatar.url)
        embed.set_footer(text=f"Salon: #{msg.channel.name}")
        
        await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        
        self.last_deleted_message = message
    
    @commands.command(name="editsnipe")
    async def edit_snipe(self, ctx):
        """Voir le dernier message modifié"""
        if not hasattr(self, 'last_edited_message'):
            return await ctx.send("❌ Aucun message modifié récemment.")
        
        msg = self.last_edited_message
        embed = nextcord.Embed(
            title="📝 Message Modifié",
            color=0xF39C12,
            timestamp=msg.edited_at
        )
        
        embed.add_field(name="Avant", value=msg.content, inline=False)
        embed.add_field(name="Après", value=msg.edited_content, inline=False)
        
        embed.set_author(name=msg.author.name, icon_url=msg.author.display_avatar.url)
        embed.set_footer(text=f"Salon: #{msg.channel.name}")
        
        await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload):
        if payload.cached_message:
            msg = payload.cached_message
            if msg.content != payload.data.get('content', ''):
                self.last_edited_message = msg
                self.last_edited_message.edited_content = payload.data.get('content', '')
    
    @commands.command(name="emoji")
    async def emoji_info(self, ctx, emoji: nextcord.Emoji):
        """Informations sur un émoji"""
        embed = nextcord.Embed(
            title=f"😀 Informations sur {emoji.name}",
            color=0x3498db
        )
        
        embed.set_thumbnail(url=emoji.url)
        
        embed.add_field(
            name="📝 Informations",
            value=f"**Nom:** {emoji.name}\n"
                   f"**ID:** {emoji.id}\n"
                   f"**Animé:** {'Oui' if emoji.animated else 'Non'}\n"
                   f"**Géré:** {'Oui' if emoji.managed else 'Non'}\n"
                   f"**Disponible:** {'Oui' if emoji.available else 'Non'}",
            inline=False
        )
        
        embed.add_field(
            name="🔗 Liens",
            value=f"[Émoji]({emoji.url})\n"
                   f"`<:{emoji.name}:{emoji.id}>`",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="steal")
    async def steal_emoji(self, ctx, emoji: nextcord.Emoji, name: str = None):
        """Ajouter un émoji d'un autre serveur"""
        if ctx.guild.emoji_limit >= ctx.guild.emoji_limit:
            return await ctx.send("❌ Limite d'émojis atteinte.")
        
        emoji_name = name or emoji.name
        
        try:
            # Télécharger l'émoji
            async with aiohttp.ClientSession() as session:
                async with session.get(emoji.url) as response:
                    if response.status == 200:
                        emoji_bytes = await response.read()
                        
                        # Créer l'émoji
                        new_emoji = await ctx.guild.create_custom_emoji(
                            name=emoji_name,
                            image=emoji_bytes,
                            reason=f"Volé par {ctx.author}"
                        )
                        
                        embed = nextcord.Embed(
                            title="✅ Émoji ajouté",
                            description=f"Émoji {new_emoji} ajouté avec succès !",
                            color=0x2ECC71
                        )
                        
                        await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="firstmessage")
    async def first_message(self, ctx, channel: nextcord.TextChannel = None):
        """Voir le premier message d'un salon"""
        target_channel = channel or ctx.channel
        
        try:
            async for message in target_channel.history(limit=1, oldest_first=True):
                embed = nextcord.Embed(
                    title="📜 Premier Message",
                    description=message.content,
                    color=0x3498db,
                    timestamp=message.created_at
                )
                
                embed.set_author(
                    name=message.author.name,
                    icon_url=message.author.display_avatar.url
                )
                
                embed.set_footer(
                    text=f"Message ID: {message.id} | Salon: #{target_channel.name}"
                )
                
                if message.attachments:
                    embed.add_field(
                        name="📎 Pièces jointes",
                        value="\n".join([f"[{a.filename}]({a.url})" for a in message.attachments]),
                        inline=False
                    )
                
                await ctx.send(embed=embed)
                return
        except:
            await ctx.send("❌ Impossible de trouver le premier message.")
    
    @commands.command(name="createinvite")
    async def create_invite(self, ctx, channel: nextcord.TextChannel = None, max_uses: int = 1, expires_in: int = 24):
        """Créer une invitation"""
        target_channel = channel or ctx.channel
        
        try:
            invite = await target_channel.create_invite(
                max_uses=max_uses,
                max_age=expires_in * 3600,
                reason=f"Créée par {ctx.author}"
            )
            
            embed = nextcord.Embed(
                title="✅ Invitation Créée",
                description=f"**Lien:** {invite.url}\n"
                           f"**Utilisations:** {invite.uses}/{invite.max_uses}\n"
                           f"**Expire dans:** {expires_in}h",
                color=0x2ECC71
            )
            
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="channelinfo")
    async def channel_info(self, ctx, channel: nextcord.TextChannel = None):
        """Informations sur un salon"""
        target_channel = channel or ctx.channel
        
        embed = nextcord.Embed(
            title=f"📝 Informations sur #{target_channel.name}",
            description=target_channel.topic or "Aucun sujet",
            color=0x3498db,
            timestamp=target_channel.created_at
        )
        
        embed.add_field(
            name="📝 Informations",
            value=f"**Nom:** {target_channel.name}\n"
                   f"**ID:** {target_channel.id}\n"
                   f"**Type:** {target_channel.type}\n"
                   f"**NSFW:** {'Oui' if target_channel.is_nsfw() else 'Non'}\n"
                   f"**Position:** {target_channel.position}",
            inline=False
        )
        
        # Permissions du salon
        overwrites = []
        for target, overwrite in target_channel.overwrites.items():
            if isinstance(target, nextcord.Role):
                name = f"🎭 {target.name}"
            elif isinstance(target, nextcord.Member):
                name = f"👤 {target.name}"
            else:
                name = f"👥 {target.name}"
            
            allow_perms = [perm for perm, value in overwrite.allow if value]
            deny_perms = [perm for perm, value in overwrite.deny if value]
            
            overwrites.append(f"{name}: ✅{len(allow_perms)} ❌{len(deny_perms)}")
        
        if overwrites:
            embed.add_field(
                name="🔐 Permissions spéciales",
                value="\n".join(overwrites[:5]),
                inline=False
            )
        
        embed.set_footer(text=f"Catégorie: {target_channel.category.name if target_channel.category else 'Aucune'}")
        
        await ctx.send(embed=embed)
    
    # ============= COMMANDES DE MODÉRATION AMÉLIORÉES =============
    @commands.command(name="slowmode")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int = 0):
        """Activer le mode lent"""
        if seconds < 0 or seconds > 21600:  # 6 heures max
            return await ctx.send("❌ Le mode lent doit être entre 0 et 21600 secondes.")
        
        await ctx.channel.edit(slowmode_delay=seconds)
        
        if seconds == 0:
            await ctx.send("✅ Mode lent désactivé.")
        else:
            await ctx.send(f"✅ Mode lent activé: **{seconds} secondes** entre chaque message.")
    
    @commands.command(name="lockdown")
    @commands.has_permissions(manage_channels=True)
    async def lockdown(self, ctx):
        """Verrouiller le serveur (tout le monde ne peut pas parler)"""
        embed = nextcord.Embed(
            title="🔒 LOCKDOWN ACTIVÉ",
            description="Le serveur est actuellement en lockdown. Seuls les administrateurs peuvent parler.",
            color=0xE74C3C
        )
        
        # Verrouiller tous les salons textuels
        for channel in ctx.guild.text_channels:
            try:
                await channel.set_permissions(ctx.guild.default_role, send_messages=False)
            except:
                continue
        
        await ctx.send(embed=embed)
    
    @commands.command(name="unlockdown")
    @commands.has_permissions(manage_channels=True)
    async def unlockdown(self, ctx):
        """Déverrouiller le serveur"""
        embed = nextcord.Embed(
            title="🔓 LOCKDOWN DÉSACTIVÉ",
            description="Le serveur n'est plus en lockdown. Tout le monde peut parler.",
            color=0x2ECC71
        )
        
        # Déverrouiller tous les salons textuels
        for channel in ctx.guild.text_channels:
            try:
                await channel.set_permissions(ctx.guild.default_role, send_messages=True)
            except:
                continue
        
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(UtilityCommands(bot))
