import nextcord
from nextcord.ext import commands
import os
import json
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from cogs.logs import log_welcome

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Envoyer un message d'arrivée quand un membre rejoint le serveur"""
        
        # Logger l'arrivée du membre
        log_welcome(member, "join", f"{member.guild.name} (ID: {member.guild.id})")
        
        # Récupérer le nombre correct de membres (tous les membres, y compris les bots)
        total_members = len(member.guild.members)
        
        # Récupérer le nombre de membres humains (exclut les bots)
        human_members = len([m for m in member.guild.members if not m.bot])
        
        # Logger les statistiques
        log_welcome(member, "member_count", f"Total: {total_members} | Humains: {human_members}")
        
        try:
            # Créer l'embed d'arrivée avec le bon comptage
            embed = nextcord.Embed(
                title=f"👋 Bienvenue {member.name} !",
                description=f"Tu es notre **{human_members}ème** membre humain !",
                color=0x3498db,
                timestamp=member.joined_at
            )
            
            # Ajouter l'information sur le serveur
            embed.add_field(
                name="🎉 Rejoins-nous !",
                value=f"Nous sommes ravis de t'accueillir sur **{member.guild.name}** !",
                inline=False
            )
            
            # Ajouter les statistiques du serveur
            embed.add_field(
                name="📊 Statistiques",
                value=f"👥 Total membres: **{total_members}**\n🤖 Bots: **{total_members - human_members}**\n👤 Humains: **{human_members}**",
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
            welcome_channel_id = 1469768104786657534  # ID du channel de bienvenue
            
            if welcome_channel_id:
                channel = self.bot.get_channel(welcome_channel_id)
                if channel:
                    await channel.send(embed=embed)
                    log_welcome(member, "public_sent", f"{channel.name} (ID: {channel.id})")
                else:
                    log_welcome(member, "public_error", f"Channel {welcome_channel_id} non trouvé")
            else:
                # Si pas de channel configuré, essayer de trouver un channel "général" ou "welcome"
                for channel in member.guild.text_channels:
                    if "général" in channel.name.lower() or "general" in channel.name.lower() or "welcome" in channel.name.lower():
                        await channel.send(embed=embed)
                        log_welcome(member, "public_sent", f"{channel.name} (auto-détection)")
                        break
                else:
                    log_welcome(member, "public_error", "Aucun channel de bienvenue trouvé")
            
        except Exception as e:
            log_welcome(member, "public_error", str(e))
        
        # Envoyer un DM au nouveau membre
        try:
            log_welcome(member, "dm_attempt")
            
            # Créer le lien d'invitation (illimité et n'expire pas)
            invite = await member.guild.create_invite(max_uses=0, max_age=0, unique=False)
            log_welcome(member, "invite_created", invite.url)
            
            # Envoyer un message normal (pas un embed)
            message = f"🍃 Bienvenue {member.mention} sur {member.guild.name} !\n\nVoici un lien du serveur si tu quittes sans faire exprès :\n{invite.url}"
            
            await member.send(message)
            log_welcome(member, "dm_sent")
            
        except nextcord.Forbidden:
            log_welcome(member, "dm_blocked", "DMs désactivés")
            # Le membre a désactivé les DMs, on ignore silencieusement
            pass
        except Exception as e:
            log_welcome(member, "dm_error", str(e))
            # Autre erreur (pas de permissions pour créer une invitation, etc.)
            pass

def setup(bot):
    bot.add_cog(Welcome(bot))
