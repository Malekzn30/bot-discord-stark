import nextcord
from nextcord.ext import commands
import asyncio
import re
import json
import os
from datetime import datetime, timedelta
from config import AUTHORIZED_ROLE_ID

def has_role():
    async def predicate(ctx):
        role = ctx.guild.get_role(AUTHORIZED_ROLE_ID)
        return role in ctx.author.roles
    return commands.check(predicate)

class AntiMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.whitelist_file = "data/whitelist.json"
        self.whitelist = self.load_whitelist()
        self.link_pattern = re.compile(
            r'(https?://)?(www\.)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(\/[^\s]*)?',
            re.IGNORECASE
        )
        self.muted_users = {}  # Pour gérer les mutes temporaires

    def load_whitelist(self):
        """Charger la whitelist depuis le fichier"""
        try:
            if os.path.exists(self.whitelist_file):
                with open(self.whitelist_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Whitelist par défaut
                default_whitelist = [
                    "discord.com",
                    "discord.gg", 
                    "twitch.tv",
                    "youtube.com",
                    "youtu.be",
                    "twitter.com",
                    "x.com",
                    "tiktok.com",
                    "instagram.com",
                    "facebook.com",
                    "reddit.com",
                    "github.com",
                    "openai.com",
                    "spotify.com"
                ]
                self.save_whitelist(default_whitelist)
                return default_whitelist
        except Exception as e:
            print(f"Erreur chargement whitelist: {e}")
            return ["discord.com", "discord.gg", "twitch.tv", "youtube.com"]

    def save_whitelist(self, whitelist_data):
        """Sauvegarder la whitelist dans le fichier"""
        try:
            os.makedirs(os.path.dirname(self.whitelist_file), exist_ok=True)
            with open(self.whitelist_file, 'w', encoding='utf-8') as f:
                json.dump(whitelist_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur sauvegarde whitelist: {e}")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Détecter et supprimer les liens non autorisés"""
        
        # Ignorer les messages des bots
        if message.author.bot:
            return
        
        # Ignorer les messages des admins (rôle autorisé)
        if message.guild:
            role = message.guild.get_role(AUTHORIZED_ROLE_ID)
            if role and role in message.author.roles:
                return
        
        # Chercher des liens dans le message
        links = self.link_pattern.findall(message.content)
        
        if not links:
            return
        
        # Vérifier chaque lien
        for link_tuple in links:
            # Reconstruire le lien
            protocol = link_tuple[0] or "https://"
            www = link_tuple[1] or ""
            domain = link_tuple[2]
            path = link_tuple[3] or ""
            
            full_link = f"{protocol}{www}{domain}{path}"
            
            # Nettoyer le domaine pour la vérification
            clean_domain = domain.lower().rstrip('.')
            
            # Vérifier si le domaine est dans la whitelist
            if not any(allowed in clean_domain for allowed in self.whitelist):
                await self.handle_unauthorized_link(message, full_link, clean_domain)
                break  # Un seul traitement par message

    async def handle_unauthorized_link(self, message, link, domain):
        """Gérer un lien non autorisé"""
        
        try:
            # Supprimer le message
            await message.delete()
            
            # Mute l'utilisateur 5 secondes
            await self.temp_mute_user(message.author, message.guild, 5)
            
            # Envoyer un message de warning
            embed = nextcord.Embed(
                title="🔒 Lien non autorisé détecté",
                description=f"**{message.author.mention}** a envoyé un lien non autorisé",
                color=0xE74C3C
            )
            
            embed.add_field(
                name="🚫 Lien supprimé",
                value=f"**Domaine :** `{domain}`\n**Lien :** {link}",
                inline=False
            )
            
            embed.add_field(
                name="⏰ Sanction",
                value="**Mute de 5 secondes** appliqué",
                inline=False
            )
            
            embed.add_field(
                name="ℹ️ Information",
                value="Seuls les liens des domaines autorisés sont permis.\nContactez un administrateur pour ajouter un domaine à la whitelist.",
                inline=False
            )
            
            embed.set_footer(text="Protection anti-liens automatique")
            embed.set_thumbnail(url=message.guild.icon.url if message.guild.icon else None)
            
            warning_msg = await message.channel.send(embed=embed)
            
            # Supprimer le message de warning après 10 secondes
            await asyncio.sleep(10)
            try:
                await warning_msg.delete()
            except:
                pass
            
            # Logger l'action
            try:
                from cogs.logs import log_command, log_moderation
                log_moderation("anti_link", message.author.name, f"Domaine: {domain}", "Lien non autorisé supprimé et mute 5s")
            except:
                pass
                
        except nextcord.Forbidden:
            # Si le bot ne peut pas supprimer le message
            try:
                await message.channel.send(
                    f"🚫 {message.author.mention} Lien non autorisé détecté mais je ne peux pas le supprimer. "
                    f"Veuillez contacter un administrateur."
                )
            except:
                pass
        except Exception as e:
            print(f"Erreur traitement lien non autorisé: {e}")

    async def temp_mute_user(self, user, guild, duration_seconds):
        """Mute temporaire d'un utilisateur"""
        
        try:
            # Créer ou récupérer le rôle "Muted"
            muted_role = nextcord.utils.get(guild.roles, name="Muted")
            
            if not muted_role:
                # Créer le rôle Muted s'il n'existe pas
                muted_role = await guild.create_role(
                    name="Muted",
                    color=nextcord.Color.dark_grey(),
                    reason="Création rôle pour anti-liens"
                )
                
                # Configurer les permissions pour tous les salons
                for channel in guild.channels:
                    if isinstance(channel, (nextcord.TextChannel, nextcord.VoiceChannel)):
                        await channel.set_permissions(muted_role, send_messages=False, speak=False)
            
            # Appliquer le mute
            await user.add_roles(muted_role, reason="Lien non autorisé - 5 secondes")
            
            # Stocker pour le unmute automatique
            self.muted_users[user.id] = {
                "role": muted_role,
                "guild": guild,
                "end_time": datetime.now() + timedelta(seconds=duration_seconds)
            }
            
            # Programmer le unmute
            self.bot.loop.create_task(self.scheduled_unmute(user.id, duration_seconds))
            
        except Exception as e:
            print(f"Erreur mute temporaire: {e}")

    async def scheduled_unmute(self, user_id, delay):
        """Unmute programmé"""
        await asyncio.sleep(delay)
        
        if user_id in self.muted_users:
            mute_info = self.muted_users.pop(user_id)
            
            try:
                guild = mute_info["guild"]
                role = mute_info["role"]
                user = guild.get_member(user_id)
                
                if user and role in user.roles:
                    await user.remove_roles(role, reason="Fin du mute temporaire")
                    
            except Exception as e:
                print(f"Erreur unmute programmé: {e}")

    @commands.command(name="whitelist")
    @has_role()
    async def manage_whitelist(self, ctx, action: str = None, domain: str = None):
        """
        Gérer la whitelist des domaines autorisés
        
        Utilisation:
        +whitelist list                    - Voir la whitelist
        +whitelist add <domaine>           - Ajouter un domaine
        +whitelist remove <domaine>        - Retirer un domaine
        +whitelist clear                   - Vider la whitelist
        """
        
        if not action:
            return await self.show_whitelist_help(ctx)
        
        action = action.lower()
        
        if action == "list":
            await self.show_whitelist(ctx)
        elif action == "add" and domain:
            await self.add_to_whitelist(ctx, domain)
        elif action == "remove" and domain:
            await self.remove_from_whitelist(ctx, domain)
        elif action == "clear":
            await self.clear_whitelist(ctx)
        else:
            await self.show_whitelist_help(ctx)

    async def show_whitelist_help(self, ctx):
        """Afficher l'aide pour la whitelist"""
        embed = nextcord.Embed(
            title="🔒 Gestion de la Whitelist",
            description="Commandes pour gérer les domaines autorisés",
            color=0x3498db
        )
        
        embed.add_field(
            name="📋 Commandes disponibles",
            value=(
                "`+whitelist list` - Voir tous les domaines autorisés\n"
                "`+whitelist add <domaine>` - Ajouter un domaine\n"
                "`+whitelist remove <domaine>` - Retirer un domaine\n"
                "`+whitelist clear` - Vider la whitelist"
            ),
            inline=False
        )
        
        embed.add_field(
            name="ℹ️ Information",
            value=(
                "Les domaines dans la whitelist sont autorisés dans les messages.\n"
                "Les autres liens seront automatiquement supprimés et l'utilisateur sera muet 5 secondes."
            ),
            inline=False
        )
        
        embed.set_footer(text=f"Actuellement {len(self.whitelist)} domaine(s) dans la whitelist")
        await ctx.send(embed=embed)

    async def show_whitelist(self, ctx):
        """Afficher la whitelist actuelle"""
        if not self.whitelist:
            embed = nextcord.Embed(
                title="🔒 Whitelist vide",
                description="Aucun domaine n'est actuellement autorisé",
                color=0xE74C3C
            )
            return await ctx.send(embed=embed)
        
        embed = nextcord.Embed(
            title="🔒 Domaines autorisés",
            description=f"**{len(self.whitelist)}** domaine(s) dans la whitelist",
            color=0x2ECC71
        )
        
        # Organiser par catégories
        categories = {
            "📱 Réseaux sociaux": ["twitter.com", "x.com", "tiktok.com", "instagram.com", "facebook.com", "reddit.com"],
            "🎮 Streaming": ["twitch.tv", "youtube.com", "youtu.be", "spotify.com"],
            "💻 Développement": ["github.com", "openai.com"],
            "💬 Communication": ["discord.com", "discord.gg"],
            "🌐 Autres": []
        }
        
        # Classer les domaines
        categorized = {cat: [] for cat in categories}
        uncategorized = []
        
        for domain in self.whitelist:
            placed = False
            for category, domains in categories.items():
                if category != "🌐 Autres" and domain in domains:
                    categorized[category].append(domain)
                    placed = True
                    break
            if not placed:
                uncategorized.append(domain)
        
        categorized["🌐 Autres"] = uncategorized
        
        # Afficher les catégories
        for category, domains in categorized.items():
            if domains:
                domain_list = "\n".join([f"• `{domain}`" for domain in domains])
                embed.add_field(name=category, value=domain_list, inline=False)
        
        embed.set_footer(text="Utilise +whitelist add <domaine> pour ajouter un domaine")
        await ctx.send(embed=embed)

    async def add_to_whitelist(self, ctx, domain):
        """Ajouter un domaine à la whitelist"""
        domain = domain.lower().strip()
        
        if domain in self.whitelist:
            embed = nextcord.Embed(
                title="⚠️ Domaine déjà existant",
                description=f"`{domain}` est déjà dans la whitelist",
                color=0xF39C12
            )
            return await ctx.send(embed=embed)
        
        self.whitelist.append(domain)
        self.save_whitelist(self.whitelist)
        
        embed = nextcord.Embed(
            title="✅ Domaine ajouté",
            description=f"`{domain}` a été ajouté à la whitelist",
            color=0x2ECC71
        )
        
        embed.add_field(
            name="📊 Statistiques",
            value=f"**{len(self.whitelist)}** domaine(s) maintenant autorisés",
            inline=False
        )
        
        embed.set_footer(text="Les liens vers ce domaine ne seront plus supprimés")
        await ctx.send(embed=embed)
        
        # Logger l'action
        try:
            from cogs.logs import log_command
            log_command(ctx, "whitelist_add", f"Domaine: {domain}")
        except:
            pass

    async def remove_from_whitelist(self, ctx, domain):
        """Retirer un domaine de la whitelist"""
        domain = domain.lower().strip()
        
        if domain not in self.whitelist:
            embed = nextcord.Embed(
                title="❌ Domaine introuvable",
                description=f"`{domain}` n'est pas dans la whitelist",
                color=0xE74C3C
            )
            return await ctx.send(embed=embed)
        
        self.whitelist.remove(domain)
        self.save_whitelist(self.whitelist)
        
        embed = nextcord.Embed(
            title="✅ Domaine retiré",
            description=f"`{domain}` a été retiré de la whitelist",
            color=0xE74C3C
        )
        
        embed.add_field(
            name="⚠️ Attention",
            value="Les liens vers ce domaine seront maintenant supprimés automatiquement",
            inline=False
        )
        
        embed.add_field(
            name="📊 Statistiques",
            value=f"**{len(self.whitelist)}** domaine(s) restent autorisés",
            inline=False
        )
        
        embed.set_footer(text="Utilise +whitelist list pour voir la whitelist actuelle")
        await ctx.send(embed=embed)
        
        # Logger l'action
        try:
            from cogs.logs import log_command
            log_command(ctx, "whitelist_remove", f"Domaine: {domain}")
        except:
            pass

    async def clear_whitelist(self, ctx):
        """Vider la whitelist"""
        if not self.whitelist:
            embed = nextcord.Embed(
                title="ℹ️ Whitelist déjà vide",
                description="La whitelist est déjà vide",
                color=0xF39C12
            )
            return await ctx.send(embed=embed)
        
        old_count = len(self.whitelist)
        self.whitelist = []
        self.save_whitelist(self.whitelist)
        
        embed = nextcord.Embed(
            title="🗑️ Whitelist vidée",
            description=f"**{old_count}** domaine(s) ont été retirés de la whitelist",
            color=0xE74C3C
        )
        
        embed.add_field(
            name="⚠️ Attention",
            value="Tous les liens (sauf Discord) seront maintenant supprimés",
            inline=False
        )
        
        embed.set_footer(text="Utilise +whitelist add <domaine> pour ajouter des domaines")
        await ctx.send(embed=embed)
        
        # Logger l'action
        try:
            from cogs.logs import log_command
            log_command(ctx, "whitelist_clear", f"Anciens domaines: {old_count}")
        except:
            pass

def setup(bot):
    bot.add_cog(AntiMod(bot))
