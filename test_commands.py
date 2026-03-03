import bot
import asyncio

async def test_commands():
    print('TEST DE TOUTES LES COMMANDES...')
    
    # Simuler un contexte pour tester
    class MockContext:
        def __init__(self):
            self.guild = MockGuild()
            self.author = MockAuthor()
            self.channel = MockChannel()
    
    class MockGuild:
        def __init__(self):
            self.id = 123456789
            self.icon = None
    
    class MockAuthor:
        def __init__(self):
            self.id = 987654321
            self.mention = '@test_user'
    
    class MockChannel:
        def __init__(self):
            self.id = 555555555
    
    ctx = MockContext()
    
    # Importer tous les cogs
    cogs_to_test = [
        'cogs.moderation_enhanced',
        'cogs.community_features', 
        'cogs.utility_commands',
        'cogs.fun_commands',
        'cogs.extended_commands',
        'cogs.performance_optimizer',
        'cogs.voice',
        'cogs.social',
        'cogs.antimod',
        'cogs.system',
        'cogs.rolemanager',
        'cogs.config_panel',
        'cogs.help_system',
        'cogs.bot_customization',
        'cogs.logs',
        'cogs.games',
        'cogs.dm',
        'cogs.welcome',
        'cogs.tickets'
    ]
    
    total_commands = 0
    
    for cog_name in cogs_to_test:
        try:
            cog_module = __import__(cog_name, fromlist=[''])
            cog_classes = [getattr(cog_module, name) for name in dir(cog_module) 
                         if isinstance(getattr(cog_module, name), type) and 
                         hasattr(getattr(cog_module, name), '__cog_commands__')]
            
            if cog_classes:
                cog_class = cog_classes[0]
                commands_list = [cmd.name for cmd in cog_class.__cog_commands__]
                total_commands += len(commands_list)
                print(f'OK {cog_name}: {len(commands_list)} commandes')
                
                # Tester quelques commandes clés
                for cmd in commands_list[:3]:  # Tester les 3 premières
                    print(f'   - {cmd}')
            else:
                print(f'ERREUR {cog_name}: Pas de cog trouvé')
                
        except Exception as e:
            print(f'ERREUR {cog_name}: {e}')
    
    print(f'\nTOTAL: {total_commands} commandes testees')
    print('Test termine !')

# Lancer le test
asyncio.run(test_commands())
