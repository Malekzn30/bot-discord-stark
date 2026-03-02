import nextcord
from nextcord.ext import commands
import datetime
import os
import json
import asyncio

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ensure_data_directory()

    def ensure_data_directory(self):
        """S'assurer que le répertoire data/tickets existe"""
        os.makedirs("data/tickets", exist_ok=True)

    @commands.command(name="ticket")
    async def create_ticket(self, ctx, *, reason: str = "Aucune raison spécifiée"):
        """Créer un ticket de support"""
        
        # Vérifier si l'utilisateur a déjà un ticket ouvert
        tickets_file = f"data/tickets/{ctx.guild.id}.json"
        
        if os.path.exists(tickets_file):
            with open(tickets_file, 'r', encoding='utf-8') as f:
                tickets = json.load(f)
        else:
            tickets = []
        
        # Vérifier si l'utilisateur a déjà un ticket ouvert
        user_tickets = [t for t in tickets if t.get("user_id") == ctx.author.id and t.get("status") == "open"]
        
        if user_tickets:
            return await ctx.send("❌ Tu as déjà un ticket ouvert !")
        
        # Créer la catégorie de tickets si elle n'existe pas
        ticket_category = nextcord.utils.get(ctx.guild.categories, name="🎫 Tickets")
        if not ticket_category:
            # Créer la catégorie
            overwrites = {
                ctx.guild.default_role: nextcord.PermissionOverwrite(
                    read_messages=False,
                    send_messages=False,
                    connect=False
                ),
                ctx.guild.me: nextcord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True,
                    connect=True,
                    manage_channels=True
                )
            }
            
            ticket_category = await ctx.guild.create_category(
                name="🎫 Tickets",
                overwrites=overwrites,
                position=0
            )
        
        # Créer le salon de ticket
        ticket_number = len(tickets) + 1
        channel_name = f"ticket-{ticket_number:04d}"
        
        overwrites = {
            ctx.author: nextcord.PermissionOverwrite(
                read_messages=True,
                send_messages=True,
                attach_files=True,
                embed_links=True
            ),
            ctx.guild.default_role: nextcord.PermissionOverwrite(
                read_messages=False,
                send_messages=False
            ),
            ctx.guild.me: nextcord.PermissionOverwrite(
                read_messages=True,
                send_messages=True,
                manage_channels=True
            )
        }
        
        ticket_channel = await ticket_category.create_text_channel(
            name=channel_name,
            overwrites=overwrites
        )
        
        # Ajouter le ticket à la base de données
        new_ticket = {
            "ticket_id": ticket_number,
            "channel_id": ticket_channel.id,
            "user_id": ctx.author.id,
            "user_name": ctx.author.name,
            "user_mention": ctx.author.mention,
            "reason": reason,
            "status": "open",
            "created_at": datetime.datetime.now().isoformat(),
            "messages": []
        }
        
        tickets.append(new_ticket)
        
        # Sauvegarder
        with open(tickets_file, 'w', encoding='utf-8') as f:
            json.dump(tickets, f, indent=2, ensure_ascii=False)
        
        # Envoyer le message de confirmation
        embed = nextcord.Embed(
            title="🎫 Ticket Créé",
            description=f"Ton ticket **#{ticket_number}** a été créé !",
            color=0x2ECC71,
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(
            name="📝 Raison",
            value=reason,
            inline=False
        )
        
        embed.add_field(
            name="💬 Salon",
            value=f"{ticket_channel.mention}",
            inline=False
        )
        
        embed.set_footer(text="Utilise +close pour fermer le ticket")
        await ctx.send(embed=embed)
        
        # Message dans le salon de ticket
        ticket_embed = nextcord.Embed(
            title="🎫 Nouveau Ticket",
            description=f"**Ticket #{ticket_number}**\n\n**Utilisateur:** {ctx.author.mention}\n**Raison:** {reason}",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        
        ticket_embed.add_field(
            name="📋 Instructions",
            value="Attends qu'un membre du staff réponde à ton ticket.\nUtilise `+close` pour fermer le ticket.",
            inline=False
        )
        
        await ticket_channel.send(embed=ticket_embed)
        
        # Notifier le staff
        staff_role = ctx.guild.get_role(AUTHORIZED_ROLE_ID)
        if staff_role:
            notification_embed = nextcord.Embed(
                title="🎫 Nouveau Ticket",
                description=f"**Ticket #{ticket_number}** créé par {ctx.author.mention}",
                color=0xE74C3C,
                timestamp=datetime.datetime.now()
            )
            
            notification_embed.add_field(
                name="📝 Raison",
                value=reason,
                inline=False
            )
            
            notification_embed.add_field(
                name="🔗 Lien",
                value=f"[Accéder au ticket]({ticket_channel.mention})",
                inline=False
            )
            
            # Envoyer la notification au staff
            try:
                await ctx.author.send(f"✅ Ton ticket #{ticket_number} a été créé ! {ticket_channel.mention}")
            except:
                pass

    @commands.command(name="close")
    async def close_ticket(self, ctx):
        """Fermer le ticket actuel"""
        
        # Vérifier si l'utilisateur est dans un salon de ticket
        if not ctx.channel.name.startswith("ticket-"):
            return await ctx.send("❌ Cette commande n'est utilisable que dans les salons de tickets.")
        
        tickets_file = f"data/tickets/{ctx.guild.id}.json"
        
        if not os.path.exists(tickets_file):
            return await ctx.send("❌ Aucun ticket trouvé.")
        
        with open(tickets_file, 'r', encoding='utf-8') as f:
            tickets = json.load(f)
        
        # Trouver le ticket correspondant
        ticket = None
        for t in tickets:
            if t.get("channel_id") == ctx.channel.id and t.get("status") == "open":
                ticket = t
                break
        
        if not ticket:
            return await ctx.send("❌ Ce ticket n'existe pas ou est déjà fermé.")
        
        # Vérifier les permissions
        staff_role = ctx.guild.get_role(AUTHORIZED_ROLE_ID)
        if staff_role not in ctx.author.roles:
            return await ctx.send("❌ Seul le staff peut fermer les tickets.")
        
        # Fermer le ticket
        ticket["status"] = "closed"
        ticket["closed_at"] = datetime.datetime.now().isoformat()
        ticket["closed_by"] = ctx.author.mention
        
        # Sauvegarder
        with open(tickets_file, 'w', encoding='utf-8') as f:
            json.dump(tickets, f, indent=2, ensure_ascii=False)
        
        # Archiver le salon
        await ctx.channel.edit(name=f"closed-{ticket['ticket_id']:04d}")
        
        # Message de fermeture
        embed = nextcord.Embed(
            title="🔒 Ticket Fermé",
            description=f"Le ticket **#{ticket['ticket_id']}** a été fermé par {ctx.author.mention}",
            color=0xE74C3C,
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(
            name="📝 Raison originale",
            value=ticket.get("reason", "Non spécifiée"),
            inline=False
        )
        
        embed.add_field(
            name="⏰ Durée",
            value=f"{hours}h {minutes}min",
            inline=False
        )
        
        await ctx.send(embed=embed)
        
        # Supprimer le salon après 5 minutes
        await asyncio.sleep(300)
        try:
            await ctx.channel.delete()
        except:
            pass

    @commands.command(name="tickets")
    @commands.has_permissions(administrator=True)
    async def list_tickets(self, ctx, status: str = "open"):
        """Lister tous les tickets"""
        
        tickets_file = f"data/tickets/{ctx.guild.id}.json"
        
        if not os.path.exists(tickets_file):
            return await ctx.send("❌ Aucun ticket trouvé.")
        
        with open(tickets_file, 'r', encoding='utf-8') as f:
            tickets = json.load(f)
        
        # Filtrer par statut
        if status.lower() in ["open", "closed"]:
            tickets = [t for t in tickets if t.get("status") == status.lower()]
        
        if not tickets:
            return await ctx.send(f"❌ Aucun ticket {status} trouvé.")
        
        embed = nextcord.Embed(
            title=f"🎫 Tickets {status.title()}s",
            description=f"Liste des tickets {status.lower()}s",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        
        for ticket in tickets[-10:]:  # Limiter à 10 tickets
            ticket_id = ticket.get("ticket_id", "N/A")
            user_mention = ticket.get("user_mention", "N/A")
            reason = ticket.get("reason", "N/A")
            created_at = ticket.get("created_at", "N/A")
            status_emoji = "🟢" if ticket.get("status") == "open" else "🔴"
            
            embed.add_field(
                name=f"{status_emoji} Ticket #{ticket_id}",
                value=f"**Utilisateur:** {user_mention}\n**Raison:** {reason}\n**Créé le:** {created_at}",
                inline=False
            )
        
        embed.set_footer(text=f"Total: {len(tickets)} tickets {status.lower()}s")
        await ctx.send(embed=embed)

    @commands.command(name="addstaff")
    @commands.has_permissions(administrator=True)
    async def add_staff(self, ctx, member: nextcord.Member):
        """Ajouter un membre au staff"""
        
        staff_role = ctx.guild.get_role(AUTHORIZED_ROLE_ID)
        if not staff_role:
            return await ctx.send("❌ Rôle de staff non configuré.")
        
        await member.add_roles(staff_role)
        await ctx.send(f"✅ {member.mention} a été ajouté au staff.")

    @commands.command(name="removestaff")
    @commands.has_permissions(administrator=True)
    async def remove_staff(self, ctx, member: nextcord.Member):
        """Retirer un membre du staff"""
        
        staff_role = ctx.guild.get_role(AUTHORIZED_ROLE_ID)
        if not staff_role:
            return await ctx.send("❌ Rôle de staff non configuré.")
        
        if staff_role not in member.roles:
            return await ctx.send(f"❌ {member.mention} n'est pas dans le staff.")
        
        await member.remove_roles(staff_role)
        await ctx.send(f"✅ {member.mention} a été retiré du staff.")

def setup(bot):
    bot.add_cog(Tickets(bot))
