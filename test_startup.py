#!/usr/bin/env python3
"""
Script de test pour verifier le temps de demarrage du bot
"""

import time
import asyncio
import bot

async def test_startup():
    print("Test de demarrage du bot...")
    start_time = time.time()
    
    # Charger les cogs essentiels
    await bot.load_cogs_async()
    
    end_time = time.time()
    startup_time = end_time - start_time
    
    print(f"Temps de demarrage: {startup_time:.2f} secondes")
    print(f"Commandes chargees: {len(bot.bot.commands)}")
    print(f"Cogs charges: {len(bot.cog_manager.loaded_cogs)}")
    
    # Afficher les cogs essentiels
    print("\nCogs essentiels charges:")
    for cog in bot.cog_manager.loaded_cogs:
        print(f"  OK {cog}")
    
    print(f"\nPerformance: {len(bot.bot.commands)/startup_time:.1f} commandes/seconde")

if __name__ == "__main__":
    asyncio.run(test_startup())
