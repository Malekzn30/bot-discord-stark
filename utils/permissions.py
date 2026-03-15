"""
Système de permissions avancé pour le bot
Gère les rôles autorisés de manière dynamique avec permissions par commande
"""

import json
import os
from functools import wraps

# Importer le nouveau système de permissions par commande
from .command_permissions import is_command_authorized_cached, ALWAYS_AUTHORIZED_ROLE

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
    """Vérifier si un membre est autorisé avec cache (ancien système pour compatibilité)"""
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
    """Vérifier si un membre est autorisé à utiliser les commandes (ancien système)"""
    if not member.guild:
        return False
    
    # Vérifier si le membre a le rôle toujours autorisé
    always_authorized_role = member.guild.get_role(ALWAYS_AUTHORIZED_ROLE)
    if always_authorized_role and always_authorized_role in member.roles:
        return True
    
    # Charger les rôles autorisés
    authorized_roles = load_authorized_roles()
    
    # Vérifier si le membre a un des rôles autorisés
    for role_id in authorized_roles:
        role = member.guild.get_role(int(role_id))
        if role and role in member.roles:
            return True
    
    return False

def has_role():
    """Décorateur pour vérifier si un membre a un rôle autorisé (ancien système)"""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, ctx, *args, **kwargs):
            # Vérifier les permissions avec le nouveau système si possible
            command_name = func.__name__
            
            # Essayer le nouveau système de permissions par commande
            try:
                from .command_permissions import is_command_authorized_cached
                if is_command_authorized_cached(ctx.author, command_name):
                    return await func(self, ctx, *args, **kwargs)
            except:
                pass  # Fallback sur l'ancien système
            
            # Ancien système en fallback
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

def has_command_permission(command_name: str):
    """Décorateur pour vérifier les permissions par commande (nouveau système)"""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, ctx, *args, **kwargs):
            # Vérifier les permissions avec le nouveau système
            try:
                from .command_permissions import is_command_authorized_cached
                if is_command_authorized_cached(ctx.author, command_name):
                    return await func(self, ctx, *args, **kwargs)
            except:
                pass
            
            # Message d'erreur
            embed = nextcord.Embed(
                title="❌ Accès refusé",
                description=f"Vous n'avez pas la permission d'utiliser la commande `+{command_name}`.",
                color=0xE74C3C
            )
            
            # Afficher les rôles requis
            try:
                from .command_permissions import get_authorized_roles_for_command
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
            except:
                pass
            
            embed.add_field(
                name="💡 Que faire ?",
                value="Contactez un administrateur pour obtenir les permissions nécessaires.",
                inline=False
            )
            
            embed.set_footer(text=f"Utilise +permissions check @{ctx.author.name} pour vérifier vos permissions")
            
            try:
                await ctx.send(embed=embed, delete_after=15)
            except:
                pass
            
            return
        
        return wrapper
    return decorator

def has_any_role(*role_ids):
    """Décorateur pour vérifier si un membre a un des rôles spécifiés"""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, ctx, *args, **kwargs):
            if not ctx.guild:
                return
            
            # Vérifier si le membre a le rôle toujours autorisé
            always_authorized_role = ctx.guild.get_role(ALWAYS_AUTHORIZED_ROLE)
            if always_authorized_role and always_authorized_role in ctx.author.roles:
                return await func(self, ctx, *args, **kwargs)
            
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
            
            role_mentions = []
            for role_id in role_ids:
                role = ctx.guild.get_role(role_id)
                if role:
                    role_mentions.append(role.mention)
            
            if role_mentions:
                embed.set_footer(text="Permissions requises : " + ", ".join(role_mentions))
            
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
    
    # Vider aussi le cache du nouveau système
    try:
        from .command_permissions import clear_permissions_cache as clear_command_cache
        clear_command_cache()
    except:
        pass
