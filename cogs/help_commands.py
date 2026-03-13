import nextcord
from nextcord.ext import commands
import config

class HelpCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx, category: str = None, page: int = 1):
        """Affiche l'aide du bot avec interface interactive"""
        # Vérifier si le salon est autorisé
        from bot import is_channel_allowed
        if not is_channel_allowed(ctx.channel):
            return
        
        if category:
            # Aide par catégorie avec pagination
            category_commands = []
            for cmd in self.bot.commands:
                if cmd.cog and cmd.cog.__class__.__name__.lower() == category.lower():
                    category_commands.append(cmd)
            
            if not category_commands:
                return await ctx.send(f"❌ Catégorie `{category}` non trouvée")
            
            await self.send_category_help(ctx, category, category_commands, page)
        else:
            # Menu principal interactif
            await self.send_main_help(ctx)

    async def send_main_help(self, ctx):
        """Envoie le menu principal d'aide avec sélecteur"""
        from collections import Counter
        
        # Regrouper par catégories
        categories = {}
        for cmd in self.bot.commands:
            cog_name = cmd.cog.__class__.__name__ if cmd.cog else "Inconnu"
            if cog_name not in categories:
                categories[cog_name] = []
            categories[cog_name].append(cmd)
        
        # Créer le menu déroulant avec plus de catégories
        options = []
        for cog_name, cmds in sorted(categories.items(), key=lambda x: len(x[1]), reverse=True):
            if cog_name != "Inconnu":  # Exclure les commandes système
                options.append(nextcord.SelectOption(
                    label=f"{cog_name} ({len(cmds)} commandes)",
                    description=f"Voir les {len(cmds)} commandes de {cog_name}",
                    value=cog_name.lower()
                ))
        
        select = nextcord.ui.Select(
            placeholder="🔍 Choisis une catégorie...",
            options=options[:25],  # Limite Discord
            custom_id="help_category_select"
        )
        
        async def select_callback(interaction: nextcord.Interaction):
            selected_category = interaction.data['values'][0]
            await interaction.response.defer()
            await self.send_category_help(interaction, selected_category, 
                                   [cmd for cmd in self.bot.commands 
                                    if cmd.cog and cmd.cog.__class__.__name__.lower() == selected_category], 1)
        
        select.callback = select_callback
        
        view = nextcord.ui.View(timeout=180)
        view.add_item(select)
        
        embed = nextcord.Embed(
            title="🤖 StarK92 Bot - Aide Interactive",
            description=f"**{len(self.bot.commands)} commandes disponibles**\n\n👇 **Sélectionne une catégorie ci-dessous**",
            color=0x3498db
        )
        
        embed.add_field(
            name="📊 Statistiques",
            value=f"• **{len(categories)} catégories**\n• **{len(self.bot.commands)} commandes totales**\n• **Système optimisé**",
            inline=False
        )
        
        embed.add_field(
            name="🎯 Commandes Populaires",
            value="`+devinelenombre` • `+helpmenu` • `+voice`\n`+cogstatus` • `+ping` • `+dice`",
            inline=False
        )
        
        embed.add_field(
            name="⚙️ Gestion",
            value="`+setactivity` • `+setstatus` • `+autoreact`\n`+ignoredchannels` • `+testchannel`",
            inline=False
        )
        
        embed.set_footer(text="Sélectionne une catégorie dans le menu déroulant")
        
        await ctx.send(embed=embed, view=view)

    async def send_category_help(self, ctx, category_name, commands_list, page=1):
        """Envoie l'aide d'une catégorie avec boutons de navigation"""
        # Trier les commandes
        sorted_commands = sorted(commands_list, key=lambda x: x.name)
        
        # Calculer la pagination
        commands_per_page = 25
        total_pages = (len(sorted_commands) + commands_per_page - 1) // commands_per_page
        
        if page < 1 or page > total_pages:
            page = 1
        
        # Obtenir les commandes pour cette page
        start_idx = (page - 1) * commands_per_page
        end_idx = start_idx + commands_per_page
        page_commands = sorted_commands[start_idx:end_idx]
        
        embed = nextcord.Embed(
            title=f"📖 Aide: {category_name.title()}",
            description=f"**{len(commands_list)} commandes** - Page {page}/{total_pages}",
            color=0x3498db
        )
        
        for cmd in page_commands:
            help_text = cmd.help or "Aucune description"
            embed.add_field(name=f"+{cmd.name}", value=help_text[:100], inline=False)
        
        embed.set_footer(text=f"Page {page}/{total_pages} • Utilise les boutons pour naviguer")
        
        # Créer les boutons de navigation
        view = nextcord.ui.View(timeout=180)
        
        # Bouton Retour
        back_button = nextcord.ui.Button(
            label="🔙 Retour",
            style=nextcord.ButtonStyle.secondary,
            custom_id="help_back"
        )
        
        async def back_callback(interaction: nextcord.Interaction):
            await interaction.response.defer()
            await self.send_main_help(interaction)
        
        back_button.callback = back_callback
        view.add_item(back_button)
        
        # Boutons de navigation de page
        if page > 1:
            prev_button = nextcord.ui.Button(
                label="⬅️ Précédent",
                style=nextcord.ButtonStyle.primary,
                custom_id="help_prev"
            )
            
            async def prev_callback(interaction: nextcord.Interaction):
                await interaction.response.defer()
                await self.send_category_help(interaction, category_name, commands_list, page - 1)
            
            prev_button.callback = prev_callback
            view.add_item(prev_button)
        
        # Bouton page actuelle
        page_button = nextcord.ui.Button(
            label=f"📄 {page}/{total_pages}",
            style=nextcord.ButtonStyle.secondary,
            disabled=True
        )
        view.add_item(page_button)
        
        if page < total_pages:
            next_button = nextcord.ui.Button(
                label="➡️ Suivant",
                style=nextcord.ButtonStyle.primary,
                custom_id="help_next"
            )
            
            async def next_callback(interaction: nextcord.Interaction):
                await interaction.response.defer()
                await self.send_category_help(interaction, category_name, commands_list, page + 1)
            
            next_button.callback = next_callback
            view.add_item(next_button)
        
        # Envoyer ou modifier le message
        if hasattr(ctx, 'edit'):  # Si c'est une interaction (modification)
            await ctx.edit(embed=embed, view=view)
        else:  # Si c'est un Context normal (nouveau message)
            await ctx.send(embed=embed, view=view)

def setup(bot):
    bot.add_cog(HelpCommands(bot))
