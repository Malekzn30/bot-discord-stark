import nextcord
from nextcord.ext import commands
import requests
import json
import datetime

class WeatherCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="weather")
    async def weather(self, ctx, *, city: str):
        """Météo d'une ville"""
        try:
            # Simulation de données météo (remplacer par vraie API)
            weather_data = {
                "Paris": {"temp": "18°C", "desc": "Nuageux", "humidity": "65%"},
                "Lyon": {"temp": "16°C", "desc": "Pluvieux", "humidity": "80%"},
                "Marseille": {"temp": "22°C", "desc": "Ensoleillé", "humidity": "55%"},
                "default": {"temp": "20°C", "desc": "Partiellement nuageux", "humidity": "60%"}
            }
            
            data = weather_data.get(city.title(), weather_data["default"])
            
            embed = nextcord.Embed(
                title=f"🌤️ Météo - {city.title()}",
                color=0x3498db,
                timestamp=datetime.datetime.now()
            )
            
            embed.add_field(name="🌡️ Température", value=data["temp"], inline=True)
            embed.add_field(name="☁️ Description", value=data["desc"], inline=True)
            embed.add_field(name="💧 Humidité", value=data["humidity"], inline=True)
            
            embed.set_footer(text=f"Demandé par {ctx.author.name}")
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="urban")
    async def urban(self, ctx, *, term: str):
        """Définition Urban Dictionary"""
        try:
            # Simulation de définitions Urban Dictionary
            definitions = {
                "lol": "Rire fort (laugh out loud)",
                "bruh": "Expression d'étonnement ou de déception",
                "yeet": "Lancer quelque chose avec force",
                "default": f"Définition de '{term}': Terme populaire sur internet"
            }
            
            definition = definitions.get(term.lower(), definitions["default"])
            
            embed = nextcord.Embed(
                title="📚 Urban Dictionary",
                description=f"**{term.title()}**",
                color=0x9B59B6,
                timestamp=datetime.datetime.now()
            )
            
            embed.add_field(name="Définition", value=definition, inline=False)
            embed.add_field(name="👍 Likes", value="🔥🔥🔥", inline=True)
            embed.add_field(name="👎 Dislikes", value="💩", inline=True)
            
            embed.set_footer(text=f"Demandé par {ctx.author.name} • Source: Urban Dictionary")
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")

def setup(bot):
    bot.add_cog(WeatherCommands(bot))
