import nextcord
from nextcord.ext import commands
import json
import os
from datetime import datetime
from config import AUTHORIZED_ROLE_ID
from utils.permissions import has_role, clear_permissions_cache

class RoleManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.authorized_roles_file = "data/authorized_roles.json"
        self.authorized_roles = self.load_authorized_roles()
        
        # S'assurer que le rôle principal est toujours dans la liste
        if str(AUTHORIZED_ROLE_ID) not in self.authorized_roles:
            self.authorized_roles.append(str(AUTHORIZED_ROLE_ID))
            self.save_authorized_roles()

    def load_authorized_roles(self):
        """Charger la liste des rôles autorisés"""
        try:
            if os.path.exists(self.authorized_roles_file):
                with open(self.authorized_roles_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Par défaut, seulement le rôle principal
                return [str(AUTHORIZED_ROLE_ID)]
        except Exception as e:
            print(f"Erreur chargement rôles autorisés: {e}")
            return [str(AUTHORIZED_ROLE_ID)]

    def save_authorized_roles(self):
        """Sauvegarder la liste des rôles autorisés"""
        try:
            os.makedirs(os.path.dirname(self.authorized_roles_file), exist_ok=True)
            with open(self.authorized_roles_file, 'w', encoding='utf-8') as f:
                json.dump(self.authorized_roles, f, indent=2, ensure_ascii=False)
            # Vider le cache après modification
            clear_permissions_cache()
        except Exception as e:
            print(f"Erreur sauvegarde rôles autorisés: {e}")

    def is_authorized(self, member):
        """Vérifier si un membre est autorisé"""
        if not member.guild:
            return False
        
        # Vérifier si le membre a un des rôles autorisés
        for role_id in self.authorized_roles:
            role = member.guild.get_role(int(role_id))
            if role and role in member.roles:
                return True
        
        return False

    @commands.command(name="roles")
    @has_role()
    async def manage_roles(self, ctx, action: str = None, *, role: nextcord.Role = None):
        """
        Gérer les rôles autorisés à utiliser les commandes
        
        Utilisation:
        +roles list                    - Voir les rôles autorisés
        +roles add <@rôle>             - Ajouter un rôle autorisé
        +roles remove <@rôle>          - Retirer un rôle autorisé
        +roles info                    - Informations sur les permissions
        """
        
        if not action:
            return await self.show_roles_help(ctx)
        
        action = action.lower()
        
        if action == "list":
            await self.show_authorized_roles(ctx)
        elif action == "add" and role:
            await self.add_authorized_role(ctx, role)
        elif action == "remove" and role:
            await self.remove_authorized_role(ctx, role)
        elif action == "info":
            await self.show_roles_info(ctx)
        else:
            await self.show_roles_help(ctx)

    async def show_roles_help(self, ctx):
        """Afficher l'aide pour la gestion des rôles"""
        embed = nextcord.Embed(
            title="🔐 Gestion des Rôles Autorisés",
            description="Commandes pour gérer les rôles qui peuvent utiliser les commandes du bot",
            color=0x3498db
        )
        
        embed.add_field(
            name="📋 Commandes disponibles",
            value=(
                "`+roles list` - Voir tous les rôles autorisés\n"
                "`+roles add <@rôle>` - Ajouter un rôle autorisé\n"
                "`+roles remove <@rôle>` - Retirer un rôle autorisé\n"
                "`+roles info` - Informations sur les permissions"
            ),
            inline=False
        )
        
        embed.add_field(
            name="ℹ️ Information",
            value=(
                "Les rôles autorisés peuvent utiliser toutes les commandes du bot.\n"
                "Le rôle principal (ID: 1469665367881420841) ne peut pas être retiré.\n"
                "Les membres avec un rôle autorisé peuvent utiliser : modération, vocal, DM, etc."
            ),
            inline=False
        )
        
        embed.set_footer(text=f"Actuellement {len(self.authorized_roles)} rôle(s) autorisé(s)")
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        
        await ctx.send(embed=embed)

    async def show_authorized_roles(self, ctx):
        """Afficher la liste des rôles autorisés"""
        if not self.authorized_roles:
            embed = nextcord.Embed(
                title="❌ Aucun rôle autorisé",
                description="Aucun rôle n'est configuré comme autorisé",
                color=0xE74C3C
            )
            return await ctx.send(embed=embed)
        
        embed = nextcord.Embed(
            title="🔐 Rôles Autorisés",
            description=f"**{len(self.authorized_roles)}** rôle(s) peuvent utiliser les commandes du bot",
            color=0x2ECC71
        )
        
        # Organiser les rôles par catégorie
        admin_roles = []
        mod_roles = []
        other_roles = []
        
        for role_id in self.authorized_roles:
            role = ctx.guild.get_role(int(role_id))
            if role:
                # Compter les membres avec ce rôle
                member_count = len([m for m in ctx.guild.members if role in m.roles])
                
                role_info = f"• {role.mention} (`{role.id}`)\n  └ **{member_count}** membre(s)"
                
                # Catégoriser selon le nom et la position
                if any(keyword in role.name.lower() for keyword in ["admin", "owner", "founder"]):
                    admin_roles.append(role_info)
                elif any(keyword in role.name.lower() for keyword in ["mod", "modo", "staff", "team"]):
                    mod_roles.append(role_info)
                else:
                    other_roles.append(role_info)
        
        # Afficher les catégories
        if admin_roles:
            embed.add_field(name="👑 Administration", value="\n".join(admin_roles), inline=False)
        
        if mod_roles:
            embed.add_field(name="🛡️ Modération", value="\n".join(mod_roles), inline=False)
        
        if other_roles:
            embed.add_field(name="📋 Autres rôles", value="\n".join(other_roles), inline=False)
        
        embed.add_field(
            name="📊 Statistiques",
            value=f"**Total**: {len(self.authorized_roles)} rôle(s)\n"
                  f"**Membres totaux**: {sum(len([m for m in ctx.guild.members if ctx.guild.get_role(int(role_id)) in m.roles]) for role_id in self.authorized_roles)} membre(s)",
            inline=False
        )
        
        embed.set_footer(text="Utilise +roles add <@rôle> pour ajouter un rôle")
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        
        await ctx.send(embed=embed)

    async def add_authorized_role(self, ctx, role):
        """Ajouter un rôle à la liste des autorisés"""
        role_id = str(role.id)
        
        if role_id in self.authorized_roles:
            embed = nextcord.Embed(
                title="⚠️ Rôle déjà autorisé",
                description=f"{role.mention} est déjà dans la liste des rôles autorisés",
                color=0xF39C12
            )
            return await ctx.send(embed=embed)
        
        self.authorized_roles.append(role_id)
        self.save_authorized_roles()
        
        # Compter les membres
        member_count = len([m for m in ctx.guild.members if role in m.roles])
        
        embed = nextcord.Embed(
            title="✅ Rôle ajouté",
            description=f"{role.mention} a été ajouté à la liste des rôles autorisés",
            color=0x2ECC71
        )
        
        embed.add_field(
            name="📊 Informations",
            value=f"**ID**: `{role.id}`\n"
                  f"**Position**: {role.position}\n"
                  f"**Membres**: {member_count}\n"
                  f"**Couleur**: {role.color}",
            inline=False
        )
        
        embed.add_field(
            name="🎯 Accès accordé",
            value="Les membres avec ce rôle peuvent maintenant utiliser :\n"
                  "• Commandes de modération\n"
                  "• Commandes vocales\n"
                  "• Messages DM massifs\n"
                  "• Gestion des lives TikTok\n"
                  "• Et bien plus !",
            inline=False
        )
        
        embed.add_field(
            name="📈 Statistiques",
            value=f"**{len(self.authorized_roles)}** rôle(s) autorisés au total",
            inline=False
        )
        
        embed.set_footer(text="Les membres devront avoir le rôle pour utiliser les commandes")
        embed.set_thumbnail(url=role.icon.url if role.icon else ctx.guild.icon.url)
        
        await ctx.send(embed=embed)
        
        # Logger l'action
        try:
            from cogs.logs import log_command
            log_command(ctx, "roles_add", f"Rôle: {role.name} ({role.id})")
        except:
            pass

    async def remove_authorized_role(self, ctx, role):
        """Retirer un rôle de la liste des autorisés"""
        role_id = str(role.id)
        
        # Empêcher de retirer le rôle principal
        if role_id == str(AUTHORIZED_ROLE_ID):
            embed = nextcord.Embed(
                title="❌ Action interdite",
                description="Le rôle principal ne peut pas être retiré de la liste des autorisés",
                color=0xE74C3C
            )
            embed.add_field(
                name="🔒 Protection",
                value="Ce rôle est essentiel au fonctionnement du bot et ne peut pas être retiré",
                inline=False
            )
            return await ctx.send(embed=embed)
        
        if role_id not in self.authorized_roles:
            embed = nextcord.Embed(
                title="❌ Rôle non autorisé",
                description=f"{role.mention} n'est pas dans la liste des rôles autorisés",
                color=0xE74C3C
            )
            return await ctx.send(embed=embed)
        
        # Compter les membres avant de retirer
        member_count = len([m for m in ctx.guild.members if role in m.roles])
        
        self.authorized_roles.remove(role_id)
        self.save_authorized_roles()
        
        embed = nextcord.Embed(
            title="✅ Rôle retiré",
            description=f"{role.mention} a été retiré de la liste des rôles autorisés",
            color=0xE74C3C
        )
        
        embed.add_field(
            name="⚠️ Conséquence",
            value=f"**{member_count}** membre(s) perdront l'accès aux commandes du bot",
            inline=False
        )
        
        embed.add_field(
            name="📊 Statistiques",
            value=f"**{len(self.authorized_roles)}** rôle(s) autorisés restants",
            inline=False
        )
        
        embed.set_footer(text="Les membres devront avoir un autre rôle autorisé pour continuer à utiliser les commandes")
        embed.set_thumbnail(url=role.icon.url if role.icon else ctx.guild.icon.url)
        
        await ctx.send(embed=embed)
        
        # Logger l'action
        try:
            from cogs.logs import log_command
            log_command(ctx, "roles_remove", f"Rôle: {role.name} ({role.id}) | Membres affectés: {member_count}")
        except:
            pass

    async def show_roles_info(self, ctx):
        """Afficher des informations détaillées sur les permissions"""
        embed = nextcord.Embed(
            title="📊 Informations sur les Permissions",
            description="Statistiques détaillées sur les rôles autorisés et les permissions",
            color=0x3498db
        )
        
        # Statistiques générales
        total_members = ctx.guild.member_count
        authorized_members = 0
        
        for role_id in self.authorized_roles:
            role = ctx.guild.get_role(int(role_id))
            if role:
                authorized_members += len([m for m in ctx.guild.members if role in m.roles])
        
        # Éviter les doublons
        unique_authorized = len(set(
            m for role_id in self.authorized_roles 
            for m in ctx.guild.members 
            if (role := ctx.guild.get_role(int(role_id))) and role in m.roles
        ))
        
        embed.add_field(
            name="👥 Statistiques des membres",
            value=f"**Total membres**: {total_members}\n"
                  f"**Avec accès**: {unique_authorized}\n"
                  f"**Sans accès**: {total_members - unique_authorized}\n"
                  f"**Pourcentage**: {(unique_authorized/total_members*100):.1f}%",
            inline=False
        )
        
        embed.add_field(
            name="🔐 Rôles autorisés",
            value=f"**Nombre**: {len(self.authorized_roles)}\n"
                  f"**Principal**: <@&{AUTHORIZED_ROLE_ID}> (non retirable)",
            inline=False
        )
        
        # Liste des commandes disponibles
        commands_list = (
            "🛡️ **Modération**: warn, kick, ban, mute, timeout, clear\n"
            "🎤 **Vocal**: déplacer, équilibrer, stats_vocal\n"
            "📬 **Communication**: dmall, dmtest\n"
            "📱 **Social**: live, finduser, find\n"
            "🔒 **Admin**: whitelist, logs_setup, embed"
        )
        
        embed.add_field(
            name="⚡ Commandes disponibles",
            value=commands_list,
            inline=False
        )
        
        # Rôles les plus puissants
        role_hierarchy = []
        for role_id in self.authorized_roles:
            role = ctx.guild.get_role(int(role_id))
            if role:
                role_hierarchy.append((role.position, role.name, role.mention))
        
        role_hierarchy.sort(reverse=True)
        top_roles = role_hierarchy[:5]
        
        if top_roles:
            roles_text = "\n".join([f"{i+1}. {mention} (Position: {pos})" for i, (pos, name, mention) in enumerate(top_roles)])
            embed.add_field(
                name="👑 Rôles les plus hauts",
                value=roles_text,
                inline=False
            )
        
        embed.set_footer(text="Utilise +roles list pour voir la liste complète")
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        
        await ctx.send(embed=embed)

    @commands.command(name="checkperms")
    async def check_permissions(self, ctx, member: nextcord.Member = None):
        """
        Vérifier si un membre a accès aux commandes du bot
        
        Utilisation:
        +checkperms              - Vérifier vos permissions
        +checkperms @membre     - Vérifier les permissions d'un membre
        """
        
        if member is None:
            member = ctx.author
        
        is_auth = self.is_authorized(member)
        
        if is_auth:
            # Trouver quels rôles donnent l'accès
            access_roles = []
            for role_id in self.authorized_roles:
                role = ctx.guild.get_role(int(role_id))
                if role and role in member.roles:
                    access_roles.append(role)
            
            embed = nextcord.Embed(
                title="✅ Accès autorisé",
                description=f"{member.mention} **peut utiliser** les commandes du bot",
                color=0x2ECC71
            )
            
            if access_roles:
                roles_text = "\n".join([f"• {role.mention}" for role in access_roles])
                embed.add_field(
                    name="🔐 Rôles donnant l'accès",
                    value=roles_text,
                    inline=False
                )
            
            embed.add_field(
                name="⚡ Commandes disponibles",
                value="Modération • Vocal • DM • Social • Admin",
                inline=False
            )
            
        else:
            embed = nextcord.Embed(
                title="❌ Accès refusé",
                description=f"{member.mention} **ne peut pas utiliser** les commandes du bot",
                color=0xE74C3C
            )
            
            embed.add_field(
                name="🔒 Raison",
                value="Aucun rôle autorisé n'a été trouvé",
                inline=False
            )
            
            embed.add_field(
                name="💡 Solution",
                value="Contactez un administrateur pour obtenir un rôle autorisé",
                inline=False
            )
        
        embed.set_footer(text=f"Vérifié par {ctx.author.name}")
        embed.set_thumbnail(url=member.display_avatar.url)
        
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(RoleManager(bot))
