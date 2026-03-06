import nextcord
from nextcord.ext import commands
import datetime
import random
import asyncio

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}
    
    @commands.command(name="hangman")
    async def hangman(self, ctx):
        """Jeu du pendu"""
        words = ["python", "discord", "bot", "coding", "game", "computer", "programming", "developer"]
        word = random.choice(words).upper()
        guessed = []
        attempts = 6
        
        self.active_games[ctx.channel.id] = {
            'word': word,
            'guessed': guessed,
            'attempts': attempts,
            'author': ctx.author.id
        }
        
        # Afficher le mot avec des underscores
        display = "".join([letter if letter in guessed else "_" for letter in word])
        
        embed = nextcord.Embed(
            title="🎯 Jeu du Pendu",
            description=f"**Mot:** {display}\n**Tentatives restantes:** {attempts}\n**Lettres utilisées:** {', '.join(guessed) if guessed else 'Aucune'}",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Jeu créé par {ctx.author.name} • Envoyez une lettre pour deviner")
        
        await ctx.send(embed=embed)
    
    @commands.command(name="trivia")
    async def trivia(self, ctx):
        """Questions de culture générale"""
        questions = [
            {
                "question": "Quel est le langage de programmation le plus populaire en 2024?",
                "options": ["Python", "JavaScript", "Java", "C++"],
                "answer": 1
            },
            {
                "question": "Combien de planètes dans notre système solaire?",
                "options": ["7", "8", "9", "10"],
                "answer": 1
            },
            {
                "question": "Qui a fondé Microsoft?",
                "options": ["Steve Jobs", "Bill Gates", "Mark Zuckerberg", "Elon Musk"],
                "answer": 1
            }
        ]
        
        q = random.choice(questions)
        
        embed = nextcord.Embed(
            title="🧠 Question Culture G",
            description=f"**Question:** {q['question']}",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        
        for i, option in enumerate(q['options']):
            embed.add_field(name=f"Option {i+1}", value=option, inline=False)
        
        embed.set_footer(text=f"Envoyez le numéro de votre réponse • Demandé par {ctx.author.name}")
        
        await ctx.send(embed=embed)
    
    @commands.command(name="memory")
    async def memory(self, ctx):
        """Jeu de mémoire"""
        emojis = ["🍎", "🍌", "🍇", "🍓", "🍒", "🍑", "🥝", "🍊"]
        sequence = []
        
        # Générer une séquence
        for _ in range(5):
            sequence.append(random.choice(emojis))
        
        embed = nextcord.Embed(
            title="🧠 Jeu de Mémoire",
            description="Mémorisez cette séquence d'emojis!",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="Séquence", value=" ".join(sequence), inline=False)
        embed.set_footer(text=f"Demandé par {ctx.author.name} • La séquence disparaîtra dans 5 secondes")
        
        msg = await ctx.send(embed=embed)
        
        # Attendre 5 secondes puis effacer
        await asyncio.sleep(5)
        
        embed_hidden = nextcord.Embed(
            title="🧠 Jeu de Mémoire",
            description="Maintenant, écrivez la séquence dans le bon ordre!",
            color=0xe74c3c,
            timestamp=datetime.datetime.now()
        )
        embed_hidden.set_footer(text=f"Demandé par {ctx.author.name}")
        
        await msg.edit(embed=embed_hidden)
    
    @commands.command(name="wordchain")
    async def wordchain(self, ctx):
        """Jeu de chaîne de mots"""
        self.active_games[ctx.channel.id] = {
            'last_word': '',
            'used_words': [],
            'author': ctx.author.id
        }
        
        embed = nextcord.Embed(
            title="🔗 Chaîne de Mots",
            description="Le premier mot commence par 'A'. Écrivez un mot qui commence par la dernière lettre du mot précédent!",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Jeu créé par {ctx.author.name}")
        
        await ctx.send(embed=embed)
    
    @commands.command(name="rps")
    async def rps(self, ctx, choice: str = None):
        """Pierre feuille ciseaux"""
        choices = ["pierre", "feuille", "ciseaux", "rock", "paper", "scissors"]
        if not choice or choice.lower() not in choices:
            return await ctx.send("❌ Choisis: pierre, feuille ou ciseaux")
        
        bot_choice = random.choice(["pierre", "feuille", "ciseaux"])
        
        if choice.lower() == bot_choice:
            result = "Égalité!"
        elif (choice.lower() == "pierre" and bot_choice == "ciseaux") or \
             (choice.lower() == "feuille" and bot_choice == "pierre") or \
             (choice.lower() == "ciseaux" and bot_choice == "feuille"):
            result = "Tu gagnes!"
        else:
            result = "Tu perds!"
        
        embed = nextcord.Embed(
            title="🎮 Pierre Feuille Ciseaux",
            description=f"**Ton choix:** {choice.lower()}\n**Bot:** {bot_choice}\n**Résultat:** {result}",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        await ctx.send(embed=embed)

def cleanup_games():
    """Nettoyer les jeux actifs"""
    pass

def setup(bot):
    bot.add_cog(Games(bot))
