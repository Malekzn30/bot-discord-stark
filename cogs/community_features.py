import nextcord
from nextcord.ext import commands
import datetime
import json
import os

class CommunityFeatures(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ensure_data_files()
    
    def ensure_data_files(self):
        """Créer les fichiers de données nécessaires"""
        os.makedirs("data", exist_ok=True)
        
        if not os.path.exists("data/suggestions.json"):
            with open("data/suggestions.json", "w") as f:
                json.dump([], f)
        
        if not os.path.exists("data/polls.json"):
            with open("data/polls.json", "w") as f:
                json.dump({}, f)
    
    @commands.command(name="suggest")
    async def suggest(self, ctx, *, suggestion: str):
        """Faire une suggestion pour le serveur"""
        try:
            with open("data/suggestions.json", "r") as f:
                suggestions = json.load(f)
            
            new_suggestion = {
                "id": len(suggestions) + 1,
                "author": ctx.author.id,
                "author_name": ctx.author.name,
                "content": suggestion,
                "timestamp": datetime.datetime.now().isoformat(),
                "status": "pending"
            }
            
            suggestions.append(new_suggestion)
            
            with open("data/suggestions.json", "w") as f:
                json.dump(suggestions, f, indent=2)
            
            embed = nextcord.Embed(
                title="💡 Suggestion Soumise",
                description=f"**Suggestion #{new_suggestion['id']}**\n\n{suggestion}",
                color=0x3498db,
                timestamp=datetime.datetime.now()
            )
            embed.add_field(name="👤 Auteur", value=ctx.author.mention, inline=True)
            embed.add_field(name="📊 Statut", value="⏳ En attente", inline=True)
            embed.set_footer(text="Les admins examineront votre suggestion")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="poll")
    @commands.has_permissions(manage_channels=True)
    async def poll(self, ctx, question: str, *options: str):
        """Créer un sondage"""
        if len(options) < 2 or len(options) > 10:
            return await ctx.send("❌ Spécifiez entre 2 et 10 options.")
        
        # Créer le sondage
        poll_id = f"{ctx.channel.id}_{datetime.datetime.now().timestamp()}"
        
        embed = nextcord.Embed(
            title="📊 Sondage",
            description=f"**Question:** {question}",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        
        for i, option in enumerate(options):
            embed.add_field(name=f"Option {i+1}", value=option, inline=False)
        
        embed.set_footer(text=f"Votez avec les réactions • Sondage par {ctx.author.name}")
        
        message = await ctx.send(embed=embed)
        
        # Ajouter les réactions
        for i in range(len(options)):
            await message.add_reaction(f"{i+1}\u20e3")
        
        # Sauvegarder le sondage
        try:
            with open("data/polls.json", "r") as f:
                polls = json.load(f)
            
            polls[poll_id] = {
                "message_id": message.id,
                "channel_id": ctx.channel.id,
                "question": question,
                "options": list(options),
                "author": ctx.author.id,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            with open("data/polls.json", "w") as f:
                json.dump(polls, f, indent=2)
                
        except Exception as e:
            print(f"Erreur sauvegarde sondage: {e}")
    
    @commands.command(name="vote")
    async def vote(self, ctx, poll_id: str, option: int):
        """Voter à un sondage"""
        if option < 1 or option > 10:
            return await ctx.send("❌ Option invalide (1-10).")
        
        await ctx.send(f"✅ Vous avez voté pour l'option {option} du sondage {poll_id}")
    
    @commands.command(name="birthday")
    async def birthday(self, ctx, member: nextcord.Member = None):
        """Souhaiter joyeux anniversaire"""
        target = member or ctx.author
        
        embed = nextcord.Embed(
            title="🎂 Joyeux Anniversaire!",
            description=f"🎉🎈 Joyeux anniversaire à {target.mention}! 🎈🎉\n\nQue ta journée soit remplie de joie et de bonheur!",
            color=0xff69b4,
            timestamp=datetime.datetime.now()
        )
        embed.set_image(url="https://media.giphy.com/media/3o7TKs4x2T6gP2iWgI/giphy.gif")
        embed.set_footer(text=f"De la part de {ctx.author.name}")
        
        await ctx.send(embed=embed)
    
    @commands.command(name="welcome")
    async def welcome(self, ctx, member: nextcord.Member = None):
        """Accueillir un nouveau membre"""
        target = member or ctx.author
        
        welcome_messages = [
            f"🎉 Bienvenue sur le serveur {target.mention}! Nous sommes ravis de t'avoir parmi nous!",
            f"🌟 Salut {target.mention}! Bienvenue dans notre communauté!",
            f"👋 Hey {target.mention}! Bienvenue et amuse-toi bien!",
            f"🎊 {target.mention} vient de rejoindre le serveur! Faisons-lui un accueil chaleureux!"
        ]
        
        embed = nextcord.Embed(
            title="👋 Bienvenue!",
            description=random.choice(welcome_messages),
            color=0x2ecc71,
            timestamp=datetime.datetime.now()
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.set_footer(text=f"Accueil par {ctx.author.name}")
        
        await ctx.send(embed=embed)
    
    @commands.command(name="goodbye")
    async def goodbye(self, ctx, member: nextcord.Member = None):
        """Dire au revoir à un membre"""
        target = member or ctx.author
        
        embed = nextcord.Embed(
            title="👋 Au Revoir!",
            description=f"😢 {target.mention} nous quitte. Nous espérons te revoir bientôt!",
            color=0xe74c3c,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Au revoir de la part de {ctx.author.name}")
        
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(CommunityFeatures(bot))
