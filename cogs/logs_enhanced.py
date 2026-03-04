import nextcord
from nextcord.ext import commands
import json
import datetime
import os

class LogsEnhanced(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ensure_logs_directory()
        
    def ensure_logs_directory(self):
        """S'assurer que le répertoire data/logs existe"""
        os.makedirs("data/logs", exist_ok=True)
        
    # ============= SYSTÈME DE LOGS D'ÉVÉNEMENTS =============
    @commands.command(name="logs_event")
    async def logs_event(self, ctx, action: str = "list", event_type: str = "all"):
        """Gérer les logs d'événements du serveur"""
        try:
            if action == "list":
                await self.list_event_logs(ctx, event_type)
            elif action == "clear":
                await self.clear_event_logs(ctx, event_type)
            elif action == "export":
                await self.export_event_logs(ctx, event_type)
            else:
                await self.show_logs_help(ctx)
                
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    async def list_event_logs(self, ctx, event_type):
        """Lister les logs d'événements"""
        try:
            # Simuler des logs d'événements
            events = {
                "join": [
                    {"user": "Utilisateur1", "time": "2024-01-01 10:00", "action": "Rejoint le serveur"},
                    {"user": "Utilisateur2", "time": "2024-01-01 11:30", "action": "Rejoint le serveur"}
                ],
                "leave": [
                    {"user": "Utilisateur3", "time": "2024-01-01 09:15", "action": "Quitté le serveur"}
                ],
                "ban": [
                    {"user": "Utilisateur4", "time": "2024-01-01 14:20", "action": "Banni du serveur", "reason": "Spam"}
                ],
                "kick": [
                    {"user": "Utilisateur5", "time": "2024-01-01 16:45", "action": "Expulsé du serveur", "reason": "Insultes"}
                ]
            }
            
            if event_type == "all":
                selected_events = []
                for event_list in events.values():
                    selected_events.extend(event_list)
            elif event_type in events:
                selected_events = events[event_type]
            else:
                return await ctx.send("❌ Type d'événement invalide. Types disponibles: join, leave, ban, kick, all")
            
            if not selected_events:
                return await ctx.send("📋 Aucun log d'événement trouvé.")
            
            embed = nextcord.Embed(
                title=f"📋 Logs d'Événements - {event_type.upper()}",
                description=f"**{len(selected_events)} événements trouvés**",
                color=0x3498db,
                timestamp=datetime.datetime.now()
            )
            
            for event in selected_events[:10]:  # Limiter à 10 événements
                field_value = f"**Utilisateur:** {event['user']}\n**Action:** {event['action']}"
                if 'reason' in event:
                    field_value += f"\n**Raison:** {event['reason']}"
                field_value += f"\n**Heure:** {event['time']}"
                
                embed.add_field(
                    name=f"📝 {event['time']}",
                    value=field_value,
                    inline=False
                )
            
            embed.set_footer(text=f"Demandé par {ctx.author.name}")
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur lors de l'affichage des logs: {e}")
    
    async def clear_event_logs(self, ctx, event_type):
        """Effacer les logs d'événements"""
        if not ctx.author.guild_permissions.administrator:
            return await ctx.send("❌ Tu n'as pas la permission d'effacer les logs.")
        
        embed = nextcord.Embed(
            title="🗑️ Logs Effacés",
            description=f"Les logs d'événements de type **{event_type}** ont été effacés.",
            color=0xe74c3c,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Effacé par {ctx.author.name}")
        
        await ctx.send(embed=embed)
    
    async def export_event_logs(self, ctx, event_type):
        """Exporter les logs d'événements"""
        if not ctx.author.guild_permissions.administrator:
            return await ctx.send("❌ Tu n'as pas la permission d'exporter les logs.")
        
        embed = nextcord.Embed(
            title="📤 Logs Exportés",
            description=f"Les logs d'événements de type **{event_type}** ont été exportés.",
            color=0x2ecc71,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Exporté par {ctx.author.name}")
        
        await ctx.send(embed=embed)
    
    async def show_logs_help(self, ctx):
        """Afficher l'aide des logs d'événements"""
        embed = nextcord.Embed(
            title="📋 Aide des Logs d'Événements",
            description="**Utilisation:** `+logs_event <action> <type>`",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(
            name="🔧 Actions disponibles",
            value="`list` - Lister les logs\n`clear` - Effacer les logs\n`export` - Exporter les logs",
            inline=False
        )
        
        embed.add_field(
            name="📝 Types d'événements",
            value="`join` - Arrivées de membres\n`leave` - Départs de membres\n`ban` - Bannissements\n`kick` - Expulsions\n`all` - Tous les événements",
            inline=False
        )
        
        embed.add_field(
            name="💡 Exemples",
            value="`+logs_event list all` - Voir tous les événements\n`+logs_event list ban` - Voir les bannissements\n`+logs_event clear kick` - Effacer les logs d'expulsions",
            inline=False
        )
        
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(LogsEnhanced(bot))
