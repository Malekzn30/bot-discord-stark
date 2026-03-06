import nextcord
from nextcord.ext import commands
import datetime
import json
import os

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ensure_data_files()
    
    def ensure_data_files(self):
        """Créer les fichiers de données nécessaires"""
        os.makedirs("data/logs", exist_ok=True)
        
        if not os.path.exists("data/logs/server_logs.json"):
            with open("data/logs/server_logs.json", "w") as f:
                json.dump([], f)
        
        if not os.path.exists("data/logs/mod_logs.json"):
            with open("data/logs/mod_logs.json", "w") as f:
                json.dump([], f)
    
    @commands.command(name="logs")
    @commands.has_permissions(administrator=True)
    async def logs(self, ctx, log_type: str = "server", limit: int = 10):
        """Voir les logs du serveur"""
        try:
            if log_type.lower() == "server":
                file_path = "data/logs/server_logs.json"
                title = "📋 Logs Serveur"
            elif log_type.lower() == "mod":
                file_path = "data/logs/mod_logs.json"
                title = "🛡️ Logs Modération"
            else:
                return await ctx.send("❌ Types disponibles: `server`, `mod`")
            
            with open(file_path, "r") as f:
                logs = json.load(f)
            
            if not logs:
                return await ctx.send("📋 Aucun log trouvé.")
            
            # Prendre les logs les plus récents
            recent_logs = logs[-limit:] if len(logs) > limit else logs
            
            embed = nextcord.Embed(
                title=title,
                description=f"**Type:** {log_type}\n**Total:** {len(recent_logs)} logs affichés",
                color=0x3498db,
                timestamp=datetime.datetime.now()
            )
            
            for log in recent_logs:
                timestamp = datetime.datetime.fromisoformat(log["timestamp"]).strftime("%H:%M:%S")
                embed.add_field(
                    name=f"[{timestamp}] {log['type'].upper()}",
                    value=f"**{log['action']}**\n*{log['description']}*",
                    inline=False
                )
            
            embed.set_footer(text=f"Demandé par {ctx.author.name}")
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="clearlogs")
    @commands.has_permissions(administrator=True)
    async def clearlogs(self, ctx, log_type: str = "all"):
        """Vider les logs"""
        try:
            if log_type.lower() == "server":
                with open("data/logs/server_logs.json", "w") as f:
                    json.dump([], f)
                await ctx.send("🗑️ Logs serveur vidés avec succès.")
                
            elif log_type.lower() == "mod":
                with open("data/logs/mod_logs.json", "w") as f:
                    json.dump([], f)
                await ctx.send("🗑️ Logs modération vidés avec succès.")
                
            elif log_type.lower() == "all":
                with open("data/logs/server_logs.json", "w") as f:
                    json.dump([], f)
                with open("data/logs/mod_logs.json", "w") as f:
                    json.dump([], f)
                await ctx.send("🗑️ Tous les logs vidés avec succès.")
                
            else:
                await ctx.send("❌ Options: `server`, `mod`, `all`")
                
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="exportlogs")
    @commands.has_permissions(administrator=True)
    async def exportlogs(self, ctx):
        """Exporter les logs dans un fichier"""
        try:
            # Lire tous les logs
            with open("data/logs/server_logs.json", "r") as f:
                server_logs = json.load(f)
            
            with open("data/logs/mod_logs.json", "r") as f:
                mod_logs = json.load(f)
            
            # Créer le contenu exporté
            export_content = {
                "export_date": datetime.datetime.now().isoformat(),
                "exported_by": ctx.author.id,
                "server_logs": server_logs,
                "mod_logs": mod_logs
            }
            
            # Sauvegarder dans un fichier
            export_file = f"data/logs/export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(export_file, "w") as f:
                json.dump(export_content, f, indent=2)
            
            embed = nextcord.Embed(
                title="📤 Logs Exportés",
                description=f"**Fichier:** {export_file}\n**Logs serveur:** {len(server_logs)}\n**Logs modération:** {len(mod_logs)}",
                color=0x2ecc71,
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Exporté par {ctx.author.name}")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="logchannel")
    @commands.has_permissions(administrator=True)
    async def logchannel(self, ctx, action: str = "set", channel: nextcord.TextChannel = None):
        """Définir le canal de logs"""
        try:
            if action.lower() == "set":
                target_channel = channel or ctx.channel
                
                with open("data/bot_config.json", "r") as f:
                    config = json.load(f)
                
                config["log_channel"] = target_channel.id
                
                with open("data/bot_config.json", "w") as f:
                    json.dump(config, f, indent=2)
                
                embed = nextcord.Embed(
                    title="✅ Canal de Logs Défini",
                    description=f"**Canal:** {target_channel.mention}",
                    color=0x2ecc71,
                    timestamp=datetime.datetime.now()
                )
                embed.set_footer(text=f"Défini par {ctx.author.name}")
                
                await ctx.send(embed=embed)
                
            elif action.lower() == "remove":
                with open("data/bot_config.json", "r") as f:
                    config = json.load(f)
                
                config.pop("log_channel", None)
                
                with open("data/bot_config.json", "w") as f:
                    json.dump(config, f, indent=2)
                
                await ctx.send("✅ Canal de logs supprimé.")
                
            else:
                await ctx.send("❌ Actions: `set`, `remove`")
                
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    def log_event(self, event_type: str, action: str, description: str, guild_id: int):
        """Ajouter un événement aux logs"""
        try:
            log_entry = {
                "timestamp": datetime.datetime.now().isoformat(),
                "type": event_type,
                "action": action,
                "description": description,
                "guild_id": guild_id
            }
            
            # Déterminer le fichier de logs
            if event_type in ["warn", "kick", "ban", "mute", "unmute"]:
                file_path = "data/logs/mod_logs.json"
            else:
                file_path = "data/logs/server_logs.json"
            
            with open(file_path, "r") as f:
                logs = json.load(f)
            
            logs.append(log_entry)
            
            # Garder seulement les 1000 derniers logs
            if len(logs) > 1000:
                logs = logs[-1000:]
            
            with open(file_path, "w") as f:
                json.dump(logs, f, indent=2)
                
        except Exception as e:
            print(f"Erreur ajout log: {e}")

def setup(bot):
    bot.add_cog(Logs(bot))
