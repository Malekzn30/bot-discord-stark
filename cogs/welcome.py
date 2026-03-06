import nextcord
from nextcord.ext import commands
import datetime
import json
import os

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ensure_data_files()
    
    def ensure_data_files(self):
        """Créer les fichiers de données nécessaires"""
        os.makedirs("data", exist_ok=True)
        
        if not os.path.exists("data/welcome_config.json"):
            with open("data/welcome_config.json", "w") as f:
                json.dump({
                    "welcome_channel": None,
                    "welcome_message": "Bienvenue {user} sur {server}!",
                    "welcome_enabled": True,
                    "leave_channel": None,
                    "leave_message": "Au revoir {user}!",
                    "leave_enabled": True,
                    "auto_role": None
                }, f, indent=2)
    
    @commands.command(name="setwelchannel")
    @commands.has_permissions(manage_guild=True)
    async def setwelchannel(self, ctx, channel: nextcord.TextChannel = None):
        """Définir le canal de bienvenue"""
        try:
            target_channel = channel or ctx.channel
            
            with open("data/welcome_config.json", "r") as f:
                config = json.load(f)
            
            config["welcome_channel"] = target_channel.id
            
            with open("data/welcome_config.json", "w") as f:
                json.dump(config, f, indent=2)
            
            embed = nextcord.Embed(
                title="✅ Canal de Bienvenue Défini",
                description=f"**Canal:** {target_channel.mention}",
                color=0x2ecc71,
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Défini par {ctx.author.name}")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="setleavechannel")
    @commands.has_permissions(manage_guild=True)
    async def setleavechannel(self, ctx, channel: nextcord.TextChannel = None):
        """Définir le canal de départ"""
        try:
            target_channel = channel or ctx.channel
            
            with open("data/welcome_config.json", "r") as f:
                config = json.load(f)
            
            config["leave_channel"] = target_channel.id
            
            with open("data/welcome_config.json", "w") as f:
                json.dump(config, f, indent=2)
            
            embed = nextcord.Embed(
                title="✅ Canal de Départ Défini",
                description=f"**Canal:** {target_channel.mention}",
                color=0xe74c3c,
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Défini par {ctx.author.name}")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="setwelmessage")
    @commands.has_permissions(manage_guild=True)
    async def setwelmessage(self, ctx, *, message: str):
        """Définir le message de bienvenue"""
        try:
            with open("data/welcome_config.json", "r") as f:
                config = json.load(f)
            
            config["welcome_message"] = message
            
            with open("data/welcome_config.json", "w") as f:
                json.dump(config, f, indent=2)
            
            embed = nextcord.Embed(
                title="✅ Message de Bienvenue Défini",
                description=f"**Message:** {message}",
                color=0x2ecc71,
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Défini par {ctx.author.name}")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="setleavemessage")
    @commands.has_permissions(manage_guild=True)
    async def setleavemessage(self, ctx, *, message: str):
        """Définir le message de départ"""
        try:
            with open("data/welcome_config.json", "r") as f:
                config = json.load(f)
            
            config["leave_message"] = message
            
            with open("data/welcome_config.json", "w") as f:
                json.dump(config, f, indent=2)
            
            embed = nextcord.Embed(
                title="✅ Message de Départ Défini",
                description=f"**Message:** {message}",
                color=0xe74c3c,
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Défini par {ctx.author.name}")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="setautorole")
    @commands.has_permissions(manage_guild=True)
    async def setautorole(self, ctx, role: nextcord.Role = None):
        """Définir le rôle automatique"""
        try:
            with open("data/welcome_config.json", "r") as f:
                config = json.load(f)
            
            config["auto_role"] = role.id if role else None
            
            with open("data/welcome_config.json", "w") as f:
                json.dump(config, f, indent=2)
            
            if role:
                embed = nextcord.Embed(
                    title="✅ Rôle Automatique Défini",
                    description=f"**Rôle:** {role.mention}",
                    color=0x2ecc71,
                    timestamp=datetime.datetime.now()
                )
            else:
                embed = nextcord.Embed(
                    title="❌ Rôle Automatique Désactivé",
                    description="Aucun rôle ne sera automatiquement attribué.",
                    color=0xe74c3c,
                    timestamp=datetime.datetime.now()
                )
            
            embed.set_footer(text=f"Défini par {ctx.author.name}")
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="togglewelcome")
    @commands.has_permissions(manage_guild=True)
    async def togglewelcome(self, ctx):
        """Activer/désactiver les messages de bienvenue"""
        try:
            with open("data/welcome_config.json", "r") as f:
                config = json.load(f)
            
            config["welcome_enabled"] = not config.get("welcome_enabled", True)
            
            with open("data/welcome_config.json", "w") as f:
                json.dump(config, f, indent=2)
            
            status = "activé" if config["welcome_enabled"] else "désactivé"
            color = 0x2ecc71 if config["welcome_enabled"] else 0xe74c3c
            
            embed = nextcord.Embed(
                title=f"✅ Messages de Bienvenue {status.title()}",
                description=f"Les messages de bienvenue sont maintenant {status}.",
                color=color,
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Modifié par {ctx.author.name}")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="toggleleave")
    @commands.has_permissions(manage_guild=True)
    async def toggleleave(self, ctx):
        """Activer/désactiver les messages de départ"""
        try:
            with open("data/welcome_config.json", "r") as f:
                config = json.load(f)
            
            config["leave_enabled"] = not config.get("leave_enabled", True)
            
            with open("data/welcome_config.json", "w") as f:
                json.dump(config, f, indent=2)
            
            status = "activé" if config["leave_enabled"] else "désactivé"
            color = 0x2ecc71 if config["leave_enabled"] else 0xe74c3c
            
            embed = nextcord.Embed(
                title=f"✅ Messages de Départ {status.title()}",
                description=f"Les messages de départ sont maintenant {status}.",
                color=color,
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Modifié par {ctx.author.name}")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="welcomeconfig")
    @commands.has_permissions(manage_guild=True)
    async def welcomeconfig(self, ctx):
        """Voir la configuration de bienvenue"""
        try:
            with open("data/welcome_config.json", "r") as f:
                config = json.load(f)
            
            embed = nextcord.Embed(
                title="⚙️ Configuration de Bienvenue",
                description="Configuration actuelle du système de bienvenue:",
                color=0x3498db,
                timestamp=datetime.datetime.now()
            )
            
            # Canal de bienvenue
            welcome_channel = ctx.guild.get_channel(config.get("welcome_channel"))
            embed.add_field(
                name="📢 Canal Bienvenue", 
                value=welcome_channel.mention if welcome_channel else "Non défini", 
                inline=True
            )
            
            # Canal de départ
            leave_channel = ctx.guild.get_channel(config.get("leave_channel"))
            embed.add_field(
                name="📢 Canal Départ", 
                value=leave_channel.mention if leave_channel else "Non défini", 
                inline=True
            )
            
            # Rôle automatique
            auto_role = ctx.guild.get_role(config.get("auto_role"))
            embed.add_field(
                name="🎭 Rôle Automatique", 
                value=auto_role.mention if auto_role else "Non défini", 
                inline=True
            )
            
            # Messages
            embed.add_field(
                name="📝 Message Bienvenue", 
                value=config.get("welcome_message", "Non défini"), 
                inline=False
            )
            
            embed.add_field(
                name="📝 Message Départ", 
                value=config.get("leave_message", "Non défini"), 
                inline=False
            )
            
            # Statuts
            welcome_status = "✅ Activé" if config.get("welcome_enabled", True) else "❌ Désactivé"
            leave_status = "✅ Activé" if config.get("leave_enabled", True) else "❌ Désactivé"
            
            embed.add_field(
                name="🔧 Statut Bienvenue", 
                value=welcome_status, 
                inline=True
            )
            
            embed.add_field(
                name="🔧 Statut Départ", 
                value=leave_status, 
                inline=True
            )
            
            embed.set_footer(text=f"Demandé par {ctx.author.name}")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Quand un membre rejoint le serveur"""
        try:
            with open("data/welcome_config.json", "r") as f:
                config = json.load(f)
            
            if not config.get("welcome_enabled", True):
                return
            
            # Envoyer le message de bienvenue
            welcome_channel = member.guild.get_channel(config.get("welcome_channel"))
            if welcome_channel:
                message = config.get("welcome_message", "Bienvenue {user} sur {server}!")
                message = message.format(
                    user=member.mention,
                    server=member.guild.name,
                    count=member.guild.member_count
                )
                
                embed = nextcord.Embed(
                    title="🎉 Nouveau Membre!",
                    description=message,
                    color=0x2ecc71,
                    timestamp=datetime.datetime.now()
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_footer(text=f"ID: {member.id}")
                
                await welcome_channel.send(embed=embed)
            
            # Attribuer le rôle automatique
            auto_role_id = config.get("auto_role")
            if auto_role_id:
                auto_role = member.guild.get_role(auto_role_id)
                if auto_role:
                    await member.add_roles(auto_role, reason="Rôle automatique de bienvenue")
                    
        except Exception as e:
            print(f"Erreur welcome join: {e}")
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Quand un membre quitte le serveur"""
        try:
            with open("data/welcome_config.json", "r") as f:
                config = json.load(f)
            
            if not config.get("leave_enabled", True):
                return
            
            # Envoyer le message de départ
            leave_channel = member.guild.get_channel(config.get("leave_channel"))
            if leave_channel:
                message = config.get("leave_message", "Au revoir {user}!")
                message = message.format(
                    user=member.name,
                    server=member.guild.name
                )
                
                embed = nextcord.Embed(
                    title="👋 Départ d'un Membre",
                    description=message,
                    color=0xe74c3c,
                    timestamp=datetime.datetime.now()
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_footer(text=f"ID: {member.id}")
                
                await leave_channel.send(embed=embed)
                    
        except Exception as e:
            print(f"Erreur welcome leave: {e}")

def setup(bot):
    bot.add_cog(Welcome(bot))
