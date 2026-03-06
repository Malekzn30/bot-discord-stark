import bot

# Créer une instance du bot
bot_instance = bot.bot

# Charger les cogs manuellement pour voir les erreurs
cogs_to_load = [
    "cogs.moderation_enhanced",
    "cogs.community_features", 
    "cogs.utility_commands",
    "cogs.fun_commands",
    "cogs.performance_optimizer",
    "cogs.voice",
    "cogs.social",
    "cogs.antimod",
    "cogs.system_interactive",
    "cogs.rolemanager",
    "cogs.bot_customization",
    "cogs.logs",
    "cogs.games",
    "cogs.dm",
    "cogs.welcome",
    "cogs.tickets",
    "cogs.server_config",
    "bot_complete"
]

print("Chargement des cogs...")
for cog in cogs_to_load:
    try:
        bot_instance.load_extension(cog)
        print(f"[OK] {cog} chargé")
    except Exception as e:
        print(f"[ERREUR] {cog}: {e}")

print(f"\nTotal commandes: {len(bot_instance.commands)}")
print("Commandes chargées:")
for cmd in bot_instance.commands:
    print(f"  - {cmd.name}")
