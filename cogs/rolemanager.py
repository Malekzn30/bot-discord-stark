import nextcord
from nextcord.ext import commands
import datetime
import json
import os

class RoleManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ensure_data_files()
    
    def ensure_data_files(self):
        """Créer les fichiers de données nécessaires"""
        os.makedirs("data", exist_ok=True)
        
        if not os.path.exists("data/role_menus.json"):
            with open("data/role_menus.json", "w") as f:
                json.dump({}, f)
    
    @commands.command(name="role")
    @commands.has_permissions(manage_roles=True)
    async def role(self, ctx, action: str, member: nextcord.Member = None, role: nextcord.Role = None):
        """Gérer les rôles des membres"""
        target = member or ctx.author
        target_role = role or None
        
        if action.lower() == "add":
            if not target_role:
                return await ctx.send("❌ Spécifiez un rôle à ajouter.")
            
            if target_role in target.roles:
                return await ctx.send(f"❌ {target.mention} a déjà le rôle {target_role.mention}")
            
            try:
                await target.add_roles(target_role)
                embed = nextcord.Embed(
                    title="✅ Rôle Ajouté",
                    description=f"**Rôle:** {target_role.mention}\n**Membre:** {target.mention}",
                    color=0x2ecc71,
                    timestamp=datetime.datetime.now()
                )
                await ctx.send(embed=embed)
                
            except Exception as e:
                await ctx.send(f"❌ Erreur: {e}")
        
        elif action.lower() == "remove":
            if not target_role:
                return await ctx.send("❌ Spécifiez un rôle à retirer.")
            
            if target_role not in target.roles:
                return await ctx.send(f"❌ {target.mention} n'a pas le rôle {target_role.mention}")
            
            try:
                await target.remove_roles(target_role)
                embed = nextcord.Embed(
                    title="✅ Rôle Retiré",
                    description=f"**Rôle:** {target_role.mention}\n**Membre:** {target.mention}",
                    color=0xe74c3c,
                    timestamp=datetime.datetime.now()
                )
                await ctx.send(embed=embed)
                
            except Exception as e:
                await ctx.send(f"❌ Erreur: {e}")
        
        elif action.lower() == "info":
            if not target:
                return await ctx.send("❌ Spécifiez un membre.")
            
            embed = nextcord.Embed(
                title=f"🎭 Rôles de {target.name}",
                description=f"**Total:** {len(target.roles)} rôles",
                color=0x3498db,
                timestamp=datetime.datetime.now()
            )
            
            # Afficher les rôles (sauf @everyone)
            role_list = [role.mention for role in target.roles if role.name != "@everyone"]
            if role_list:
                embed.add_field(name="🎭 Rôles", value=", ".join(role_list[:10]), inline=False)
                if len(role_list) > 10:
                    embed.add_field(name="➕ Plus", value=f"...et {len(role_list) - 10} autres", inline=False)
            else:
                embed.add_field(name="🎭 Rôles", value="Aucun rôle spécial", inline=False)
            
            await ctx.send(embed=embed)
        
        else:
            await ctx.send("❌ Actions disponibles: `add`, `remove`, `info`")
    
    @commands.command(name="createrole")
    @commands.has_permissions(manage_roles=True)
    async def createrole(self, ctx, name: str, color: str = "blue"):
        """Créer un nouveau rôle"""
        try:
            # Convertir la couleur
            color_map = {
                "red": 0xe74c3c,
                "green": 0x2ecc71,
                "blue": 0x3498db,
                "yellow": 0xf39c12,
                "purple": 0x9B59B6,
                "orange": 0xe67e22,
                "pink": 0xff69b4,
                "black": 0x2c3e50,
                "white": 0xffffff,
                "gray": 0x95a5a6
            }
            
            role_color = color_map.get(color.lower(), 0x3498db)
            
            # Créer le rôle
            role = await ctx.guild.create_role(
                name=name,
                color=role_color,
                reason=f"Créé par {ctx.author.name}"
            )
            
            embed = nextcord.Embed(
                title="✅ Rôle Créé",
                description=f"**Nom:** {role.mention}\n**Couleur:** {color}",
                color=role_color,
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Créé par {ctx.author.name}")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="deleterole")
    @commands.has_permissions(manage_roles=True)
    async def deleterole(self, ctx, role: nextcord.Role):
        """Supprimer un rôle"""
        try:
            if role.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
                return await ctx.send("❌ Vous ne pouvez pas supprimer ce rôle.")
            
            role_name = role.name
            await role.delete(reason=f"Supprimé par {ctx.author.name}")
            
            embed = nextcord.Embed(
                title="🗑️ Rôle Supprimé",
                description=f"**Rôle:** {role_name}",
                color=0xe74c3c,
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Supprimé par {ctx.author.name}")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="rolemenu")
    @commands.has_permissions(manage_roles=True)
    async def rolemenu(self, ctx, title: str, *role_pairs: str):
        """Créer un menu de rôles avec réactions"""
        try:
            if len(role_pairs) % 2 != 0:
                return await ctx.send("❌ Spécifiez des paires emoji:rôle")
            
            # Parser les paires
            role_data = {}
            for i in range(0, len(role_pairs), 2):
                emoji = role_pairs[i]
                role_name = role_pairs[i+1]
                role = nextcord.utils.get(ctx.guild.roles, name=role_name)
                if role:
                    role_data[emoji] = role.id
            
            if not role_data:
                return await ctx.send("❌ Aucun rôle valide trouvé.")
            
            # Créer l'embed
            embed = nextcord.Embed(
                title=f"🎭 {title}",
                description="Réagissez avec les emojis ci-dessous pour obtenir les rôles correspondants:",
                color=0x3498db,
                timestamp=datetime.datetime.now()
            )
            
            for emoji, role_id in role_data.items():
                role = ctx.guild.get_role(role_id)
                if role:
                    embed.add_field(name=emoji, value=role.mention, inline=True)
            
            embed.set_footer(text="Cliquez sur les réactions pour obtenir/retirer les rôles")
            
            message = await ctx.send(embed=embed)
            
            # Ajouter les réactions
            for emoji in role_data.keys():
                await message.add_reaction(emoji)
            
            # Sauvegarder le menu
            try:
                with open("data/role_menus.json", "r") as f:
                    menus = json.load(f)
                
                menus[str(message.id)] = {
                    "channel_id": ctx.channel.id,
                    "roles": role_data,
                    "author": ctx.author.id
                }
                
                with open("data/role_menus.json", "w") as f:
                    json.dump(menus, f, indent=2)
                    
            except Exception as e:
                print(f"Erreur sauvegarde menu rôles: {e}")
            
            await ctx.send("✅ Menu de rôles créé avec succès!")
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")

def setup(bot):
    bot.add_cog(RoleManager(bot))
