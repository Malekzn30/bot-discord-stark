"""
Système de permissions avancé pour le bot
Gère les rôles autorisés de manière dynamique
"""

import json
import os
from functools import wraps

# Cache pour les permissions
_permissions_cache = {}
_cache_timestamp = None
_cache_duration = 300  # 5 minutes

def load_authorized_roles():
    """Charger la liste des rôles autorisés depuis le fichier"""
    try:
        if os.path.exists("data/authorized_roles.json"):
            with open("data/authorized_roles.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Fallback sur le rôle principal par défaut
            from config import AUTHORIZED_ROLE_ID
            return [str(AUTHORIZED_ROLE_ID)]
    except Exception:
        from config import AUTHORIZED_ROLE_ID
        return [str(AUTHORIZED_ROLE_ID)]

def is_authorized_cached(member):
    """Vérifier si un membre est autorisé avec cache"""
    global _permissions_cache, _cache_timestamp
    
    import time
    current_time = time.time()
    
    # Vider le cache s'il est trop vieux
    if _cache_timestamp is None or current_time - _cache_timestamp > _cache_duration:
        _permissions_cache.clear()
        _cache_timestamp = current_time
    
    # Vérifier dans le cache
    cache_key = f"{member.guild.id}_{member.id}"
    if cache_key in _permissions_cache:
        return _permissions_cache[cache_key]
    
    # Calculer et mettre en cache
    authorized = is_authorized(member)
    _permissions_cache[cache_key] = authorized
    
    return authorized

def is_authorized(member):
    """Vérifier si un membre est autorisé à utiliser les commandes"""
    if not member.guild:
        return False
    
    # Charger les rôles autorisés
    authorized_roles = load_authorized_roles()
    
    # Vérifier si le membre a un des rôles autorisés
    for role_id in authorized_roles:
        role = member.guild.get_role(int(role_id))
        if role and role in member.roles:
            return True
    
    return False

def has_role():
    """Décorateur pour vérifier si un membre a un rôle autorisé"""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, ctx, *args, **kwargs):
            # Vérifier les permissions
            if not is_authorized_cached(ctx.author):
                embed = nextcord.Embed(
                    title="❌ Accès refusé",
                    description="Vous n'avez pas la permission d'utiliser cette commande.",
                    color=0xE74C3C
                )
                
                embed.add_field(
                    name="🔒 Raison",
                    value="Vous devez avoir un rôle autorisé pour utiliser les commandes du bot.",
                    inline=False
                )
                
                embed.add_field(
                    name="💡 Que faire ?",
                    value="Contactez un administrateur pour obtenir les permissions nécessaires.",
                    inline=False
                )
                
                embed.set_footer(text="Utilise +checkperms pour vérifier vos permissions")
                
                try:
                    await ctx.send(embed=embed, delete_after=10)
                except:
                    pass  # Ignorer si on ne peut pas répondre
                
                return
            
            # Exécuter la commande
            return await func(self, ctx, *args, **kwargs)
        
        return wrapper
    return decorator

def has_any_role(*role_ids):
    """Décorateur pour vérifier si un membre a un des rôles spécifiés"""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, ctx, *args, **kwargs):
            if not ctx.guild:
                return
            
            # Vérifier si le membre a un des rôles
            for role_id in role_ids:
                role = ctx.guild.get_role(role_id)
                if role and role in ctx.author.roles:
                    return await func(self, ctx, *args, **kwargs)
            
            # Message d'erreur
            embed = nextcord.Embed(
                title="❌ Permissions insuffisantes",
                description="Vous n'avez pas les permissions requises pour cette commande.",
                color=0xE74C3C
            )
            
            embed.set_footer(text="Permissions requises : " + ", ".join([f"<@&{rid}>" for rid in role_ids]))
            
            try:
                await ctx.send(embed=embed, delete_after=10)
            except:
                pass
            
            return
        
        return wrapper
    return decorator

def is_admin(member):
    """Vérifier si un membre est administrateur du serveur"""
    return member.guild_permissions.administrator

def is_moderator(member):
    """Vérifier si un membre est modérateur (rôle admin ou permissions)"""
    return is_admin(member) or member.guild_permissions.manage_guild

def clear_permissions_cache():
    """Vider le cache des permissions"""
    global _permissions_cache, _cache_timestamp
    _permissions_cache.clear()
    _cache_timestamp = None
