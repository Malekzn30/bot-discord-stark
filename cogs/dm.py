import nextcord
from nextcord.ext import commands
import datetime
import asyncio

class DM(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="dm")
    @commands.has_permissions(administrator=True)
    async def dm(self, ctx, member: nextcord.Member, *, message: str):
        """Envoyer un message privé à un membre"""
        try:
            embed = nextcord.Embed(
                title="📬 Message Privé",
                description=message,
                color=0x3498db,
                timestamp=datetime.datetime.now()
            )
            embed.add_field(name="👤 Envoyé par", value=ctx.author.mention, inline=True)
            embed.add_field(name="🏢 Serveur", value=ctx.guild.name, inline=True)
            embed.set_footer(text="Ceci est un message officiel du staff")
            
            await member.send(embed=embed)
            
            confirm_embed = nextcord.Embed(
                title="✅ Message Envoyé",
                description=f"**Message envoyé à:** {member.mention}",
                color=0x2ecc71,
                timestamp=datetime.datetime.now()
            )
            await ctx.send(embed=confirm_embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="dmall")
    @commands.has_permissions(administrator=True)
    async def dmall(self, ctx, *, message: str):
        """Envoyer un message à tous les membres du serveur"""
        confirm_msg = await ctx.send("📤 Envoi du message à tous les membres...")
        
        members = ctx.guild.members
        sent = 0
        failed = 0
        
        embed = nextcord.Embed(
            title="📬 Message du Serveur",
            description=message,
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="👤 Envoyé par", value=ctx.author.mention, inline=True)
        embed.add_field(name="🏢 Serveur", value=ctx.guild.name, inline=True)
        embed.set_footer(text="Ceci est un message officiel du staff")
        
        for member in members:
            if member.bot:
                continue
            
            try:
                await member.send(embed=embed)
                sent += 1
                await asyncio.sleep(0.1)  # Anti-rate limit
            except:
                failed += 1
        
        result_embed = nextcord.Embed(
            title="📤 Message Massif Envoyé",
            description=f"**Envoyés:** {sent}\n**Échecs:** {failed}\n**Total:** {len(members)}",
            color=0x2ecc71 if failed == 0 else 0xe74c3c,
            timestamp=datetime.datetime.now()
        )
        result_embed.set_footer(text=f"Demandé par {ctx.author.name}")
        
        await confirm_msg.edit(embed=result_embed)
    
    @commands.command(name="dmrole")
    @commands.has_permissions(administrator=True)
    async def dmrole(self, ctx, role: nextcord.Role, *, message: str):
        """Envoyer un message à tous les membres ayant un rôle spécifique"""
        confirm_msg = await ctx.send("📤 Envoi du message aux membres du rôle...")
        
        members_with_role = [member for member in ctx.guild.members if role in member.roles and not member.bot]
        sent = 0
        failed = 0
        
        embed = nextcord.Embed(
            title="📬 Message de Rôle",
            description=message,
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="👤 Envoyé par", value=ctx.author.mention, inline=True)
        embed.add_field(name="🎭 Rôle ciblé", value=role.mention, inline=True)
        embed.add_field(name="🏢 Serveur", value=ctx.guild.name, inline=True)
        embed.set_footer(text="Ceci est un message officiel du staff")
        
        for member in members_with_role:
            try:
                await member.send(embed=embed)
                sent += 1
                await asyncio.sleep(0.1)  # Anti-rate limit
            except:
                failed += 1
        
        result_embed = nextcord.Embed(
            title="📤 Message de Rôle Envoyé",
            description=f"**Rôle:** {role.mention}\n**Envoyés:** {sent}\n**Échecs:** {failed}\n**Total ciblés:** {len(members_with_role)}",
            color=0x2ecc71 if failed == 0 else 0xe74c3c,
            timestamp=datetime.datetime.now()
        )
        result_embed.set_footer(text=f"Demandé par {ctx.author.name}")
        
        await confirm_msg.edit(embed=result_embed)
    
    @commands.command(name="dmcheck")
    @commands.has_permissions(administrator=True)
    async def dmcheck(self, ctx, member: nextcord.Member = None):
        """Vérifier si on peut envoyer un DM à un membre"""
        target = member or ctx.author
        
        try:
            # Essayer d'envoyer un message test
            test_embed = nextcord.Embed(
                title="🧪 Test DM",
                description="Ceci est un message test pour vérifier que les DMs fonctionnent.",
                color=0x3498db,
                timestamp=datetime.datetime.now()
            )
            test_embed.set_footer(text="Message test - Vous pouvez l'ignorer")
            
            await target.send(embed=test_embed)
            
            result_embed = nextcord.Embed(
                title="✅ DM Réussi",
                description=f"**DM envoyé avec succès à:** {target.mention}",
                color=0x2ecc71,
                timestamp=datetime.datetime.now()
            )
            await ctx.send(embed=result_embed)
            
        except Exception as e:
            result_embed = nextcord.Embed(
                title="❌ DM Échoué",
                description=f"**Impossible d'envoyer un DM à:** {target.mention}\n**Erreur:** {str(e)}",
                color=0xe74c3c,
                timestamp=datetime.datetime.now()
            )
            await ctx.send(embed=result_embed)
    
    @commands.command(name="dmstats")
    @commands.has_permissions(administrator=True)
    async def dmstats(self, ctx):
        """Statistiques des DMs du serveur"""
        members = ctx.guild.members
        total_members = len([m for m in members if not m.bot])
        
        embed = nextcord.Embed(
            title="📊 Statistiques DM",
            description="Statistiques des messages privés du serveur:",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="👥 Total membres", value=str(total_members), inline=True)
        embed.add_field(name="🤖 Bots", value=str(len([m for m in members if m.bot])), inline=True)
        embed.add_field(name="📬 Membres ciblables", value=str(total_members), inline=True)
        
        embed.add_field(name="💡 Conseil", value="Utilise `+dmcheck` pour tester si un membre peut recevoir des DMs", inline=False)
        
        embed.set_footer(text=f"Demandé par {ctx.author.name}")
        
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(DM(bot))
