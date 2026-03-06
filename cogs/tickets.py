import nextcord
from nextcord.ext import commands
import datetime
import json
import os

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_tickets = {}
        self.ensure_data_files()
    
    def ensure_data_files(self):
        """Créer les fichiers de données nécessaires"""
        os.makedirs("data", exist_ok=True)
        os.makedirs("data/tickets", exist_ok=True)
        
        if not os.path.exists("data/tickets_config.json"):
            with open("data/tickets_config.json", "w") as f:
                json.dump({
                    "ticket_channel": None,
                    "support_role": None,
                    "category_id": None,
                    "enabled": True
                }, f, indent=2)
    
    @commands.command(name="ticket")
    async def ticket(self, ctx, *, reason: str = "Aucune raison spécifiée"):
        """Créer un ticket de support"""
        try:
            # Vérifier si l'utilisateur a déjà un ticket
            if ctx.author.id in self.active_tickets:
                return await ctx.send("❌ Tu as déjà un ticket ouvert.")
            
            # Vérifier si le système est activé
            with open("data/tickets_config.json", "r") as f:
                config = json.load(f)
            
            if not config.get("enabled", True):
                return await ctx.send("❌ Le système de tickets est désactivé.")
            
            guild = ctx.guild
            
            # Trouver la catégorie
            category = None
            if config.get("category_id"):
                category = guild.get_channel(config["category_id"])
            
            # Créer le salon de ticket
            ticket_channel = await guild.create_text_channel(
                name=f"ticket-{ctx.author.name}",
                category=category,
                reason=f"Ticket créé par {ctx.author.name}"
            )
            
            # Configurer les permissions
            await ticket_channel.set_permissions(ctx.author, read_messages=True, send_messages=True)
            await ticket_channel.set_permissions(guild.me, read_messages=True, send_messages=True)
            await ticket_channel.set_permissions(guild.default_role, read_messages=False)
            
            # Donner l'accès au rôle de support
            support_role_id = config.get("support_role")
            if support_role_id:
                support_role = guild.get_role(support_role_id)
                if support_role:
                    await ticket_channel.set_permissions(support_role, read_messages=True, send_messages=True)
            
            # Stocker le ticket
            self.active_tickets[ctx.author.id] = {
                "channel_id": ticket_channel.id,
                "reason": reason,
                "created_at": datetime.datetime.now().isoformat()
            }
            
            # Message dans le salon de ticket
            ticket_embed = nextcord.Embed(
                title="🎫 Nouveau Ticket",
                description=f"**Créé par:** {ctx.author.mention}\n**Raison:** {reason}",
                color=0x3498db,
                timestamp=ctx.message.created_at
            )
            ticket_embed.add_field(
                name="🔧 Actions",
                value="Utilise `+close` pour fermer ce ticket\nUtilise `+add <membre>` pour ajouter quelqu'un",
                inline=False
            )
            ticket_embed.set_footer(text="Un membre du staff viendra vous aider bientôt.")
            
            await ticket_channel.send(f"{ctx.author.mention}", embed=ticket_embed)
            
            # Confirmation
            confirm_embed = nextcord.Embed(
                title="✅ Ticket Créé",
                description=f"Ton ticket a été créé dans {ticket_channel.mention}",
                color=0x2ecc71
            )
            await ctx.send(embed=confirm_embed)
            
            # Notifier le rôle de support
            if support_role_id:
                support_role = guild.get_role(support_role_id)
                if support_role:
                    notification_embed = nextcord.Embed(
                        title="🎫 Nouveau Ticket",
                        description=f"**Nouveau ticket de:** {ctx.author.mention}\n**Raison:** {reason}\n**Salon:** {ticket_channel.mention}",
                        color=0xe74c3c,
                        timestamp=datetime.datetime.now()
                    )
                    
                    # Envoyer dans le canal de tickets si configuré
                    ticket_channel_id = config.get("ticket_channel")
                    if ticket_channel_id:
                        notif_channel = guild.get_channel(ticket_channel_id)
                        if notif_channel:
                            await notif_channel.send(f"{support_role.mention}", embed=notification_embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="close")
    async def close(self, ctx):
        """Fermer un ticket"""
        try:
            # Vérifier si c'est un salon de ticket
            ticket_found = None
            for user_id, ticket_data in self.active_tickets.items():
                if ticket_data["channel_id"] == ctx.channel.id:
                    ticket_found = (user_id, ticket_data)
                    break
            
            if not ticket_found:
                return await ctx.send("❌ Ce n'est pas un salon de ticket.")
            
            user_id, ticket_data = ticket_found
            
            # Vérifier les permissions
            if ctx.author.id != user_id and not ctx.author.guild_permissions.manage_channels:
                return await ctx.send("❌ Tu ne peux pas fermer ce ticket.")
            
            # Créer un transcript
            transcript = await self.create_transcript(ctx.channel, ticket_data)
            
            # Envoyer le transcript à l'utilisateur si possible
            ticket_user = ctx.guild.get_member(user_id)
            if ticket_user:
                try:
                    await ticket_user.send(f"📋 **Transcript de ton ticket:**\n\n{transcript}")
                except:
                    pass
            
            # Supprimer le salon
            await ctx.channel.delete(reason="Ticket fermé")
            
            # Retirer de la liste active
            del self.active_tickets[user_id]
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="add")
    async def add(self, ctx, member: nextcord.Member):
        """Ajouter un membre au ticket"""
        try:
            # Vérifier si c'est un salon de ticket
            ticket_found = None
            for user_id, ticket_data in self.active_tickets.items():
                if ticket_data["channel_id"] == ctx.channel.id:
                    ticket_found = (user_id, ticket_data)
                    break
            
            if not ticket_found:
                return await ctx.send("❌ Ce n'est pas un salon de ticket.")
            
            user_id, ticket_data = ticket_found
            
            # Vérifier les permissions
            if ctx.author.id != user_id and not ctx.author.guild_permissions.manage_channels:
                return await ctx.send("❌ Tu ne peux pas ajouter de membres à ce ticket.")
            
            # Ajouter les permissions au membre
            await ctx.channel.set_permissions(member, read_messages=True, send_messages=True)
            
            embed = nextcord.Embed(
                title="✅ Membre Ajouté",
                description=f"{member.mention} a été ajouté au ticket.",
                color=0x2ecc71,
                timestamp=datetime.datetime.now()
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @commands.command(name="remove")
    async def remove(self, ctx, member: nextcord.Member):
        """Retirer un membre du ticket"""
        try:
            # Vérifier si c'est un salon de ticket
            ticket_found = None
            for user_id, ticket_data in self.active_tickets.items():
                if ticket_data["channel_id"] == ctx.channel.id:
                    ticket_found = (user_id, ticket_data)
                    break
            
            if not ticket_found:
                return await ctx.send("❌ Ce n'est pas un salon de ticket.")
            
            user_id, ticket_data = ticket_found
            
            # Vérifier les permissions
            if ctx.author.id != user_id and not ctx.author.guild_permissions.manage_channels:
                return await ctx.send("❌ Tu ne peux pas retirer de membres de ce ticket.")
            
            # Ne pas retirer le créateur du ticket
            if member.id == user_id:
                return await ctx.send("❌ Tu ne peux pas retirer le créateur du ticket.")
            
            # Retirer les permissions du membre
            await ctx.channel.set_permissions(member, read_messages=False, send_messages=False)
            
            embed = nextcord.Embed(
                title="✅ Membre Retiré",
                description=f"{member.mention} a été retiré du ticket.",
                color=0xe74c3c,
                timestamp=datetime.datetime.now()
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    async def create_transcript(self, channel, ticket_data):
        """Créer un transcript du ticket"""
        try:
            messages = []
            async for message in channel.history(limit=None, oldest_first=True):
                if not message.author.bot:
                    messages.append(f"[{message.created_at.strftime('%H:%M:%S')}] {message.author.name}: {message.content}")
            
            transcript = f"📋 **TICKET TRANSCRIPT**\n\n"
            transcript += f"**Créé par:** <@{ticket_data['created_by']}>\n"
            transcript += f"**Raison:** {ticket_data['reason']}\n"
            transcript += f"**Créé le:** {ticket_data['created_at']}\n"
            transcript += f"**Fermé le:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            transcript += "--- MESSAGES ---\n\n"
            transcript += "\n".join(messages)
            
            return transcript
            
        except Exception as e:
            return f"Erreur lors de la création du transcript: {e}"
    
    @commands.command(name="ticketconfig")
    @commands.has_permissions(administrator=True)
    async def ticketconfig(self, ctx):
        """Voir la configuration des tickets"""
        try:
            with open("data/tickets_config.json", "r") as f:
                config = json.load(f)
            
            embed = nextcord.Embed(
                title="⚙️ Configuration des Tickets",
                description="Configuration actuelle du système de tickets:",
                color=0x3498db,
                timestamp=datetime.datetime.now()
            )
            
            # Canal de notification
            ticket_channel = ctx.guild.get_channel(config.get("ticket_channel"))
            embed.add_field(
                name="📢 Canal Notification", 
                value=ticket_channel.mention if ticket_channel else "Non défini", 
                inline=True
            )
            
            # Rôle de support
            support_role = ctx.guild.get_role(config.get("support_role"))
            embed.add_field(
                name="🛡️ Rôle Support", 
                value=support_role.mention if support_role else "Non défini", 
                inline=True
            )
            
            # Catégorie
            category = ctx.guild.get_channel(config.get("category_id"))
            embed.add_field(
                name="📁 Catégorie", 
                value=category.name if category else "Non défini", 
                inline=True
            )
            
            # Statut
            status = "✅ Activé" if config.get("enabled", True) else "❌ Désactivé"
            embed.add_field(
                name="🔧 Statut", 
                value=status, 
                inline=True
            )
            
            # Tickets actifs
            embed.add_field(
                name="🎫 Tickets Actifs", 
                value=str(len(self.active_tickets)), 
                inline=True
            )
            
            embed.set_footer(text=f"Demandé par {ctx.author.name}")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")

def setup(bot):
    bot.add_cog(Tickets(bot))
