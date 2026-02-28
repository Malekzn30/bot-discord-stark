import nextcord
from nextcord.ext import commands
import os
import time
from config import TOKEN

intents = nextcord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="+", intents=intents, help_command=None)

# IMPORTANT : nécessaire pour le +stat et le +help
bot.start_time = time.time()

@bot.event
async def on_ready():
    print(f"Bot prêt : {bot.user}")

def load_cogs():
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            bot.load_extension(f"cogs.{file[:-3]}")
            print(f"[+] Cog chargé : {file}")

load_cogs()
bot.run(TOKEN)

