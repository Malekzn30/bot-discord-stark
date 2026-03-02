import nextcord
from nextcord.ext import commands
import asyncio
import random
import datetime
import aiohttp
import io

class FunCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.truth_or_dare_data = {}
        self.would_you_rather_data = {}
    
    # ============= JEUX AMUSANTS =============
    @commands.command(name="8ball")
    async def eight_ball(self, ctx, *, question: str):
        """Boule magique 8"""
        responses = [
            "✅ Oui, absolument !",
            "✅ Oui",
            "🤔 Probablement",
            "🤷‍♂️ Je ne sais pas",
            "❌ Probablement pas",
            "❌ Non",
            "❌ Absolument pas !",
            "🔮 Demande plus tard",
            "💭 Concentre-toi et demande encore"
        ]
        
        embed = nextcord.Embed(
            title="🔮 Boule Magique 8",
            description=f"**Question:** {question}\n\n**Réponse:** {random.choice(responses)}",
            color=0x9B59B6,
            timestamp=datetime.datetime.now()
        )
        
        embed.set_thumbnail(url="https://i.imgur.com/8bVrGdF.png")
        await ctx.send(embed=embed)
    
    @commands.command(name="truth")
    async def truth(self, ctx, category: str = "normal"):
        """Question pour vérité"""
        categories = {
            "normal": [
                "Quelle est ta plus grande peur ?",
                "Quel est ton souvenir le plus embarrassant ?",
                "As-tu déjà menti à tes parents ?",
                "Quelle est la chose la plus stupide que tu aies faite ?",
                "De quoi as-tu le plus honte ?"
            ],
            "spicy": [
                "Quel est ton secret le plus sombre ?",
                "As-tu déjà triché ?",
                "Quelle est la chose la plus folle que tu as faite ?",
                "De quoi as-tu le plus honte en ce moment ?",
                "Quel est ton plus grand regret ?"
            ],
            "friendship": [
                "Qui est ton meilleur ami et pourquoi ?",
                "As-tu déjà parlé derrière le dos d'un ami ?",
                "Quelle est la qualité que tu admires le plus chez tes amis ?",
                "As-tu déjà perdu un ami ? Pourquoi ?",
                "Que ferais-tu si ton meilleur ami était en danger ?"
            ]
        }
        
        if category not in categories:
            category = "normal"
        
        question = random.choice(categories[category])
        
        embed = nextcord.Embed(
            title="🎭 VÉRITÉ",
            description=f"**Catégorie:** {category.title()}\n\n**Question:** {question}",
            color=0xE74C3C
        )
        
        embed.set_footer(text="Réponds honnêtement !")
        await ctx.send(embed=embed)
    
    @commands.command(name="dare")
    async def dare(self, ctx, intensity: str = "normal"):
        """Action pour un défi"""
        intensities = {
            "easy": [
                "Fais une danse stupide pendant 10 secondes",
                "Envoie un emoji aléatoire à 5 personnes différentes",
                "Change ton pseudo en 'Je suis un champion' pendant 1 heure",
                "Fais un compliment à 3 personnes différentes",
                "Chante une chanson dans le salon vocal"
            ],
            "normal": [
                "Poste une photo de ton visage sans filtre",
                "Fais 10 pompes et enregistre-le",
                "Change ta photo de profil en quelque chose d'embarrassant",
                "Envoie un message 'Je suis le meilleur' à 10 personnes",
                "Fais une imitation de quelqu'un dans le serveur"
            ],
            "hard": [
                "Supprime ton dernier message et dis pourquoi",
                "Fais une confession embarrassante dans le salon général",
                "Change ton pseudo en quelque chose d'humiliant pendant 24h",
                "Envoie un message vocal en chantant mal",
                "Fais un défi proposé par le serveur"
            ]
        }
        
        if intensity not in intensities:
            intensity = "normal"
        
        dare = random.choice(intensities[intensity])
        
        embed = nextcord.Embed(
            title="🎯 DÉFI",
            description=f"**Intensité:** {intensity.title()}\n\n**Défi:** {dare}",
            color=0xF39C12
        )
        
        embed.set_footer(text="Bon courage ! 💪")
        await ctx.send(embed=embed)
    
    @commands.command(name="wyr")
    async def would_you_rather(self, ctx):
        """Préfères-tu (Would You Rather)"""
        questions = [
            ("Perdre ton téléphone pour 1 mois", "Perdre internet pour 1 mois"),
            ("Vivre sans musique", "Vivre sans films"),
            ("Avoir le pouvoir de voler", "Avoir le pouvoir de lire dans les pensées"),
            ("Être invisible", "Pouvoir se téléporter"),
            ("Vivre 100 ans en bonne santé", "Vivre 50 ans avec 1 million d'euros"),
            ("Ne jamais pouvoir mentir", "Ne jamais pouvoir dire la vérité"),
            ("Avoir 3 amis proches", "Avoir 100 connaissances"),
            ("Voir le futur", "Changer le passé"),
            ("Être le plus intelligent", "Être le plus drôle"),
            ("Avoir un temps parfait", "Avoir une mémoire parfaite")
        ]
        
        option1, option2 = random.choice(questions)
        
        embed = nextcord.Embed(
            title="🤔 PRÉFÈRERAIT-TU",
            description=f"**🅰️** {option1}\n\n**🅱️** {option2}",
            color=0x3498db
        )
        
        message = await ctx.send(embed=embed)
        await message.add_reaction("🅰️")
        await message.add_reaction("🅱️")
    
    @commands.command(name="rate")
    async def rate(self, ctx, *, thing: str = None):
        """Noter quelque chose"""
        if not thing:
            thing = ctx.author.display_name
        
        rating = random.randint(1, 10)
        
        # Étoiles visuelles
        stars = "⭐" * rating + "☆" * (10 - rating)
        
        embed = nextcord.Embed(
            title="⭐ NOTATION",
            description=f"**Je note {thing}**\n\n{stars} **{rating}/10**",
            color=0xFFD700
        )
        
        if thing == ctx.author.display_name:
            embed.set_footer(text="Tu es génial ! 😊")
        
        await ctx.send(embed=embed)
    
    @commands.command(name="ship")
    async def ship(self, ctx, user1: nextcord.Member = None, user2: nextcord.Member = None):
        """Calculer le 'ship' entre deux utilisateurs"""
        if not user1:
            user1 = ctx.author
        if not user2:
            user2 = random.choice([m for m in ctx.guild.members if not m.bot and m.id != ctx.author.id])
        
        # Calculer le pourcentage de compatibilité
        compatibility = random.randint(0, 100)
        
        # Générer un nom de ship
        name1 = user1.display_name[:len(user1.display_name)//2]
        name2 = user2.display_name[len(user2.display_name)//2:]
        ship_name = name1 + name2
        
        # Cœur selon la compatibilité
        if compatibility >= 80:
            heart = "💕"
            comment = "Amour fou !"
        elif compatibility >= 60:
            heart = "💖"
            comment = "Très compatible !"
        elif compatibility >= 40:
            heart = "💝"
            comment = "Compatible..."
        else:
            heart = "💔"
            comment = "Pas compatible du tout"
        
        embed = nextcord.Embed(
            title="💝 SHIP CALCULATOR",
            description=f"{user1.mention} + {user2.mention} = **{ship_name}**",
            color=0xFF69B4
        )
        
        embed.add_field(
            name="💕 Compatibilité",
            value=f"**{compatibility}%** {heart}\n{comment}",
            inline=False
        )
        
        embed.set_thumbnail(url="https://i.imgur.com/3ZQhQ6U.png")
        await ctx.send(embed=embed)
    
    # ============= COMMANDES D'AMUSEMENT =============
    @commands.command(name="meme")
    async def meme(self, ctx, category: str = "random"):
        """Afficher un mème aléatoire"""
        # Simulation de mèmes (à remplacer par une vraie API)
        memes = {
            "random": [
                "Quand tu comprends enfin la blague 5 minutes plus tard",
                "Moi: Je vais faire du sport\nMon cerveau:",
                "Quand le prof dit 'c'est facile'",
                "Mon budget après avoir payé les factures",
                "Quand ma mère me demande de faire mes devoirs"
            ],
            "programming": [
                "99 petits bugs dans le code, 99 petits bugs...\nPrends-en un, compile-le, 101 petits bugs dans le code",
                "Ça marche sur ma machine !",
                "Ce n'est pas un bug, c'est une fonctionnalité",
                "Stack Overflow est mon meilleur ami",
                "Hello World, et c'est tout"
            ],
            "gaming": [
                "Quand tu meurs juste avant le boss",
                "Le lag dans les jeux en ligne",
                "Quand ton équipe te lâche",
                "Le RNG dans les jeux",
                "Quand tu gagnes après 100 tentatives"
            ]
        }
        
        if category not in memes:
            category = "random"
        
        meme_text = random.choice(memes[category])
        
        embed = nextcord.Embed(
            title="😂 MÈME",
            description=meme_text,
            color=0x3498db
        )
        
        embed.set_footer(text=f"Catégorie: {category}")
        embed.set_image(url="https://i.imgur.com/meme.jpg")  # Image placeholder
        
        await ctx.send(embed=embed)
    
    @commands.command(name="joke")
    async def joke(self, ctx):
        """Raconter une blague"""
        jokes = [
            ("Pourquoi les plongeurs plongent-ils toujours en arrière et jamais en avant ?", "Parce que sinon ils tombent dans l'eau !"),
            ("Quel est le comble pour un électricien ?", "De ne pas être au courant !"),
            ("Que dit une pomme de terre à une autre ?", "Je suis fâchée, je vais faire la patate !"),
            ("Pourquoi les poissons n'aiment-ils pas l'ordinateur ?", "Parce qu'ils ont peur de la souris !"),
            ("Quel est le comble pour un avocat ?", "De perdre sa cause !"),
            ("Pourquoi les fantômes sont-ils mauvais en maths ?", "Parce qu'ils ont peur des problèmes !"),
            ("Que fait un crocodile quand il mange ?", "Croc-croc !"),
            ("Pourquoi les livres sont-ils toujours fatigués ?", "Parce qu'ils ont trop de pages !"),
            ("Quel est le comble pour un chasseur ?", "De tirer sur la police !"),
            ("Pourquoi les chats n'aiment-ils pas l'eau ?", "Parce qu'ils ont peur des poissons !")
        ]
        
        setup, punchline = random.choice(jokes)
        
        embed = nextcord.Embed(
            title="😄 BLAGUE",
            description=f"**{setup}**\n\n||{punchline}||",
            color=0xF39C12
        )
        
        embed.set_footer(text="Clique pour voir la réponse !")
        await ctx.send(embed=embed)
    
    @commands.command(name="fact")
    async def fact(self, ctx):
        """Donner un fait intéressant"""
        facts = [
            "Les humains partagent 50% de leur ADN avec les bananes.",
            "Le cœur d'une crevette est dans sa tête.",
            "Il y a plus d'étoiles dans l'univers que de grains de sable sur Terre.",
            "Un jour sur Vénus dure plus longtemps qu'une année sur Vénus.",
            "Les méduses n'ont pas de cerveau ni de cœur.",
            "Les pieuvres ont trois cœurs et du sang bleu.",
            "Les otaries dorment en tenant leurs mains pour ne pas se séparer.",
            "Les éléphants sont les seuls animaux qui ne peuvent pas sauter.",
            "Le silence de l'espace est dû à l'absence de molécules pour transporter le son.",
            "Les humains sont la seule espèce qui pleure de joie.",
            "Le papillon de nuit le plus rapide peut voler à 60 km/h.",
            "Le plus grand organisme vivant sur Terre est un champignon.",
            "Les dauphins ont des noms individuels et s'appellent entre eux.",
            "Les fourmis peuvent soulever jusqu'à 50 fois leur poids corporel."
        ]
        
        fact = random.choice(facts)
        
        embed = nextcord.Embed(
            title="🧠 FAIT INTÉRESSANT",
            description=fact,
            color=0x3498db
        )
        
        embed.set_thumbnail(url="https://i.imgur.com/fact.png")
        await ctx.send(embed=embed)
    
    @commands.command(name="quote")
    async def quote(self, ctx, user: nextcord.Member = None):
        """Citer un utilisateur"""
        if not user:
            user = ctx.author
        
        # Récupérer les messages récents de l'utilisateur
        messages = []
        async for msg in ctx.channel.history(limit=100):
            if msg.author == user and not msg.content.startswith(('+', '!', '/')):
                messages.append(msg)
                if len(messages) >= 5:
                    break
        
        if not messages:
            return await ctx.send("❌ Aucun message trouvé à citer.")
        
        quote_msg = random.choice(messages)
        
        embed = nextcord.Embed(
            title="💬 CITATION",
            description=quote_msg.content,
            color=user.color,
            timestamp=quote_msg.created_at
        )
        
        embed.set_author(
            name=user.display_name,
            icon_url=user.display_avatar.url
        )
        
        embed.set_footer(
            text=f"Cité par {ctx.author.name} | #{ctx.channel.name}"
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="reverse")
    async def reverse(self, ctx, *, text: str):
        """Inverser un texte"""
        reversed_text = text[::-1]
        
        embed = nextcord.Embed(
            title="🔄 TEXTE INVERSÉ",
            description=f"**Original:** {text}\n\n**Inversé:** {reversed_text}",
            color=0x9B59B6
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="clap")
    async def clap(self, ctx, *, text: str):
        """Ajouter des applause entre les mots"""
        clapped_text = " 👏 ".join(text.split())
        
        embed = nextcord.Embed(
            title="👏 TEXTE APPLAUDI",
            description=clapped_text,
            color=0xFFD700
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="uwu")
    async def uwu(self, ctx, *, text: str):
        """Transformer un texte en uwu"""
        uwu_text = text.replace('r', 'w').replace('l', 'w').replace('R', 'W').replace('L', 'W')
        uwu_text = uwu_text.replace('th', 'd').replace('Th', 'D')
        
        # Ajouter quelques expressions uwu
        uwu_text += " " + random.choice(['uwu', 'owo', '>w<', '😊', '💕'])
        
        embed = nextcord.Embed(
            title="💖 UWU-IFICATION",
            description=uwu_text,
            color=0xFF69B4
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="ascii")
    async def ascii_art(self, ctx, *, text: str):
        """Créer de l'art ASCII"""
        # Art ASCII simple
        ascii_dict = {
            'A': '  /\  \n /  \n/~~\\\n   \n   \n',
            'B': '||~~\n|  |\n||~~\n|  |\n||~~\n',
            'C': ' ~~\n|  \n|  \n|  \n ~~\n',
            'H': '|  |\n|  |\n|~~|\n|  |\n|  |\n',
            'I': '|||\n| |\n| |\n| |\n|||\n',
            'O': ' ~~\n|  |\n|  |\n|  |\n ~~\n',
            'U': '|  |\n|  |\n|  |\n \\ /\n  \\/\n'
        }
        
        result = ""
        for char in text.upper():
            if char in ascii_dict:
                result += ascii_dict[char]
            else:
                result += char + "\n"
        
        if len(result) > 1900:  # Limite Discord
            result = result[:1900] + "..."
        
        await ctx.send(f"```\n{result}\n```")
    
    @commands.command(name="emojify")
    async def emojify(self, ctx, *, text: str):
        """Transformer un texte en émojis"""
        emoji_dict = {
            'a': '🅰️', 'b': '🅱️', 'c': '🅲️', 'd': '🅳️', 'e': '🅴️',
            'f': '🅵️', 'g': '🅶️', 'h': '🅷️', 'i': '🅸️', 'j': '🅹️',
            'k': '🅺️', 'l': '🅻️', 'm': '🅼️', 'n': '🅽️', 'o': '🅾️',
            'p': '🅿️', 'q': '🆀️', 'r': '🆁️', 's': '🆂️', 't': '🆃️',
            'u': '🆄️', 'v': '🆅️', 'w': '🆆️', 'x': '🆇️', 'y': '🆈️',
            'z': '🆉️', '0': '0️⃣', '1': '1️⃣', '2': '2️⃣', '3': '3️⃣',
            '4': '4️⃣', '5': '5️⃣', '6': '6️⃣', '7': '7️⃣', '8': '8️⃣',
            '9': '9️⃣', '!': '❗', '?': '❓', ' ': '   '
        }
        
        emojified = ""
        for char in text.lower():
            if char in emoji_dict:
                emojified += emoji_dict[char]
            else:
                emojified += char
        
        if len(emojified) > 2000:
            emojified = emojified[:2000] + "..."
        
        await ctx.send(emojified)

def setup(bot):
    bot.add_cog(FunCommands(bot))
