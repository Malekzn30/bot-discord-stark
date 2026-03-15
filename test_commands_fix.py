#!/usr/bin/env python3
"""
Test script to verify the warn and roles command fixes
"""

import nextcord
from nextcord.ext import commands
import inspect
from cogs.bot_complete import BotComplete

def test_command_signatures():
    """Test that the commands have the correct signatures"""
    
    # Create a mock bot for testing
    bot = commands.Bot(command_prefix='+', intents=nextcord.Intents.default())
    cog = BotComplete(bot)
    
    # Get the warn command
    warn_cmd = cog.warn
    warn_sig = inspect.signature(warn_cmd)
    print(f"Warn command signature: {warn_sig}")
    
    # Get the roles command
    roles_cmd = cog.roles
    roles_sig = inspect.signature(roles_cmd)
    print(f"Roles command signature: {roles_sig}")
    
    # Test warn command parameters
    warn_params = warn_sig.parameters
    print(f"Warn parameters:")
    for name, param in warn_params.items():
        if name != 'self':
            default = param.default if param.default != inspect.Parameter.empty else 'REQUIRED'
            print(f"  - {name}: {param.annotation} (default: {default})")
    
    # Test roles command parameters
    roles_params = roles_sig.parameters
    print(f"Roles parameters:")
    for name, param in roles_params.items():
        if name != 'self':
            default = param.default if param.default != inspect.Parameter.empty else 'REQUIRED'
            print(f"  - {name}: {param.annotation} (default: {default})")

def test_command_help():
    """Test command help text"""
    
    bot = commands.Bot(command_prefix='+', intents=nextcord.Intents.default())
    cog = BotComplete(bot)
    
    print(f"Warn command help: {cog.warn.help}")
    print(f"Roles command help: {cog.roles.help}")

if __name__ == "__main__":
    print("Testing command fixes...")
    test_command_signatures()
    test_command_help()
    print("All tests completed!")
