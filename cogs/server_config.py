import nextcord
from nextcord.ext import commands
import datetime
import json
import os

class ServerConfig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ensure_data_files()
    
    def ensure_data_files(self):
        """Créer les fichiers de données nécessaires"""
        os.makedirs("data", exist_ok=True)
        
        if not os.path.exists("data/server_config.json"):
            with open("data/server_config.json", "w") as f:
                json.dump({
                    "prefix": "+",
                    "mod_channel": None,
                    "log_channel": None,
                    "welcome_channel": None,
                    "leave_channel": None,
                    "auto_role": None,
                    "mute_role": None,
                    "max_warnings": 3,
                    "welcome_enabled": True,
                    "leave_enabled": True,
                    "anti_spam": True,
                    "anti_invite": True,
                    "custom_commands": {}
                }, f, indent=2)
    
    @commands.command(name="serverconfig")
    @commands.has_permissions(administrator=True)
    async def serverconfig(self, ctx):
        """Voir la configuration complète du serveur"""
        try:
            with open("data/server_config.json", "r") as f:
                config = json.load(f)
            
            embed = nextcord.Embed(
                title="⚙️ Configuration du Serveur",
                description=f"Configuration pour **{ctx.guild.name}**:",
                color=0x3498db,
                timestamp=datetime.datetime.now()
            )
            
            # Informations générales
            embed.add_field(name="🔧 Préfixe", value=f"`{config.get('prefix', '+')}`", inline=True)
            embed.add_field(name="⚠️ Max Warnings", value=str(config.get('max_warnings', 3)), inline=True)
            
            # Canaux
            mod_channel = ctx.guild.get_channel(config.get("mod_channel"))
            log_channel = ctx.guild.get_channel(config.get("log_channel"))
            welcome_channel = ctx.guild.get_channel(config.get("welcome_channel"))
            leave_channel = ctx.guild.get_channel(config.get("leave_channel"))
            
            embed.add_field(name="🛡️ Canal Mod", value=mod_channel.mention if mod_channel else "Non défini", inline=True)
            embed.add_field(name="📋 Canal Logs", value=log_channel.mention if log_channel else "Non défini", inline=True)
            embed.add_field(name="🎉 Canal Bienvenue", value=welcome_channel.mention if welcome_channel else "Non défini", inline=True)
            embed.add_field(name="👋 Canal Départ", value=leave_channel.mention if leave_channel else "Non défini", inline=True)
            
            # Rôles
            auto_role = ctx.guild.get_role(config.get("auto_role"))
            mute_role = ctx.guild.get_role(config.get("mute_role"))
            
            embed.add_field(name="🎭 Rôle Auto", value=auto_role.mention if auto_role else "Non défini", inline=True)
            embed.add_field(name="🔇 Rôle Mute", value=mute_role.mention if mute_role else "Non défini", inline=True)
            
            # Systèmes
            welcome_status = "✅" if config.get("welcome_enabled", True) else "❌"
            leave_status = "✅" if config.get("leave_enabled", True) else "❌"
            anti_spam_status = "✅" if config.get("anti_spam", True) else "❌"
            anti_invite_status = "✅" if config.get("anti_invite", True) else "❌"
            
            embed.add_field(name="🎉 Bienvenue", value=welcome_status, inline=True)
            embed.add_field(name="👋 Départ", value=leave_status, inline=True)
            embed.add_field(name="🛡️ Anti-Spam", value=anti_spam_status, inline=True)
            embed.add_field(name="🚫 Anti-Invite", value=anti_invite_status, inline=True)
            
            # Commandes personnalisées
            custom_commands = config.get("custom_commands", {})
            embed.add_field(name="⚙️ Commandes Perso", value=str(len(custom_commands)), inline=True)
            
            embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
            embed.set_footer(text=f"Demandé par {ctx.author.name}")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="setmodchannel")
    @commands.has_permissions(administrator=True)
    async def setmodchannel(self, ctx, channel: nextcord.TextChannel = None):
        """Définir le canal de modération"""
        try:
            target_channel = channel or ctx.channel
            
            with open("data/server_config.json", "r") as f:
                config = json.load(f)
            
            config["mod_channel"] = target_channel.id
            
            with open("data/server_config.json", "w") as f:
                json.dump(config, f, indent=2)
            
            embed = nextcord.Embed(
                title="✅ Canal de Modération Défini",
                description=f"**Canal:** {target_channel.mention}",
                color=0x2ecc71,
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Défini par {ctx.author.name}")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="setmuterole")
    @commands.has_permissions(administrator=True)
    async def setmuterole(self, ctx, role: nextcord.Role = None):
        """Définir le rôle mute"""
        try:
            with open("data/server_config.json", "r") as f:
                config = json.load(f)
            
            config["mute_role"] = role.id if role else None
            
            with open("data/server_config.json", "w") as f:
                json.dump(config, f, indent=2)
            
            if role:
                embed = nextcord.Embed(
                    title="✅ Rôle Mute Défini",
                    description=f"**Rôle:** {role.mention}",
                    color=0x2ecc71,
                    timestamp=datetime.datetime.now()
                )
            else:
                embed = nextcord.Embed(
                    title="❌ Rôle Mute Désactivé",
                    description="Aucun rôle mute n'est défini.",
                    color=0xe74c3c,
                    timestamp=datetime.datetime.now()
                )
            
            embed.set_footer(text=f"Défini par {ctx.author.name}")
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="setmaxwarnings")
    @commands.has_permissions(administrator=True)
    async def setmaxwarnings(self, ctx, max_warnings: int):
        """Définir le nombre maximum de warnings"""
        try:
            if max_warnings < 1 or max_warnings > 10:
                return await ctx.send("❌ Le nombre de warnings doit être entre 1 et 10.")
            
            with open("data/server_config.json", "r") as f:
                config = json.load(f)
            
            config["max_warnings"] = max_warnings
            
            with open("data/server_config.json", "w") as f:
                json.dump(config, f, indent=2)
            
            embed = nextcord.Embed(
                title="✅ Max Warnings Défini",
                description=f"**Maximum:** {max_warnings} warnings",
                color=0x2ecc71,
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Défini par {ctx.author.name}")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="toggleantispam")
    @commands.has_permissions(administrator=True)
    async def toggleantispam(self, ctx):
        """Activer/désactiver l'anti-spam"""
        try:
            with open("data/server_config.json", "r") as f:
                config = json.load(f)
            
            config["anti_spam"] = not config.get("anti_spam", True)
            
            with open("data/server_config.json", "w") as f:
                json.dump(config, f, indent=2)
            
            status = "activé" if config["anti_spam"] else "désactivé"
            color = 0x2ecc71 if config["anti_spam"] else 0xe74c3c
            
            embed = nextcord.Embed(
                title=f"✅ Anti-Spam {status.title()}",
                description=f"L'anti-spam est maintenant {status}.",
                color=color,
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Modifié par {ctx.author.name}")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="toggleantiinvite")
    @commands.has_permissions(administrator=True)
    async def toggleantiinvite(self, ctx):
        """Activer/désactiver l'anti-invite"""
        try:
            with open("data/server_config.json", "r") as f:
                config = json.load(f)
            
            config["anti_invite"] = not config.get("anti_invite", True)
            
            with open("data/server_config.json", "w") as f:
                json.dump(config, f, indent=2)
            
            status = "activé" if config["anti_invite"] else "désactivé"
            color = 0x2ecc71 if config["anti_invite"] else 0xe74c3c
            
            embed = nextcord.Embed(
                title=f"✅ Anti-Invite {status.title()}",
                description=f"L'anti-invite est maintenant {status}.",
                color=color,
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Modifié par {ctx.author.name}")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="addcommand")
    @commands.has_permissions(administrator=True)
    async def addcommand(self, ctx, command_name: str, *, response: str):
        """Ajouter une commande personnalisée"""
        try:
            with open("data/server_config.json", "r") as f:
                config = json.load(f)
            
            custom_commands = config.get("custom_commands", {})
            custom_commands[command_name.lower()] = response
            config["custom_commands"] = custom_commands
            
            with open("data/server_config.json", "w") as f:
                json.dump(config, f, indent=2)
            
            embed = nextcord.Embed(
                title="✅ Commande Personnalisée Ajoutée",
                description=f"**Commande:** `{command_name}`\n**Réponse:** {response}",
                color=0x2ecc71,
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Ajoutée par {ctx.author.name}")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="removecommand")
    @commands.has_permissions(administrator=True)
    async def removecommand(self, ctx, command_name: str):
        """Supprimer une commande personnalisée"""
        try:
            with open("data/server_config.json", "r") as f:
                config = json.load(f)
            
            custom_commands = config.get("custom_commands", {})
            
            if command_name.lower() in custom_commands:
                del custom_commands[command_name.lower()]
                config["custom_commands"] = custom_commands
                
                with open("data/server_config.json", "w") as f:
                    json.dump(config, f, indent=2)
                
                embed = nextcord.Embed(
                    title="✅ Commande Personnalisée Supprimée",
                    description=f"**Commande:** `{command_name}`",
                    color=0xe74c3c,
                    timestamp=datetime.datetime.now()
                )
                embed.set_footer(text=f"Supprimée par {ctx.author.name}")
                
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"❌ La commande `{command_name}` n'existe pas.")
                
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="listcommands")
    @commands.has_permissions(administrator=True)
    async def listcommands(self, ctx):
        """Lister les commandes personnalisées"""
        try:
            with open("data/server_config.json", "r") as f:
                config = json.load(f)
            
            custom_commands = config.get("custom_commands", {})
            
            if not custom_commands:
                return await ctx.send("📋 Aucune commande personnalisée.")
            
            embed = nextcord.Embed(
                title="📋 Commandes Personnalisées",
                description=f"**Total:** {len(custom_commands)} commandes",
                color=0x3498db,
                timestamp=datetime.datetime.now()
            )
            
            for cmd_name, response in list(custom_commands.items())[:10]:
                embed.add_field(
                    name=f"`{cmd_name}`",
                    value=response[:50] + "..." if len(response) > 50 else response,
                    inline=False
                )
            
            if len(custom_commands) > 10:
                embed.add_field(
                    name="➕ Plus",
                    value=f"...et {len(custom_commands) - 10} autres",
                    inline=False
                )
            
            embed.set_footer(text=f"Demandé par {ctx.author.name}")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")

def setup(bot):
    bot.add_cog(ServerConfig(bot))
