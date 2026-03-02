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

class System(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help(self, ctx, command: str = None):
        """
        +help            → liste générale des commandes avec descriptions
        +help <commande> → détails sur la commande spécifique
        """
        if command is None:
            # Afficher la liste des commandes avec descriptions
            await self.show_command_list(ctx)
            return

        # --- aide spécifique ------------------------------------------------
        helps = {
            "warn": {
                "description": "Avertir un membre (ajoute automatiquement le rôle de warn).",
                "usage": "+warn <@membre> [raison]",
                "exemple": "+warn @User Spam excessif",
                "permissions": "Modérateur ou plus"
            },
            "kick": {
                "description": "Expulser un membre du serveur.",
                "usage": "+kick <@membre> [raison]",
                "exemple": "+kick @User Comportement toxique",
                "permissions": "Modérateur ou plus"
            },
            "ban": {
                "description": "Bannir un membre du serveur.",
                "usage": "+ban <@membre> [raison]",
                "exemple": "+ban @User Harcèlement",
                "permissions": "Administrateur"
            },
            "tempban": {
                "description": "Bannir temporairement un membre.",
                "usage": "+tempban <@membre> <minutes> [raison]",
                "exemple": "+tempban @User 60 Spam",
                "permissions": "Administrateur"
            },
            "mute": {
                "description": "Ajouter le rôle muet à un membre.",
                "usage": "+mute <@membre> [raison]",
                "exemple": "+mute @User Langage inapproprié",
                "permissions": "Modérateur ou plus"
            },
            "timeout": {
                "description": "Placer un membre en timeout (impossible de parler).",
                "usage": "+timeout <@membre> <minutes>",
                "exemple": "+timeout @User 10",
                "permissions": "Modérateur ou plus"
            },
            "clear": {
                "description": "Supprimer un nombre de messages.",
                "usage": "+clear <nombre>",
                "exemple": "+clear 50",
                "permissions": "Gérer les messages"
            },
            "logs_setup": {
                "description": "Configurer les logs du serveur avec menu interactif.",
                "usage": "+logs_setup",
                "exemple": "+logs_setup",
                "permissions": "Administrateur"
            },
            "logs_status": {
                "description": "Voir l'état de toutes les catégories de logs.",
                "usage": "+logs_status",
                "exemple": "+logs_status",
                "permissions": "Administrateur"
            },
            "déplacer": {
                "description": "Déplacer un membre dans un salon vocal.",
                "usage": "+déplacer <@membre> <#salon>",
                "exemple": "+déplacer @User #général",
                "permissions": "Déplacer les membres"
            },
            "equilibrer": {
                "description": "Équilibrer les membres dans les salons d'une catégorie (2-5 par salon).",
                "usage": "+equilibrer <@catégorie> [2-5]",
                "exemple": "+equilibrer @Général 3",
                "permissions": "Rôle autorisé"
            },
            "equilibrer_auto": {
                "description": "Équilibrage automatique intelligent selon le nombre de membres.",
                "usage": "+equilibrer_auto <@catégorie>",
                "exemple": "+equilibrer_auto @Général",
                "permissions": "Rôle autorisé"
            },
            "stats_vocal": {
                "description": "Afficher les statistiques vocales d'une catégorie.",
                "usage": "+stats_vocal <@catégorie>",
                "exemple": "+stats_vocal @Général",
                "permissions": "Rôle autorisé"
            },
            "optimiser_vocal": {
                "description": "Optimiser automatiquement la distribution vocale.",
                "usage": "+optimiser_vocal <@catégorie>",
                "exemple": "+optimiser_vocal @Général",
                "permissions": "Rôle autorisé"
            },
            "dmall": {
                "description": "Envoyer un message à tous les membres du serveur.",
                "usage": "+dmall <texte|embed> <contenu>",
                "exemple": "+dmall texte \"Message important pour tous\"",
                "permissions": "Rôle autorisé"
            },
            "dmtest": {
                "description": "Tester l'envoi de DM avant envoi massif.",
                "usage": "+dmtest <texte|embed> <contenu>",
                "exemple": "+dmtest embed \"Titre\" \"Description du test\"",
                "permissions": "Rôle autorisé"
            },
            "ping": {
                "description": "Mesurer la latence du bot.",
                "usage": "+ping",
                "exemple": "+ping",
                "permissions": "Tout le monde"
            },
            "embed": {
                "description": "Créer un embed personnalisé.",
                "usage": "+embed <titre> <description>",
                "exemple": "+embed \"Titre\" \"Description ici\"",
                "permissions": "Gérer les messages"
            },
            "lock": {
                "description": "Verrouiller le salon actuel (empêche d'écrire).",
                "usage": "+lock",
                "exemple": "+lock",
                "permissions": "Gérer les salons"
            },
            "unlock": {
                "description": "Déverrouiller le salon actuel.",
                "usage": "+unlock",
                "exemple": "+unlock",
                "permissions": "Gérer les salons"
            },
            "devinelenombre": {
                "description": "Lancer un jeu de devinette de nombre dans un salon.",
                "usage": "+devinelenombre <#salon> <min> <max>",
                "exemple": "+devinelenombre #jeux 1 100",
                "permissions": "Tout le monde"
            },
            "dice": {
                "description": "Lancer un dé avec un nombre de faces.",
                "usage": "+dice [faces]",
                "exemple": "+dice 6",
                "permissions": "Tout le monde"
            },
            "coin": {
                "description": "Faire un pile ou face.",
                "usage": "+coin",
                "exemple": "+coin",
                "permissions": "Tout le monde"
            },
            "rps": {
                "description": "Jouer à pierre feuille ciseaux.",
                "usage": "+rps <rock|paper|scissors>",
                "exemple": "+rps rock",
                "permissions": "Tout le monde"
            }
        }
        
        command = command.lower()
        if command not in helps:
            # Chercher des commandes similaires
            similar = [cmd for cmd in helps.keys() if command in cmd or cmd.startswith(command)]
            if similar:
                embed = nextcord.Embed(
                    title="❌ Commande introuvable",
                    description=f"Commande `+{command}` non trouvée.\n\n**Commandes similaires :**\n" + "\n".join(f"• `+{cmd}`" for cmd in similar[:5]),
                    color=0xE74C3C
                )
            else:
                embed = nextcord.Embed(
                    title="❌ Commande introuvable",
                    description=f"Commande `+{command}` non trouvée.\nUtilise `+help` pour voir toutes les commandes.",
                    color=0xE74C3C
                )
            embed.set_footer(text="Utilise +help pour voir la liste complète")
            await ctx.send(embed=embed)
            return

        help_info = helps[command]
        
        embed = nextcord.Embed(
            title=f"📖 Aide : +{command}",
            description=help_info["description"],
            color=0x3498db
        )
        
        embed.add_field(name="🔧 Utilisation", value=f"```{help_info['usage']}``", inline=False)
        embed.add_field(name="📝 Exemple", value=f"```{help_info['exemple']}``", inline=False)
        embed.add_field(name="🔒 Permissions requises", value=help_info["permissions"], inline=False)
        
        embed.set_footer(text=f"Utilise +help pour voir toutes les commandes")
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        
        await ctx.send(embed=embed)

    async def show_command_list(self, ctx):
        """Afficher la liste des commandes avec descriptions"""
        
        # Organiser les commandes par catégorie
        categories = {
            "🛡️ Modération": ["warn", "kick", "ban", "tempban", "mute", "timeout", "clear", "lock", "unlock"],
            "📊 Logs & Administration": ["logs_setup", "logs_status", "embed", "ping"],
            "🎤 Vocal & Équilibrage": ["déplacer", "equilibrer", "equilibrer_auto", "stats_vocal", "optimiser_vocal"],
            "📬 Messages & Communication": ["dmall", "dmtest"],
            "🎮 Jeux & Divertissement": ["devinelenombre", "dice", "coin", "rps"]
        }
        
        embed = nextcord.Embed(
            title="🤖 Commandes du Bot Stark",
            description="Voici toutes les commandes disponibles avec leurs descriptions.\nUtilise `+help <commande>` pour plus de détails.",
            color=0x3498db
        )
        
        for category_name, commands_list in categories.items():
            commands_text = ""
            for cmd in commands_list:
                # Récupérer la description courte
                descriptions = {
                    "warn": "Avertir un membre",
                    "kick": "Expulser un membre", 
                    "ban": "Bannir un membre",
                    "tempban": "Bannir temporairement",
                    "mute": "Rendre muet un membre",
                    "timeout": "Mettre en timeout",
                    "clear": "Supprimer des messages",
                    "lock": "Verrouiller un salon",
                    "unlock": "Déverrouiller un salon",
                    "logs_setup": "Configurer les logs",
                    "logs_status": "Voir les logs",
                    "embed": "Créer un embed",
                    "ping": "Vérifier la latence",
                    "déplacer": "Déplacer en vocal",
                    "equilibrer": "Équilibrer les salons vocaux",
                    "equilibrer_auto": "Équilibrage automatique",
                    "stats_vocal": "Statistiques vocales",
                    "optimiser_vocal": "Optimiser les salons vocaux",
                    "dmall": "Envoyer un DM massif",
                    "dmtest": "Tester un DM",
                    "devinelenombre": "Jeu de devinette",
                    "dice": "Lancer un dé",
                    "coin": "Pile ou face",
                    "rps": "Pierre feuille ciseaux"
                }
                
                desc = descriptions.get(cmd, "Description non disponible")
                commands_text += f"• `+{cmd}` - {desc}\n"
            
            if commands_text:
                embed.add_field(name=category_name, value=commands_text, inline=False)
        
        embed.add_field(
            name="🎯 Comment utiliser",
            value="`+help` - Voir cette liste\n`+help <commande>` - Aide détaillée sur une commande\n\nExemple : `+help warn`",
            inline=False
        )
        
        embed.set_footer(text=f"Demandé par {ctx.author.name} | Made by 𝐒𝐭𝐚𝐫𝐊𝟗𝟐☆🇵🇸")
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        
        await ctx.send(embed=embed)

    @commands.command(name="ping")
    async def ping(self, ctx):
        """Mesurer la latence du bot"""
        start_time = datetime.datetime.now()
        message = await ctx.send("🏓 Pong !")
        end_time = datetime.datetime.now()
        
        latency = (end_time - start_time).total_seconds() * 1000
        api_latency = round(self.bot.latency * 1000, 2)
        
        embed = nextcord.Embed(
            title="🏓 Pong !",
            description=f"Latence du bot : **{latency:.2f}ms**\nLatence API : **{api_latency}ms**",
            color=0x3498db
        )
        
        await message.edit(embed=embed)

    @commands.command(name="embed")
    @has_role()
    async def create_embed(self, ctx, title: str, *, description: str = None):
        """Créer un embed personnalisé"""
        if not description:
            return await ctx.send("❌ Veuillez fournir une description.")
        
        embed = nextcord.Embed(
            title=title,
            description=description,
            color=0x3498db
        )
        
        embed.set_footer(text=f"Créé par {ctx.author.name}")
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(System(bot))
