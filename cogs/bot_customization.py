import nextcord
from nextcord.ext import commands
import datetime
import json
import os

class BotCustomization(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ensure_data_files()
    
    def ensure_data_files(self):
        """Créer les fichiers de données nécessaires"""
        os.makedirs("data", exist_ok=True)
        
        if not os.path.exists("data/bot_config.json"):
            with open("data/bot_config.json", "w") as f:
                json.dump({
                    "prefix": "+",
                    "welcome_message": "Bienvenue sur le serveur!",
                    "leave_message": "Au revoir!",
                    "status": "En ligne",
                    "activity": "Joue à Discord"
                }, f, indent=2)
    
    @commands.command(name="setprefix")
    @commands.has_permissions(administrator=True)
    async def setprefix(self, ctx, prefix: str):
        """Changer le préfixe du bot"""
        try:
            with open("data/bot_config.json", "r") as f:
                config = json.load(f)
            
            old_prefix = config["prefix"]
            config["prefix"] = prefix
            
            with open("data/bot_config.json", "w") as f:
                json.dump(config, f, indent=2)
            
            embed = nextcord.Embed(
                title="✅ Préfixe Changé",
                description=f"**Ancien préfixe:** `{old_prefix}`\n**Nouveau préfixe:** `{prefix}`",
                color=0x2ecc71,
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Changé par {ctx.author.name}")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="setstatus")
    @commands.has_permissions(administrator=True)
    async def setstatus(self, ctx, status: str):
        """Changer le statut du bot"""
        try:
            with open("data/bot_config.json", "r") as f:
                config = json.load(f)
            
            config["status"] = status
            
            with open("data/bot_config.json", "w") as f:
                json.dump(config, f, indent=2)
            
            # Mettre à jour le statut du bot
            await self.bot.change_presence(
                activity=nextcord.Activity(
                    type=nextcord.ActivityType.custom,
                    name=status
                )
            )
            
            embed = nextcord.Embed(
                title="✅ Statut Changé",
                description=f"**Nouveau statut:** {status}",
                color=0x2ecc71,
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Changé par {ctx.author.name}")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="setactivity")
    @commands.has_permissions(administrator=True)
    async def setactivity(self, ctx, activity_type: str, *, activity_name: str):
        """Changer l'activité du bot"""
        try:
            activity_types = {
                "playing": nextcord.ActivityType.playing,
                "streaming": nextcord.ActivityType.streaming,
                "listening": nextcord.ActivityType.listening,
                "watching": nextcord.ActivityType.watching,
                "competing": nextcord.ActivityType.competing
            }
            
            if activity_type.lower() not in activity_types:
                return await ctx.send("❌ Types disponibles: playing, streaming, listening, watching, competing")
            
            with open("data/bot_config.json", "r") as f:
                config = json.load(f)
            
            config["activity"] = f"{activity_type} {activity_name}"
            
            with open("data/bot_config.json", "w") as f:
                json.dump(config, f, indent=2)
            
            # Mettre à jour l'activité
            activity = nextcord.Activity(
                type=activity_types[activity_type.lower()],
                name=activity_name
            )
            await self.bot.change_presence(activity=activity)
            
            embed = nextcord.Embed(
                title="✅ Activité Changée",
                description=f"**Type:** {activity_type}\n**Nom:** {activity_name}",
                color=0x2ecc71,
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Changé par {ctx.author.name}")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="setwelcome")
    @commands.has_permissions(manage_guild=True)
    async def setwelcome(self, ctx, *, message: str):
        """Définir le message de bienvenue"""
        try:
            with open("data/bot_config.json", "r") as f:
                config = json.load(f)
            
            config["welcome_message"] = message
            
            with open("data/bot_config.json", "w") as f:
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
    
    @commands.command(name="setleave")
    @commands.has_permissions(manage_guild=True)
    async def setleave(self, ctx, *, message: str):
        """Définir le message de départ"""
        try:
            with open("data/bot_config.json", "r") as f:
                config = json.load(f)
            
            config["leave_message"] = message
            
            with open("data/bot_config.json", "w") as f:
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
    
    @commands.command(name="config")
    @commands.has_permissions(administrator=True)
    async def config(self, ctx):
        """Voir la configuration actuelle du bot"""
        try:
            with open("data/bot_config.json", "r") as f:
                config = json.load(f)
            
            embed = nextcord.Embed(
                title="⚙️ Configuration du Bot",
                description="Configuration actuelle:",
                color=0x3498db,
                timestamp=datetime.datetime.now()
            )
            
            embed.add_field(name="🔧 Préfixe", value=f"`{config.get('prefix', '+')}`", inline=True)
            embed.add_field(name="📝 Message Bienvenue", value=config.get('welcome_message', 'Non défini'), inline=True)
            embed.add_field(name="📝 Message Départ", value=config.get('leave_message', 'Non défini'), inline=True)
            embed.add_field(name="📊 Statut", value=config.get('status', 'Non défini'), inline=True)
            embed.add_field(name="🎮 Activité", value=config.get('activity', 'Non défini'), inline=True)
            
            embed.set_footer(text=f"Demandé par {ctx.author.name}")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="resetconfig")
    @commands.has_permissions(administrator=True)
    async def resetconfig(self, ctx):
        """Réinitialiser la configuration du bot"""
        try:
            default_config = {
                "prefix": "+",
                "welcome_message": "Bienvenue sur le serveur!",
                "leave_message": "Au revoir!",
                "status": "En ligne",
                "activity": "Joue à Discord"
            }
            
            with open("data/bot_config.json", "w") as f:
                json.dump(default_config, f, indent=2)
            
            embed = nextcord.Embed(
                title="🔄 Configuration Réinitialisée",
                description="La configuration du bot a été réinitialisée aux valeurs par défaut.",
                color=0xf39c12,
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Réinitialisé par {ctx.author.name}")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")

def setup(bot):
    bot.add_cog(BotCustomization(bot))
