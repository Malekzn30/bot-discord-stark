import json
import os
from typing import Dict, Any

class ConfigManager:
    def __init__(self):
        self.config_file = "data/bot_config.json"
        self.default_config = {
            "bot": {
                "name": "Bot Stark",
                "prefix": "+",
                "description": "Bot Discord multifonctionnel",
                "version": "1.0.0"
            },
            "appearance": {
                "profile_picture": None,
                "banner": None,
                "bio": "Bot Discord multifonctionnel avec modération, vocal, jeux et plus !",
                "status": "online",
                "activity_type": "watching",
                "activity_text": "vos serveurs",
                "color_scheme": {
                    "primary": 0x3498db,
                    "success": 0x2ECC71,
                    "warning": 0xF39C12,
                    "error": 0xE74C3C,
                    "info": 0x9B59B6
                }
            },
            "features": {
                "moderation": {
                    "enabled": True,
                    "auto_mod": False,
                    "log_channel": None,
                    "welcome_channel": None,
                    "goodbye_channel": None
                },
                "vocal": {
                    "enabled": True,
                    "auto_balance": False,
                    "max_members_per_channel": 5,
                    "create_temp_channels": False
                },
                "social": {
                    "enabled": True,
                    "live_notifications": True,
                    "live_role": None,
                    "social_commands": True
                },
                "games": {
                    "enabled": True,
                    "daily_rewards": False,
                    "leaderboards": False
                }
            },
            "permissions": {
                "admin_roles": [],
                "moderator_roles": [],
                "trusted_users": [],
                "blacklisted_users": []
            },
            "messages": {
                "welcome_message": "Bienvenue {user} sur {server} !",
                "goodbye_message": "Au revoir {user} !",
                "level_up_message": "Félicitations {user}, tu as atteint le niveau {level} !",
                "custom_commands": {}
            },
            "server_specific": {}
        }
        
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Charger la configuration depuis le fichier"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Fusionner avec la config par défaut pour les nouvelles options
                    return self._merge_configs(self.default_config, loaded_config)
            except Exception as e:
                print(f"Erreur de chargement de la config: {e}")
                return self.default_config.copy()
        return self.default_config.copy()
    
    def save_config(self):
        """Sauvegarder la configuration dans le fichier"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erreur de sauvegarde de la config: {e}")
            return False
    
    def _merge_configs(self, default: Dict, loaded: Dict) -> Dict:
        """Fusionner la config chargée avec la config par défaut"""
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def get(self, path: str, default=None):
        """Récupérer une valeur avec un chemin type 'bot.name'"""
        keys = path.split('.')
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    def set(self, path: str, value):
        """Définir une valeur avec un chemin type 'bot.name'"""
        keys = path.split('.')
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value
        return self.save_config()
    
    def get_server_config(self, guild_id: int) -> Dict[str, Any]:
        """Récupérer la configuration spécifique à un serveur"""
        server_config = self.config.get("server_specific", {}).get(str(guild_id), {})
        return server_config
    
    def set_server_config(self, guild_id: int, config: Dict[str, Any]):
        """Définir la configuration spécifique à un serveur"""
        if "server_specific" not in self.config:
            self.config["server_specific"] = {}
        self.config["server_specific"][str(guild_id)] = config
        return self.save_config()
    
    def reset_to_default(self):
        """Réinitialiser la configuration par défaut"""
        self.config = self.default_config.copy()
        return self.save_config()

# Instance globale
config_manager = ConfigManager()
