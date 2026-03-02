import nextcord
from nextcord.ext import commands
import os
import json

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Envoyer un message d'arrivée quand un membre rejoint le serveur"""
        
        # Créer l'embed d'arrivée
        embed = nextcord.Embed(
            title=f"👋 Bienvenue {member.name} !",
            description=f"Tu es notre **{len(member.guild.members)}ème** membre !",
            color=0x3498db,
            timestamp=member.joined_at
        )
        
        # Ajouter l'information sur qui a invité
        # Note: Discord ne fournit plus cette information directement, donc on utilise un message générique
        embed.add_field(
            name="🎉 Rejoins-nous !",
            value=f"Nous sommes ravis de t'accueillir sur **{member.guild.name}** !",
            inline=False
        )
        
        # Thumbnail avec l'avatar du membre
        embed.set_thumbnail(url=member.display_avatar.url)
        
        # Image de profil du bot en haut à droite (author)
        embed.set_author(
            name="𝐒𝐭𝐚𝐫𝐊𝟗𝟐☆🇵🇸",
            icon_url=self.bot.user.display_avatar.url if self.bot.user.avatar else None
        )
        
        # Footer avec le nom du bot
        embed.set_footer(
            text="made by 𝐒𝐭𝐚𝐫𝐊𝟗𝟐☆🇵🇸",
            icon_url=self.bot.user.display_avatar.url if self.bot.user.avatar else None
        )
        
        # Icône du serveur comme thumbnail principale
        if member.guild.icon:
            embed.set_thumbnail(url=member.guild.icon.url)
        
        # Envoyer dans le channel général (ou un channel de bienvenue configuré)
        # Tu peux modifier l'ID du channel de bienvenue ici
        welcome_channel_id = 1469768104786657534  # Mets l'ID du channel de bienvenue ici
        
        if welcome_channel_id:
            channel = self.bot.get_channel(welcome_channel_id)
            if channel:
                await channel.send(embed=embed)
        else:
            # Si pas de channel configuré, essayer de trouver un channel "général" ou "welcome"
            for channel in member.guild.text_channels:
                if "général" in channel.name.lower() or "general" in channel.name.lower() or "welcome" in channel.name.lower():
                    await channel.send(embed=embed)
                    break
        
        # Envoyer un DM au nouveau membre
        try:
            # Créer le lien d'invitation (illimité et n'expire pas)
            invite = await member.guild.create_invite(max_uses=0, max_age=0, unique=False)
            
            # Envoyer un message normal (pas un embed)
            message = f"🍃 Bienvenue {member.mention} sur {member.guild.name} !\n\nVoici un lien du serveur si tu quittes sans faire exprès :\n{invite.url}"
            
            await member.send(message)
        except nextcord.Forbidden:
            # Le membre a désactivé les DMs, on ignore silencieusement
            pass
        except Exception as e:
            # Autre erreur (pas de permissions pour créer une invitation, etc.)
            print(f"[DM Welcome] Erreur: {e}")

def setup(bot):
    bot.add_cog(Welcome(bot))
