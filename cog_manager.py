import nextcord
from nextcord.ext import commands
import asyncio
import json
import os

class CogManager:
    def __init__(self, bot):
        self.bot = bot
        self.loaded_cogs = set()
        self.cog_config = self.load_cog_config()
    
    def load_cog_config(self):
        """Charger la configuration des cogs"""
        config_file = "data/cog_config.json"
        
        if not os.path.exists(config_file):
            default_config = {
                "essential": ["voice", "system_interactive", "bot_complete", "permission_manager"],
                "optional": [
                    "moderation_enhanced",
                    "utility_commands", 
                    "fun_commands",
                    "performance_optimizer",
                    "social",
                    "rolemanager",
                    "bot_customization",
                    "logs",
                    "games",
                    "dm",
                    "welcome",
                    "tickets",
                    "server_config",
                    "community_features",
                    "antimod"
                ],
                "disabled": [],
                "auto_load": True
            }
            
            os.makedirs("data", exist_ok=True)
            with open(config_file, "w") as f:
                json.dump(default_config, f, indent=2)
            
            return default_config
        
        with open(config_file, "r") as f:
            return json.load(f)
    
    async def load_essential_cogs(self):
        """Charger uniquement les cogs essentiels au démarrage"""
        print("[COG MANAGER] Chargement des cogs essentiels...")
        
        for cog_name in self.cog_config["essential"]:
            if cog_name not in self.cog_config["disabled"]:
                success = await self.load_single_cog(cog_name, priority=True)
                if success:
                    self.loaded_cogs.add(cog_name)
        
        print(f"[COG MANAGER] {len(self.loaded_cogs)} cogs essentiels chargés")
    
    async def load_optional_cogs(self):
        """Charger les cogs optionnels après le démarrage"""
        print("[COG MANAGER] Chargement des cogs optionnels...")
        
        for cog_name in self.cog_config["optional"]:
            if cog_name not in self.cog_config["disabled"] and cog_name not in self.loaded_cogs:
                success = await self.load_single_cog(cog_name, priority=False)
                if success:
                    self.loaded_cogs.add(cog_name)
        
        print(f"[COG MANAGER] {len(self.loaded_cogs)} cogs totaux chargés")
    
    async def load_single_cog(self, cog_name, priority=False):
        """Charger un seul cog avec gestion d'erreur"""
        try:
            self.bot.load_extension(f"cogs.{cog_name}")
            
            pause_time = 0.3 if priority else 0.1
            await asyncio.sleep(pause_time)
            
            print(f"[+] Cog chargé : {cog_name}")
            return True
            
        except Exception as e:
            print(f"[!] Erreur chargement {cog_name}: {e}")
            return False
    
    async def unload_cog(self, cog_name):
        """Décharger un cog"""
        try:
            if cog_name in self.loaded_cogs:
                self.bot.unload_extension(f"cogs.{cog_name}")
                self.loaded_cogs.discard(cog_name)
                print(f"[-] Cog déchargé : {cog_name}")
                return True
        except Exception as e:
            print(f"[!] Erreur déchargement {cog_name}: {e}")
        return False
    
    async def reload_cog(self, cog_name):
        """Recharger un cog"""
        await self.unload_cog(cog_name)
        return await self.load_single_cog(cog_name, priority=True)
    
    async def load_cog_on_demand(self, cog_name):
        """Charger un cog à la demande"""
        if cog_name in self.loaded_cogs:
            return True
        
        if cog_name in self.cog_config["essential"] + self.cog_config["optional"]:
            success = await self.load_single_cog(cog_name, priority=True)
            if success:
                self.loaded_cogs.add(cog_name)
            return success
        
        return False
    
    def get_loaded_cogs(self):
        """Obtenir la liste des cogs chargés"""
        return list(self.loaded_cogs)
    
    def get_cog_status(self):
        """Obtenir le statut de tous les cogs"""
        status = {
            "loaded": list(self.loaded_cogs),
            "essential": self.cog_config["essential"],
            "optional": self.cog_config["optional"],
            "disabled": self.cog_config["disabled"],
            "total_loaded": len(self.loaded_cogs),
            "total_available": len(self.cog_config["essential"]) + len(self.cog_config["optional"])
        }
        return status

def setup_cog_manager(bot):
    """Initialiser le gestionnaire de cogs"""
    return CogManager(bot)
