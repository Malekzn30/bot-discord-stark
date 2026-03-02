import nextcord
from nextcord.ext import commands
import asyncio
import datetime
from config import AUTHORIZED_ROLE_ID

def has_role():
    async def predicate(ctx):
        role = ctx.guild.get_role(AUTHORIZED_ROLE_ID)
        return role in ctx.author.roles
    return commands.check(predicate)

class Social(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.live_role_id = 1469682659817951302  # Rôle pour les notifications live
        self.live_announcements = {}  # Pour éviter les doublons

    @commands.command(name="live")
    @has_role()
    async def live_notification(self, ctx, *, message: str = None):
        """
        Annoncer que tu es en live sur TikTok
        
        Utilisation:
        +live "Je suis en live ! Venez nombreux !"
        +live (sans message = message par défaut)
        """
        
        # Vérifier si l'utilisateur a le rôle live
        live_role = ctx.guild.get_role(self.live_role_id)
        if not live_role:
            return await ctx.send("❌ Rôle live non trouvé. Vérifie l'ID du rôle.")
        
        # Message par défaut si aucun n'est fourni
        if not message:
            message = "🔴 **𝑳𝑨𝒁 est en LIVE sur TikTok !** 🔴\n\n🎥 Rejoignez le live maintenant !\n🎉 Venez nombreux pour partager ce moment !"
        else:
            message = f"🔴 **𝑳𝑨𝒁 est en LIVE sur TikTok !** 🔴\n\n{message}"
        
        # Créer l'embed stylé
        embed = nextcord.Embed(
            title="🔴 LIVE TIKTOK 🔴",
            description=message,
            color=0xFF0000,  # Rouge pour le live
            timestamp=datetime.datetime.now()
        )
        
        # Style spécial pour 𝑳𝑨𝒁
        embed.set_author(
            name="𝑳𝑨𝒁",
            icon_url=ctx.author.display_avatar.url if ctx.author.avatar else None
        )
        
        embed.set_thumbnail(url="https://i.imgur.com/7XqJQ5R.png")  # Icône TikTok live
        
        embed.add_field(
            name="🎥 Stream en direct",
            value="📱 **TikTok Live**\n🔗 Rejoignez maintenant !",
            inline=True
        )
        
        embed.add_field(
            name="⏰ Heure de début",
            value=f"<t:{int(datetime.datetime.now().timestamp())}:t>",
            inline=True
        )
        
        embed.set_image(url="https://i.imgur.com/TikTokLiveBanner.png")  # Bannière live
        
        embed.set_footer(
            text="🔴 LIVE EN COURS 🔴",
            icon_url=ctx.guild.icon.url if ctx.guild.icon else None
        )
        
        # Ajouter le rôle live à l'utilisateur
        try:
            await ctx.author.add_roles(live_role)
            await ctx.send(f"✅ Rôle live ajouté à {ctx.author.mention} !")
        except nextcord.Forbidden:
            await ctx.send("❌ Je n'ai pas la permission de gérer les rôles.")
        
        # Envoyer l'annonce dans le channel actuel
        await ctx.send(embed=embed)
        
        # Notifier les membres avec le rôle live (si existant)
        if live_role.members:
            notification = f"🔴 **{ctx.author.mention} est en LIVE !**\n"
            notification += f"📱 Rejoignez le live TikTok maintenant !\n"
            notification += f"🎯 Mention: {', '.join([m.mention for m in live_role.members[:5]])}"
            
            if len(live_role.members) > 5:
                notification += f" et {len(live_role.members) - 5} autres..."
            
            await ctx.send(notification)
        
        # Logger l'action
        try:
            from cogs.logs import log_command
            log_command(ctx, "live", f"Utilisateur: {ctx.author.name} | Message: {message[:50]}...")
        except:
            pass

    @commands.command(name="stoplive")
    @has_role()
    async def stop_live(self, ctx):
        """
        Arrêter le live et retirer le rôle
        """
        live_role = ctx.guild.get_role(self.live_role_id)
        if not live_role:
            return await ctx.send("❌ Rôle live non trouvé.")
        
        if live_role in ctx.author.roles:
            await ctx.author.remove_roles(live_role)
            
            embed = nextcord.Embed(
                title="✅ Live terminé",
                description=f"🎉 **{ctx.author.mention}** a terminé son live !\n\nMerci à tous ceux qui ont assisté !",
                color=0x2ECC71
            )
            
            embed.set_footer(text="À la prochaine fois !")
            await ctx.send(embed=embed)
            
            # Logger l'action
            try:
                from cogs.logs import log_command
                log_command(ctx, "stoplive", f"Utilisateur: {ctx.author.name}")
            except:
                pass
        else:
            await ctx.send("❌ Vous n'avez pas le rôle live.")

    @commands.command(name="finduser")
    async def find_user(self, ctx, *, search: str):
        """
        Chercher des utilisateurs par pseudo
        
        Utilisation:
        +finduser laz
        +finduser Stark
        +finduser "pseudo avec espaces"
        """
        
        if len(search) < 2:
            return await ctx.send("❌ La recherche doit contenir au moins 2 caractères.")
        
        # Chercher les membres correspondants
        found_members = []
        search_lower = search.lower()
        
        for member in ctx.guild.members:
            if search_lower in member.display_name.lower() or search_lower in member.name.lower():
                found_members.append(member)
        
        if not found_members:
            embed = nextcord.Embed(
                title="🔍 Recherche d'utilisateurs",
                description=f"Aucun membre trouvé pour : **{search}**",
                color=0xE74C3C
            )
            embed.set_footer(text="Essayez avec une autre recherche")
            return await ctx.send(embed=embed)
        
        # Créer l'embed avec les résultats
        embed = nextcord.Embed(
            title=f"🔍 Recherche : '{search}'",
            description=f"**{len(found_members)}** membre(s) trouvé(s)",
            color=0x3498db
        )
        
        # Limiter à 20 résultats pour éviter les embeds trop longs
        display_members = found_members[:20]
        
        for i, member in enumerate(display_members, 1):
            status_emoji = {
                "online": "🟢",
                "idle": "🟡", 
                "dnd": "🔴",
                "offline": "⚫"
            }.get(str(member.status), "⚪")
            
            # Vérifier si le membre est en vocal
            voice_status = ""
            if member.voice and member.voice.channel:
                voice_status = f" 🎤 {member.voice.channel.name}"
            
            member_info = f"{i}. {status_emoji} **{member.display_name}**{voice_status}\n"
            member_info += f"   └ ID: `{member.id}` | Rejoint: <t:{int(member.joined_at.timestamp())}:R>"
            
            embed.add_field(
                name=f"👤 {member.name}",
                value=member_info,
                inline=False
            )
        
        if len(found_members) > 20:
            embed.set_footer(text=f"Affichage des 20 premiers sur {len(found_members)} résultats")
        else:
            embed.set_footer(text=f"{len(found_members)} résultat(s) trouvé(s)")
        
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        await ctx.send(embed=embed)

    @commands.command(name="find")
    async def find_messages(self, ctx, *, search: str):
        """
        Chercher des messages dans le serveur
        
        Utilisation:
        +find "texte à chercher"
        +find mot
        +find nombre
        """
        
        if len(search) < 2:
            return await ctx.send("❌ La recherche doit contenir au moins 2 caractères.")
        
        # Message de recherche en cours
        searching_msg = await ctx.send(f"🔍 Recherche de messages contenant : **{search}**\n\n⏳ Analyse des channels...")
        
        found_messages = []
        search_lower = search.lower()
        channels_checked = 0
        
        # Limiter la recherche pour éviter les timeouts
        max_channels = 50
        max_messages_per_channel = 100
        
        for channel in ctx.guild.text_channels:
            if channels_checked >= max_channels:
                break
                
            # Vérifier les permissions
            if not channel.permissions_for(ctx.guild.me).read_message_history:
                continue
            
            try:
                channels_checked += 1
                
                # Mettre à jour le message de progression
                if channels_checked % 5 == 0:
                    await searching_msg.edit(
                        content=f"🔍 Recherche de messages contenant : **{search}**\n\n⏳ Analyse : {channels_checked} channels vérifiés..."
                    )
                
                # Chercher dans les messages récents
                async for message in channel.history(limit=max_messages_per_channel):
                    if search_lower in message.content.lower():
                        found_messages.append(message)
                
                # Petite pause pour éviter le rate limiting
                await asyncio.sleep(0.1)
                
            except nextcord.Forbidden:
                continue
            except Exception as e:
                print(f"Erreur recherche channel {channel.name}: {e}")
                continue
        
        # Supprimer le message de recherche
        await searching_msg.delete()
        
        if not found_messages:
            embed = nextcord.Embed(
                title="🔍 Recherche de messages",
                description=f"Aucun message trouvé pour : **{search}**\n\n📊 {channels_checked} channels analysés",
                color=0xE74C3C
            )
            embed.set_footer(text="Essayez avec une autre recherche")
            return await ctx.send(embed=embed)
        
        # Trier par date (du plus ancien au plus récent)
        found_messages.sort(key=lambda m: m.created_at)
        
        # Créer les pages de résultats
        messages_per_page = 10
        total_pages = (len(found_messages) + messages_per_page - 1) // messages_per_page
        
        class FindView(nextcord.ui.View):
            def __init__(self, messages, search_term, total_pages):
                super().__init__(timeout=300)  # 5 minutes
                self.messages = messages
                self.search_term = search_term
                self.total_pages = total_pages
                self.current_page = 1
                self.message = None
                
            def get_page_messages(self):
                start_idx = (self.current_page - 1) * messages_per_page
                end_idx = start_idx + messages_per_page
                return self.messages[start_idx:end_idx]
            
            def create_embed(self):
                page_messages = self.get_page_messages()
                
                embed = nextcord.Embed(
                    title=f"🔍 Recherche : '{self.search_term}'",
                    description=f"**{len(self.messages)}** message(s) trouvé(s) • Page {self.current_page}/{self.total_pages}",
                    color=0x3498db
                )
                
                for i, msg in enumerate(page_messages, 1):
                    # Limiter la longueur du message
                    content_preview = msg.content
                    if len(content_preview) > 100:
                        content_preview = content_preview[:97] + "..."
                    
                    # Mettre en évidence la recherche
                    content_preview = content_preview.replace(
                        self.search_term, 
                        f"**{self.search_term}**"
                    )
                    
                    field_value = f"📝 {content_preview}\n"
                    field_value += f"└ 👤 **{msg.author.display_name}** | 📍 #{msg.channel.name} | 🕐 <t:{int(msg.created_at.timestamp())}:R>"
                    
                    embed.add_field(
                        name=f"Message #{(self.current_page - 1) * messages_per_page + i}",
                        value=field_value,
                        inline=False
                    )
                
                embed.set_footer(text=f"Page {self.current_page}/{self.total_pages} • {len(self.messages)} résultats totaux")
                return embed
            
            @nextcord.ui.button(label="◀️", style=nextcord.ButtonStyle.secondary, custom_id="prev_page")
            async def previous_page(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                if self.current_page > 1:
                    self.current_page -= 1
                    button.disabled = (self.current_page == 1)
                    self.children[1].disabled = False  # Next button
                    await interaction.response.edit_message(embed=self.create_embed(), view=self)
                else:
                    await interaction.response.defer()
            
            @nextcord.ui.button(label="▶️", style=nextcord.ButtonStyle.secondary, custom_id="next_page")
            async def next_page(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                if self.current_page < self.total_pages:
                    self.current_page += 1
                    button.disabled = (self.current_page == self.total_pages)
                    self.children[0].disabled = False  # Previous button
                    await interaction.response.edit_message(embed=self.create_embed(), view=self)
                else:
                    await interaction.response.defer()
            
            @nextcord.ui.button(label="❌", style=nextcord.ButtonStyle.danger, custom_id="close")
            async def close_search(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                await interaction.response.edit_message(
                    content="🔍 Recherche terminée",
                    embed=None,
                    view=None
                )
                self.stop()
        
        # Créer et envoyer la vue
        view = FindView(found_messages, search, total_pages)
        
        # Désactiver le bouton précédent si on est à la première page
        if total_pages == 1:
            view.children[0].disabled = True
            view.children[1].disabled = True
        
        embed = view.create_embed()
        message = await ctx.send(embed=embed, view=view)
        view.message = message
        
        # Logger l'action
        try:
            from cogs.logs import log_command
            log_command(ctx, "find", f"Recherche: {search} | Résultats: {len(found_messages)}")
        except:
            pass

def setup(bot):
    bot.add_cog(Social(bot))
