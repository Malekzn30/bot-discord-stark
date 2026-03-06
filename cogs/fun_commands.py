import nextcord
from nextcord.ext import commands
import datetime
import random
import requests

class FunCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="meme")
    async def meme(self, ctx, category: str = "random"):
        """Afficher un mème aléatoire"""
        memes = {
            "random": [
                "Quand tu codes à 3h du matin... 😴",
                "Moi qui essaie de déboguer... 🐛",
                "Quand le bot fonctionne enfin... 🎉",
                "Les erreurs qui n'existent que pour toi... 🤔"
            ],
            "coding": [
                "Hello World! 👋",
                "404: Brain not found 🧠",
                "It works on my machine 💻",
                "Have you tried turning it off and on again? 🔄"
            ]
        }
        
        meme_list = memes.get(category.lower(), memes["random"])
        meme_text = random.choice(meme_list)
        
        embed = nextcord.Embed(
            title="😂 Mème Aléatoire",
            description=meme_text,
            color=0xf39c12,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        
        await ctx.send(embed=embed)
    
    @commands.command(name="joke")
    async def joke(self, ctx):
        """Blague aléatoire"""
        jokes = [
            "Pourquoi les développeurs portent-ils des lunettes ?\nParce qu'ils ne voient pas bien le C# ! 👓",
            "Quel est le langage préféré des magiciens ?\nPython, parce qu'il fait des tours ! 🐍✨",
            "Combien de développeurs faut-il pour changer une ampoule ?\nAucun, c'est un problème matériel ! 💡",
            "Pourquoi les bot Discord sont-ils toujours fatigués ?\nParce qu'ils font des nuits blanches à répondre aux commandes ! 🤖😴"
        ]
        
        joke_text = random.choice(jokes)
        
        embed = nextcord.Embed(
            title="😂 Blague Aléatoire",
            description=joke_text,
            color=0xf39c12,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        
        await ctx.send(embed=embed)
    
    @commands.command(name="fact")
    async def fact(self, ctx):
        """Fait intéressant aléatoire"""
        facts = [
            "🐙 Les pieuvres ont trois cœurs et du sang bleu!",
            "🍯 Le miel ne périt jamais. On peut en manger des milliers d'années plus tard!",
            "🌍 Il y a plus d'étoiles dans l'univers que de grains de sable sur Terre!",
            "🦒 Un girafe peut nettoyer ses oreilles avec sa langue!",
            "⚡ Un éclair est 5 fois plus chaud que la surface du soleil!",
            "🐧 Les manchots proposent des cailloux comme cadeaux pour séduire!",
            "🍃 Le bambou peut pousser de 90cm en une seule journée!",
            "🌈 Un arc-en-ciel est en fait un cercle complet!"
        ]
        
        fact_text = random.choice(facts)
        
        embed = nextcord.Embed(
            title="🧠 Fait Intéressant",
            description=fact_text,
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        
        await ctx.send(embed=embed)
    
    @commands.command(name="quote")
    async def quote(self, ctx):
        """Citation inspirante"""
        quotes = [
            "🚀 'Le seul moyen de faire du bon travail est d'aimer ce que vous faites.' - Steve Jobs",
            "💡 'L'imagination est plus importante que le savoir.' - Albert Einstein",
            "⭐ 'Soyez vous-même; tous les autres sont déjà pris.' - Oscar Wilde",
            "🎯 'Le succès est la somme de petits efforts répétés jour après jour.' - Robert Collier",
            "🌟 'La seule limite à notre accomplissement de demain sera nos doutes d'aujourd'hui.' - Franklin D. Roosevelt",
            "💪 'N'attendez pas. Le moment ne sera jamais juste.' - Napoleon Hill",
            "🎨 'La créativité demande courage.' - Henri Matisse",
            "🔥 'Le meilleur moment pour planter un arbre était il y a 20 ans. Le deuxième meilleur moment est maintenant.' - Proverbe chinois"
        ]
        
        quote_text = random.choice(quotes)
        
        embed = nextcord.Embed(
            title="💭 Citation du Jour",
            description=quote_text,
            color=0x9B59B6,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        
        await ctx.send(embed=embed)
    
    @commands.command(name="roll")
    async def roll(self, ctx, sides: int = 6):
        """Lancer un dé avec le nombre de faces spécifié"""
        if sides < 2 or sides > 100:
            return await ctx.send("❌ Le dé doit avoir entre 2 et 100 faces.")
        
        result = random.randint(1, sides)
        
        embed = nextcord.Embed(
            title="🎲 Lancer de Dé",
            description=f"**Dé à {sides} faces**\n**Résultat:** {result}",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Lancé par {ctx.author.name}")
        
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(FunCommands(bot))
