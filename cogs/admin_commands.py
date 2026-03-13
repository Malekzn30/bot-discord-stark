import nextcord
from nextcord.ext import commands
import config
import os
import json

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def cogstatus(self, ctx):
        """Voir le statut des cogs"""
        cog_manager = self.bot.cog_manager
        if not cog_manager:
            return await ctx.send("❌ Gestionnaire de cogs non initialisé")
        
        status = cog_manager.get_cog_status()
        
        embed = nextcord.Embed(
            title="⚙️ Statut des Cogs",
            description=f"**Cogs chargés:** {status['total_loaded']}/{status['total_available']}",
            color=0x3498db
        )
        
        embed.add_field(name="🟢 Chargés", value=", ".join(status['loaded'])[:500], inline=False)
        embed.add_field(name="🔴 Désactivés", value=", ".join(status['disabled']) or "Aucun", inline=False)
        
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def loadcog(self, ctx, cog_name: str):
        """Charger un cog spécifique"""
        cog_manager = self.bot.cog_manager
        if not cog_manager:
            return await ctx.send("❌ Gestionnaire de cogs non initialisé")
        
        success = await cog_manager.load_cog_on_demand(cog_name)
        
        if success:
            await ctx.send(f"✅ Cog `{cog_name}` chargé avec succès")
        else:
            await ctx.send(f"❌ Impossible de charger le cog `{cog_name}`")

    @commands.command()
    @commands.is_owner()
    async def unloadcog(self, ctx, cog_name: str):
        """Décharger un cog spécifique"""
        cog_manager = self.bot.cog_manager
        if not cog_manager:
            return await ctx.send("❌ Gestionnaire de cogs non initialisé")
        
        success = await cog_manager.unload_cog(cog_name)
        
        if success:
            await ctx.send(f"✅ Cog `{cog_name}` déchargé avec succès")
        else:
            await ctx.send(f"❌ Impossible de décharger le cog `{cog_name}`")

    @commands.command()
    @commands.is_owner()
    async def reloadcog(self, ctx, cog_name: str):
        """Recharger un cog spécifique"""
        cog_manager = self.bot.cog_manager
        if not cog_manager:
            return await ctx.send("❌ Gestionnaire de cogs non initialisé")
        
        success = await cog_manager.reload_cog(cog_name)
        
        if success:
            await ctx.send(f"✅ Cog `{cog_name}` rechargé avec succès")
        else:
            await ctx.send(f"❌ Impossible de recharger le cog `{cog_name}`")

    @commands.command()
    @commands.is_owner()
    async def ignoredchannels(self, ctx):
        """Gérer les salons ignorés par le bot"""
        embed = nextcord.Embed(
            title="🔇 Salons Ignorés",
            description="Configuration des salons où le bot ne répondra pas",
            color=0x3498db
        )
        
        # Afficher les salons ignorés
        if config.IGNORED_CHANNELS:
            ignored_text = []
            for ignored in config.IGNORED_CHANNELS:
                if isinstance(ignored, int):
                    ignored_text.append(f"ID: `{ignored}`")
                else:
                    ignored_text.append(f"Nom: `{ignored}`")
            embed.add_field(name="🚫 Salons Ignorés", value="\n".join(ignored_text), inline=False)
        else:
            embed.add_field(name="🚫 Salons Ignorés", value="Aucun salon ignoré", inline=False)
        
        # Afficher les salons autorisés (si configuré)
        if config.ALLOWED_CHANNELS:
            allowed_text = []
            for allowed in config.ALLOWED_CHANNELS:
                if isinstance(allowed, int):
                    allowed_text.append(f"ID: `{allowed}`")
                else:
                    allowed_text.append(f"Nom: `{allowed}`")
            embed.add_field(name="✅ Salons Autorisés Uniquement", value="\n".join(allowed_text), inline=False)
        else:
            embed.add_field(name="✅ Mode", value="Tous les salons autorisés sauf ignorés", inline=False)
        
        embed.add_field(
            name="📝 Comment Modifier",
            value="Édite `config.py` et modifie les listes:\n- `IGNORED_CHANNELS` - Salons à ignorer\n- `ALLOWED_CHANNELS` - Salons autorisés uniquement",
            inline=False
        )
        
        embed.set_footer(text="Le bot doit être redémarré pour appliquer les changements")
        
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def reloadconfig(self, ctx):
        """Recharge la configuration du bot"""
        try:
            import importlib
            importlib.reload(config)
            
            await ctx.send("✅ Configuration rechargée avec succès!")
            
            # Afficher les nouvelles configurations
            embed = nextcord.Embed(
                title="⚙️ Configuration Rechargée",
                color=0x2ecc71
            )
            
            embed.add_field(name="🚫 Salons Ignorés", value=f"{len(config.IGNORED_CHANNELS)} salons", inline=True)
            embed.add_field(name="✅ Salons Autorisés", value=f"{len(config.ALLOWED_CHANNELS)} salons", inline=True)
            embed.add_field(name="🔄 Auto-Réactions", value=f"{len(config.AUTO_REACT_CHANNELS)} salons", inline=True)
            embed.add_field(name="🎯 Mode", value="Restreint" if config.ALLOWED_CHANNELS else "Ouvert", inline=True)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur lors du rechargement: {e}")

    @commands.command()
    @commands.is_owner()
    async def testchannel(self, ctx):
        """Teste si le bot peut répondre dans le salon actuel"""
        from bot import is_channel_allowed
        
        if is_channel_allowed(ctx.channel):
            await ctx.send("✅ Ce salon est **autorisé** - Le bot peut répondre ici")
        else:
            await ctx.send("❌ Ce salon est **ignoré** - Le bot ne répondra pas ici")
            
            # Donner des informations sur pourquoi
            channel_id = ctx.channel.id
            channel_name = ctx.channel.name.lower()
            
            reasons = []
            for ignored in config.IGNORED_CHANNELS:
                if isinstance(ignored, int) and ignored == channel_id:
                    reasons.append(f"ID `{ignored}` est dans la liste ignorée")
                elif isinstance(ignored, str) and ignored.lower() == channel_name:
                    reasons.append(f"Nom `{ignored}` est dans la liste ignorée")
            
            if config.ALLOWED_CHANNELS:
                is_allowed = False
                for allowed in config.ALLOWED_CHANNELS:
                    if isinstance(allowed, int) and allowed == channel_id:
                        is_allowed = True
                        break
                    elif isinstance(allowed, str) and allowed.lower() == channel_name:
                        is_allowed = True
                        break
                if not is_allowed:
                    reasons.append("Le salon n'est pas dans la liste autorisée")
            
            if reasons:
                await ctx.send(f"📝 **Raison(s):**\n" + "\n".join(reasons))

def setup(bot):
    bot.add_cog(AdminCommands(bot))
