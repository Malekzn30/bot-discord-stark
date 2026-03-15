"""
Commandes pour gérer les permissions par rôle et par commande
"""

import nextcord
from nextcord.ext import commands
import json
from utils.command_permissions import (
    load_command_permissions, 
    get_command_category,
    get_authorized_roles_for_command,
    add_role_to_command,
    remove_role_from_command,
    clear_permissions_cache,
    get_user_permissions
)

class PermissionManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="permissions")
    @commands.has_permissions(administrator=True)
    async def permissions(self, ctx, action: str = None, command_name: str = None, role: nextcord.Role = None):
        """Gérer les permissions des commandes
        
        Actions disponibles:
        - list: Voir toutes les permissions
        - add <commande> @rôle: Ajouter un rôle à une commande
        - remove <commande> @rôle: Retirer un rôle d'une commande
        - check @user: Vérifier les permissions d'un utilisateur
        """
        
        if action is None:
            await self.show_permissions_help(ctx)
            return
        
        action = action.lower()
        
        if action == "list":
            await self.list_permissions(ctx)
        elif action == "add":
            if command_name is None or role is None:
                return await ctx.send("❌ Utilisation: `+permissions add <commande> @rôle`")
            await self.add_permission(ctx, command_name, role)
        elif action == "remove":
            if command_name is None or role is None:
                return await ctx.send("❌ Utilisation: `+permissions remove <commande> @rôle`")
            await self.remove_permission(ctx, command_name, role)
        elif action == "check":
            if command_name is None:  # Ici command_name est l'utilisateur
                return await ctx.send("❌ Utilisation: `+permissions check @utilisateur`")
            await self.check_user_permissions(ctx, command_name)
        else:
            await self.show_permissions_help(ctx)

    async def show_permissions_help(self, ctx):
        """Afficher l'aide pour les permissions"""
        embed = nextcord.Embed(
            title="🔐 Gestion des Permissions",
            description="Système de permissions par commande et par rôle",
            color=0x3498db
        )
        
        embed.add_field(
            name="📋 Commandes disponibles",
            value="`+permissions list` - Voir toutes les permissions\n"
                  "`+permissions add <commande> @rôle` - Ajouter une permission\n"
                  "`+permissions remove <commande> @rôle` - Retirer une permission\n"
                  "`+permissions check @user` - Vérifier les permissions d'un utilisateur",
            inline=False
        )
        
        embed.add_field(
            name="🎯 Rôle toujours autorisé",
            value=f"<@&1469665367881420841> - Ce rôle a accès à toutes les commandes",
            inline=False
        )
        
        embed.set_footer(text="Utilise +help pour voir les commandes disponibles")
        await ctx.send(embed=embed)

    async def list_permissions(self, ctx):
        """Lister toutes les permissions configurées"""
        permissions_data = load_command_permissions()
        
        embed = nextcord.Embed(
            title="📋 Permissions Configurées",
            description="Liste des permissions par catégorie",
            color=0x3498db
        )
        
        # Rôles globaux
        global_roles = permissions_data.get("global_authorized_roles", [])
        global_mentions = []
        for role_id in global_roles:
            role = ctx.guild.get_role(int(role_id))
            if role:
                global_mentions.append(role.mention)
        
        if global_mentions:
            embed.add_field(
                name="🌐 Rôles globaux (toutes les commandes)",
                value=", ".join(global_mentions),
                inline=False
            )
        
        # Permissions par catégorie
        for category, data in permissions_data.get("command_permissions", {}).items():
            authorized_roles = data.get("authorized_roles", [])
            commands = data.get("commands", [])
            
            role_mentions = []
            for role_id in authorized_roles:
                role = ctx.guild.get_role(int(role_id))
                if role:
                    role_mentions.append(role.mention)
            
            if role_mentions and commands:
                embed.add_field(
                    name=f"📂 {category.title()}",
                    value=f"**Rôles:** {', '.join(role_mentions)}\n"
                          f"**Commandes:** {', '.join(commands[:10])}{'...' if len(commands) > 10 else ''}",
                    inline=False
                )
        
        await ctx.send(embed=embed)

    async def add_permission(self, ctx, command_name: str, role: nextcord.Role):
        """Ajouter une permission à une commande"""
        if add_role_to_command(command_name, str(role.id)):
            embed = nextcord.Embed(
                title="✅ Permission ajoutée",
                description=f"Le rôle {role.mention} peut maintenant utiliser `+{command_name}`",
                color=0x2ecc71
            )
            await ctx.send(embed=embed)
        else:
            embed = nextcord.Embed(
                title="❌ Erreur",
                description=f"Impossible d'ajouter la permission pour `+{command_name}`\n"
                          f"Vérifiez que la commande existe et que la catégorie est configurée.",
                color=0xe74c3c
            )
            await ctx.send(embed=embed)

    async def remove_permission(self, ctx, command_name: str, role: nextcord.Role):
        """Retirer une permission d'une commande"""
        if remove_role_from_command(command_name, str(role.id)):
            embed = nextcord.Embed(
                title="✅ Permission retirée",
                description=f"Le rôle {role.mention} ne peut plus utiliser `+{command_name}`",
                color=0x2ecc71
            )
            await ctx.send(embed=embed)
        else:
            embed = nextcord.Embed(
                title="❌ Erreur",
                description=f"Impossible de retirer la permission pour `+{command_name}`",
                color=0xe74c3c
            )
            await ctx.send(embed=embed)

    async def check_user_permissions(self, ctx, user_mention: str):
        """Vérifier les permissions d'un utilisateur"""
        # Extraire l'ID de l'utilisateur depuis la mention
        import re
        match = re.search(r'<@!?(\d+)>', user_mention)
        if not match:
            return await ctx.send("❌ Mention invalide. Utilise `+permissions check @utilisateur`")
        
        user_id = int(match.group(1))
        member = ctx.guild.get_member(user_id)
        
        if not member:
            return await ctx.send("❌ Utilisateur introuvable sur ce serveur.")
        
        user_perms = get_user_permissions(member)
        
        embed = nextcord.Embed(
            title="🔍 Permissions de l'utilisateur",
            description=f"Permissions pour {member.mention}",
            color=0x3498db
        )
        
        if user_perms:
            for category, commands in user_perms.items():
                embed.add_field(
                    name=f"📂 {category.title()}",
                    value=f"`{', '.join(commands)}`",
                    inline=False
                )
        else:
            embed.add_field(
                name="❌ Aucune permission",
                value="Cet utilisateur n'a accès à aucune commande spécifique.",
                inline=False
            )
        
        # Vérifier si l'utilisateur a le rôle toujours autorisé
        always_authorized_role = ctx.guild.get_role(1469665367881420841)
        if always_authorized_role and always_authorized_role in member.roles:
            embed.add_field(
                name="🌟 Accès total",
                value=f"Cet utilisateur a le rôle {always_authorized_role.mention} qui donne accès à toutes les commandes.",
                inline=False
            )
        
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        await ctx.send(embed=embed)

    @commands.command(name="checkperms")
    @commands.has_permissions(administrator=True)
    async def check_perms(self, ctx, member: nextcord.Member = None):
        """Vérifier les permissions d'un membre (version simplifiée)"""
        target = member or ctx.author
        
        # Vérifier le rôle toujours autorisé
        always_authorized_role = ctx.guild.get_role(1469665367881420841)
        has_global_access = always_authorized_role and always_authorized_role in target.roles
        
        embed = nextcord.Embed(
            title="🔐 Permissions",
            description=f"Permissions de {target.mention}",
            color=0x3498db
        )
        
        if has_global_access:
            embed.add_field(
                name="🌟 Accès total",
                value=f"✅ A accès à toutes les commandes via {always_authorized_role.mention}",
                inline=False
            )
        else:
            user_perms = get_user_permissions(target)
            if user_perms:
                for category, commands in user_perms.items():
                    embed.add_field(
                        name=f"📂 {category.title()}",
                        value=f"`{', '.join(commands[:5])}{'...' if len(commands) > 5 else ''}`",
                        inline=False
                    )
            else:
                embed.add_field(
                    name="❌ Permissions limitées",
                    value="Cet utilisateur a accès aux commandes de base uniquement.",
                    inline=False
                )
        
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(PermissionManager(bot))
