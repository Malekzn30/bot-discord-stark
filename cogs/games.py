import nextcord
from nextcord.ext import commands
import random
from config import AUTHORIZED_ROLE_ID
import asyncio
import time

# Cache limité pour Render
active_games = {}  # {channel_id: {...}}
ROLE_DM_ID = 1469665367881420841
GAME_TIMEOUT = 1800  # Auto-cleanup après 30 min (plus agressif)
MAX_GAMES = 10  # Max 10 jeux simultanés

def cleanup_games():
    """Nettoyage agressif des jeux."""
    global active_games
    now = time.time()
    # Supprimer les jeux > 30 min
    expired = [cid for cid, game in active_games.items() if now - game.get("started_at", 0) > GAME_TIMEOUT]
    for cid in expired:
        del active_games[cid]
    
    # Si > 10 jeux, supprimer les plus anciens
    if len(active_games) > MAX_GAMES:
        sorted_games = sorted(active_games.items(), key=lambda x: x[1].get("started_at", 0))
        for cid, _ in sorted_games[:-MAX_GAMES]:
            del active_games[cid]

def has_role():
    async def predicate(ctx):
        role = ctx.guild.get_role(AUTHORIZED_ROLE_ID)
        return role in ctx.author.roles
    return commands.check(predicate)

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="devinelenombre",
        help="Lance un jeu où les membres doivent deviner un nombre dans un salon donné."
    )
    @has_role()
    async def devinelenombre(self, ctx, min_val: int, max_val: int, channel: nextcord.TextChannel):
        if min_val > max_val:
            return await ctx.send("❌ Le premier nombre doit être inférieur ou égal au second.")

        number = random.randint(min_val, max_val)
        # store game state with timestamp for auto-cleanup
        active_games[channel.id] = {"number": number, "min": min_val, "max": max_val, "started_at": time.time()}

        # lock channel for countdown
        try:
            await channel.set_permissions(ctx.guild.default_role, send_messages=False)
        except Exception:
            pass

        await ctx.send(f"🎮 Jeu programmé dans {channel.mention} — verrouillage pour le compte à rebours.")

        # countdown in the target channel
        countdown_msg = await channel.send("Le jeu commence dans 5...")
        for i in range(4, 0, -1):
            await asyncio.sleep(1)
            try:
                await countdown_msg.edit(content=f"Le jeu commence dans {i}...")
            except Exception:
                pass

        # unlock channel to allow guesses
        try:
            await channel.set_permissions(ctx.guild.default_role, send_messages=True)
        except Exception:
            pass

        await channel.send(f"🔓 Le jeu commence ! Devinez un nombre entre **{min_val}** et **{max_val}** !")

        # send the chosen number by DM to members with the specified role
        role = ctx.guild.get_role(ROLE_DM_ID)
        if role:
            for member in role.members:
                try:
                    await member.send(f"🔒 Jeu devinelenombre dans {channel.guild.name}#{channel.name} — nombre choisi : **{number}**")
                except Exception:
                    pass

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        cid = message.channel.id
        if cid not in active_games:
            return

        try:
            guess = int(message.content)
        except:
            return

        game = active_games.get(cid)
        if not game:
            return

        if guess == game["number"]:
            # announce and lock the channel; require +unlock to reopen
            await message.channel.send(f"✅ {message.author.mention} a trouvé le nombre **{game['number']}** ! Le salon est verrouillé. Utilisez `+unlock` pour déverrouiller.")
            try:
                await message.channel.set_permissions(message.guild.default_role, send_messages=False)
            except Exception:
                pass
            del active_games[cid]

    @commands.command(name="dice")
    async def dice(self, ctx, sides: int = 6):
        if sides < 2:
            return await ctx.send("❌ Le nombre de faces doit être >= 2.")
        roll = random.randint(1, sides)
        await ctx.send(f"🎲 {ctx.author.mention} a lancé un dé ({sides} faces) et obtenu : **{roll}**")

    @commands.command(name="coin")
    async def coin(self, ctx):
        res = random.choice(["Pile", "Face"])
        await ctx.send(f"🪙 {ctx.author.mention} → **{res}**")

    @commands.command(name="rps")
    async def rps(self, ctx, choice: str = None):
        if not choice:
            return await ctx.send("❌ Utilise : `+rps <rock|paper|scissors>`")
        choice = choice.lower()
        opts = {"rock":"rock","paper":"paper","scissors":"scissors"}
        if choice not in opts:
            return await ctx.send("❌ Choix invalide. Utilise rock/paper/scissors.")

        comp = random.choice(list(opts.keys()))
        outcome = "égalité"
        if (choice == "rock" and comp == "scissors") or (choice == "paper" and comp == "rock") or (choice == "scissors" and comp == "paper"):
            outcome = "gagné"
        elif choice != comp:
            outcome = "perdu"

        await ctx.send(f"✋ {ctx.author.mention} → **{choice}** vs {comp} → **{outcome}**")

    @commands.command(name="trivia")
    async def trivia(self, ctx):
        questions = [
            {"q":"Quelle est la capitale de la France?","a":"paris"},
            {"q":"Combien de jours y a-t-il dans une année non bissextile?","a":"365"},
            {"q":"Quel est le plus grand océan sur Terre?","a":"pacific"}
        ]

        qa = random.choice(questions)
        await ctx.send(f"❓ Trivia : {qa['q']} (15s)")

        def check(m):
            return m.channel == ctx.channel and m.author == ctx.author

        try:
            msg = await self.bot.wait_for('message', timeout=15.0, check=check)
            if msg.content.lower().strip() == qa['a']:
                await ctx.send(f"✅ Correct, {ctx.author.mention}!")
            else:
                await ctx.send(f"❌ Faux — la réponse était **{qa['a']}**")
        except asyncio.TimeoutError:
            await ctx.send(f"⌛ Temps écoulé — la réponse était **{qa['a']}**")

    @commands.command(name="higher_lower")
    async def higher_lower(self, ctx):
        """Devinez si le prochain nombre est plus haut ou bas."""
        n1 = random.randint(1, 100)
        n2 = random.randint(1, 100)
        await ctx.send(f"🎲 Nombre : **{n1}** — Le prochain sera-t-il plus **haut** ou **bas**?")
        
        def check(m):
            return m.channel == ctx.channel and m.author == ctx.author and m.content.lower() in ['haut', 'bas']
        
        try:
            msg = await self.bot.wait_for('message', timeout=10.0, check=check)
            guess = msg.content.lower()
            result = "haut" if n2 > n1 else "bas"
            if guess == result:
                await ctx.send(f"✅ Correct! Le nombre était **{n2}**!")
            else:
                await ctx.send(f"❌ Faux — le nombre était **{n2}** (plus {result})")
        except asyncio.TimeoutError:
            await ctx.send(f"⌛ Temps écoulé — la réponse était **{n2}** (plus {'haut' if n2 > n1 else 'bas'})")

    @commands.command(name="slots")
    async def slots(self, ctx):
        """Jeu de machines à sous."""
        emojis = ['🍎', '🍊', '🍋', '🍌', '🍇']
        result = [random.choice(emojis) for _ in range(3)]
        await ctx.send(f"🎰 {result[0]} {result[1]} {result[2]}")
        if result[0] == result[1] == result[2]:
            await ctx.send(f"🎉 {ctx.author.mention} a gagné le jackpot!")
        elif result[0] == result[1] or result[1] == result[2]:
            await ctx.send(f"⭐ {ctx.author.mention} a un petit gain!")
        else:
            await ctx.send(f"😢 {ctx.author.mention} a perdu...")

    @commands.command(name="rock_paper_scissors")
    async def rock_paper_scissors(self, ctx):
        """Variante du RPS avec choix multiples."""
        opts = {"pierre":"pierre","papier":"papier","ciseaux":"ciseaux"}
        await ctx.send(f"✂️ Choisis : pierre / papier / ciseaux")
        
        def check(m):
            return m.channel == ctx.channel and m.author == ctx.author and m.content.lower() in opts
        
        try:
            msg = await self.bot.wait_for('message', timeout=10.0, check=check)
            user_choice = msg.content.lower()
            bot_choice = random.choice(list(opts.keys()))
            
            if user_choice == bot_choice:
                result = "égalité"
            elif (user_choice == "pierre" and bot_choice == "ciseaux") or \
                 (user_choice == "papier" and bot_choice == "pierre") or \
                 (user_choice == "ciseaux" and bot_choice == "papier"):
                result = "gagné"
            else:
                result = "perdu"
            
            await ctx.send(f"🔥 {user_choice} vs {bot_choice} → **{result}**")
        except asyncio.TimeoutError:
            await ctx.send("⌛ Temps écoulé")

def setup(bot):
    bot.add_cog(Games(bot))
