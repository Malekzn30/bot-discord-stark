import nextcord
from nextcord.ext import commands
import threading
from flask import Flask
import os
import time
from config import TOKEN

# ============================
# DISCORD BOT
# ============================

intents = nextcord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="+", intents=intents, help_command=None)

# Pour +stat et +help
bot.start_time = time.time()

@bot.event
async def on_ready():
    print(f"Bot prêt : {bot.user}")

def load_cogs():
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            bot.load_extension(f"cogs.{file[:-3]}")
            print(f"[+] Cog chargé : {file}")

def run_bot():
    load_cogs()
    bot.run(TOKEN)

# ============================
# FAKE FLASK SERVER (pour Render)
# ============================

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Discord en ligne."

def run_flask():
    app.run(host="0.0.0.0", port=10000)

# ============================
# LANCEMENT
# ============================

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    run_flask()