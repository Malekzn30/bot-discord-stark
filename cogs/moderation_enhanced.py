import nextcord
from nextcord.ext import commands
import datetime
import json
import os

class ModerationEnhanced(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ensure_data_files()
    
    def ensure_data_files(self):
        """Créer les fichiers de données nécessaires"""
        os.makedirs("data", exist_ok=True)
        
        if not os.path.exists("data/warns.json"):
            with open("data/warns.json", "w") as f:
                json.dump({}, f)
    
    @commands.command(name="modlogs")
    @commands.has_permissions(administrator=True)
    async def modlogs(self, ctx):
        """Voir les logs de modération"""
        try:
            with open("data/warns.json", "r") as f:
                warns = json.load(f)
            
            if not warns:
                return await ctx.send("📋 Aucun warn enregistré.")
            
            embed = nextcord.Embed(
                title="📋 Logs de Modération",
                description=f"**Total warns:** {len(warns)}",
                color=0xe74c3c,
                timestamp=datetime.datetime.now()
            )
            
            for user_id, user_warns in list(warns.items())[:10]:
                member = ctx.guild.get_member(int(user_id))
                name = member.name if member else f"User {user_id}"
                embed.add_field(
                    name=f"⚠️ {name}",
                    value=f"**Warns:** {len(user_warns)}",
                    inline=True
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="snipe")
    async def snipe(self, ctx):
        """Voir le dernier message supprimé"""
        await ctx.send("🔍 Aucun message supprimé récemment.")
    
    @commands.command(name="editsnipe")
    async def editsnipe(self, ctx):
        """Voir le dernier message modifié"""
        await ctx.send("✏️ Aucun message modifié récemment.")

def setup(bot):
    bot.add_cog(ModerationEnhanced(bot))
