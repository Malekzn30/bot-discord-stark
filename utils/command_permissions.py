"""
Système de permissions avancé par commande et catégorie
Gère les permissions spécifiques pour chaque type de commande
"""

import json
import os
from functools import wraps
from typing import List, Dict, Set, Optional

# Cache pour les permissions
_command_permissions_cache = {}
_role_permissions_cache = {}
_cache_timestamp = None
_cache_duration = 300  # 5 minutes

# Rôle toujours autorisé
ALWAYS_AUTHORIZED_ROLE = "1469665367881420841"

def load_command_permissions():
    """Charger les permissions de commandes depuis le fichier"""
    try:
        if os.path.exists("data/command_permissions.json"):
            with open("data/command_permissions.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Configuration par défaut si le fichier n'existe pas
            return {
                "global_authorized_roles": [ALWAYS_AUTHORIZED_ROLE],
                "command_permissions": {},
                "role_mappings": {
                    "admin_roles": [ALWAYS_AUTHORIZED_ROLE],
                    "moderator_roles": [],
                    "staff_roles": [],
                    "vip_roles": []
                }
            }
    except Exception as e:
        print(f"Erreur chargement permissions: {e}")
        return {
            "global_authorized_roles": [ALWAYS_AUTHORIZED_ROLE],
            "command_permissions": {},
            "role_mappings": {
                "admin_roles": [ALWAYS_AUTHORIZED_ROLE],
                "moderator_roles": [],
                "staff_roles": [],
                "vip_roles": []
            }
        }

def get_command_category(command_name: str) -> Optional[str]:
    """Déterminer la catégorie d'une commande"""
    permissions_data = load_command_permissions()
    
    for category, data in permissions_data.get("command_permissions", {}).items():
        if command_name in data.get("commands", []):
            return category
    
    return None

def get_authorized_roles_for_command(command_name: str) -> List[str]:
    """Obtenir la liste des rôles autorisés pour une commande spécifique"""
    permissions_data = load_command_permissions()
    
    # Rôles globaux toujours autorisés
    global_roles = permissions_data.get("global_authorized_roles", [])
    
    # Rôles spécifiques à la catégorie de la commande
    category = get_command_category(command_name)
    if category:
        category_roles = permissions_data.get("command_permissions", {}).get(category, {}).get("authorized_roles", [])
        return list(set(global_roles + category_roles))
    
    return global_roles

def is_command_authorized(member, command_name: str) -> bool:
    """Vérifier si un membre est autorisé à utiliser une commande spécifique"""
    if not member.guild:
        return False
    
    # Le propriétaire du serveur a toujours accès
    if member.guild.owner_id == member.id:
        return True
    
    # Récupérer les rôles autorisés pour cette commande
    authorized_roles = get_authorized_roles_for_command(command_name)
    
    # Vérifier si le membre a un des rôles autorisés
    for role_id in authorized_roles:
        try:
            role = member.guild.get_role(int(role_id))
            if role and role in member.roles:
                return True
        except (ValueError, AttributeError):
            continue
    
    return False

def is_command_authorized_cached(member, command_name: str) -> bool:
    """Vérifier avec cache pour optimiser les performances"""
    global _command_permissions_cache, _cache_timestamp
    
    import time
    current_time = time.time()
    
    # Vider le cache s'il est trop vieux
    if _cache_timestamp is None or current_time - _cache_timestamp > _cache_duration:
        _command_permissions_cache.clear()
        _cache_timestamp = current_time
    
    # Vérifier dans le cache
    cache_key = f"{member.guild.id}_{member.id}_{command_name}"
    if cache_key in _command_permissions_cache:
        return _command_permissions_cache[cache_key]
    
    # Calculer et mettre en cache
    authorized = is_command_authorized(member, command_name)
    _command_permissions_cache[cache_key] = authorized
    
    return authorized

def has_command_permission(command_name: str):
    """Décorateur pour vérifier les permissions par commande"""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, ctx, *args, **kwargs):
            # Vérifier les permissions
            if not is_command_authorized_cached(ctx.author, command_name):
                embed = nextcord.Embed(
                    title="❌ Accès refusé",
                    description=f"Vous n'avez pas la permission d'utiliser la commande `+{command_name}`.",
                    color=0xE74C3C
                )
                
                # Afficher les rôles requis
                authorized_roles = get_authorized_roles_for_command(command_name)
                role_mentions = []
                for role_id in authorized_roles:
                    role = ctx.guild.get_role(int(role_id))
                    if role:
                        role_mentions.append(role.mention)
                    else:
                        role_mentions.append(f"`ID: {role_id}`")
                
                if role_mentions:
                    embed.add_field(
                        name="🔒 Rôles requis",
                        value=", ".join(role_mentions),
                        inline=False
                    )
                
                embed.add_field(
                    name="💡 Que faire ?",
                    value="Contactez un administrateur pour obtenir les permissions nécessaires.",
                    inline=False
                )
                
                embed.set_footer(text=f"Utilise +checkperms @{ctx.author.name} pour vérifier vos permissions")
                
                try:
                    await ctx.send(embed=embed, delete_after=15)
                except:
                    pass
                
                return
            
            # Exécuter la commande
            return await func(self, ctx, *args, **kwargs)
        
        return wrapper
    return decorator

def add_role_to_command(command_name: str, role_id: str) -> bool:
    """Ajouter un rôle aux autorisations d'une commande"""
    try:
        permissions_data = load_command_permissions()
        category = get_command_category(command_name)
        
        if category:
            if role_id not in permissions_data["command_permissions"][category]["authorized_roles"]:
                permissions_data["command_permissions"][category]["authorized_roles"].append(role_id)
                
                with open("data/command_permissions.json", 'w', encoding='utf-8') as f:
                    json.dump(permissions_data, f, indent=2, ensure_ascii=False)
                
                # Vider le cache
                clear_permissions_cache()
                return True
        
        return False
    except Exception as e:
        print(f"Erreur ajout rôle commande: {e}")
        return False

def remove_role_from_command(command_name: str, role_id: str) -> bool:
    """Retirer un rôle des autorisations d'une commande"""
    try:
        permissions_data = load_command_permissions()
        category = get_command_category(command_name)
        
        if category:
            if role_id in permissions_data["command_permissions"][category]["authorized_roles"]:
                permissions_data["command_permissions"][category]["authorized_roles"].remove(role_id)
                
                with open("data/command_permissions.json", 'w', encoding='utf-8') as f:
                    json.dump(permissions_data, f, indent=2, ensure_ascii=False)
                
                # Vider le cache
                clear_permissions_cache()
                return True
        
        return False
    except Exception as e:
        print(f"Erreur retrait rôle commande: {e}")
        return False

def clear_permissions_cache():
    """Vider le cache des permissions"""
    global _command_permissions_cache, _role_permissions_cache, _cache_timestamp
    _command_permissions_cache.clear()
    _role_permissions_cache.clear()
    _cache_timestamp = None

def get_user_permissions(member) -> Dict[str, List[str]]:
    """Obtenir toutes les permissions d'un utilisateur"""
    permissions_data = load_command_permissions()
    user_permissions = {}
    
    for category, data in permissions_data.get("command_permissions", {}).items():
        authorized_commands = []
        
        for command in data.get("commands", []):
            if is_command_authorized(member, command):
                authorized_commands.append(command)
        
        if authorized_commands:
            user_permissions[category] = authorized_commands
    
    return user_permissions
