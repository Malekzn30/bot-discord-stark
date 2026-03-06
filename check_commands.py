import bot
from collections import Counter

# Charger les cogs
bot.load_cogs()

print(f"Total commandes: {len(bot.bot.commands)}")
print("\nCategories de commandes:")

cogs = []
for cmd in bot.bot.commands:
    if cmd.cog:
        cogs.append(cmd.cog.__class__.__name__)
    else:
        cogs.append("Inconnu")

for cog, count in Counter(cogs).most_common():
    print(f"{cog}: {count} commandes")

print("\nListe des commandes:")
for cmd in sorted(bot.bot.commands, key=lambda x: x.name):
    cog_name = cmd.cog.__class__.__name__ if cmd.cog else "Inconnu"
    print(f"+{cmd.name} ({cog_name})")
