#!/usr/bin/env python3

# ============= TEST DU BOT STARK =============

import sys
import os

# Ajouter le répertoire courant au path
sys.path.append(os.path.dirname(__file__))

def test_imports():
    """Tester tous les imports du bot"""
    print("TEST DES IMPORTS DU BOT STARK...")
    
    try:
        # Importer la configuration
        import config
        print("OK Config importee")
        
        # Importer le bot
        import bot
        print("OK Bot importe")
        
        # Importer les cogs
        cogs_to_test = [
            "cogs.moderation_enhanced",
            "cogs.community_features", 
            "cogs.utility_commands",
            "cogs.fun_commands",
            "cogs.extended_commands",
            "cogs.performance_optimizer",
            "cogs.voice",
            "cogs.social",
            "cogs.antimod",
            "cogs.system",
            "cogs.rolemanager",
            "cogs.config_panel",
            "cogs.help_system",
            "cogs.bot_customization",
            "cogs.logs",
            "cogs.games",
            "cogs.dm",
            "cogs.welcome",
            "cogs.tickets"
        ]
        
        for cog in cogs_to_test:
            try:
                __import__(cog)
                print(f"OK {cog}")
            except Exception as e:
                print(f"ERREUR {cog}: {e}")
        
        print("\nTest termine !")
        print(f"{len(cogs_to_test)} cogs testes")
        
    except Exception as e:
        print(f"ERREUR CRITIQUE: {e}")

def test_dependencies():
    """Tester les dépendances"""
    print("\nTEST DES DEPENDANCES...")
    
    dependencies = [
        "nextcord",
        "aiohttp", 
        "dotenv",
        "psutil",
        "PIL",
        "requests",
        "bs4",
        "nacl",
        "flask"
    ]
    
    for dep in dependencies:
        try:
            __import__(dep.replace("-", "_"))
            print(f"OK {dep}")
        except ImportError:
            print(f"ERREUR {dep}")

def test_files():
    """Tester les fichiers essentiels"""
    print("\nTEST DES FICHIERS...")
    
    essential_files = [
        "bot.py",
        "config.py",
        "requirements.txt",
        "runtime.txt",
        ".env.example",
        ".gitignore"
    ]
    
    for file in essential_files:
        if os.path.exists(file):
            print(f"OK {file}")
        else:
            print(f"ERREUR {file}")

if __name__ == "__main__":
    print("DEMARRAGE DU TEST DU BOT STARK...\n")
    
    test_files()
    test_dependencies()
    test_imports()
    
    print("\nTEST COMPLET TERMINE !")
