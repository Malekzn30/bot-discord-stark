import nextcord
from nextcord.ext import commands
import asyncio
import time
from config import AUTHORIZED_ROLE_ID
from utils.embeds import create_embed

def has_role():
    async def predicate(ctx):
        role = ctx.guild.get_role(AUTHORIZED_ROLE_ID)
        return role in ctx.author.roles
    return commands.check(predicate)

class DM(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="dmall")
    @has_role()
    async def dmall(self, ctx, message_type: str, *, content: str = None):
        """
        Envoyer un message à tous les membres du serveur
        
        Types disponibles:
        - texte: Message texte simple
        - embed: Message avec embed (titre et description)
        
        Utilisation:
        +dmall texte "Votre message ici"
        +dmall embed "Titre" "Description ici"
        """
        
        if message_type.lower() not in ["texte", "embed"]:
            return await ctx.send("❌ Type invalide. Utilise: `texte` ou `embed`")
        
        if message_type.lower() == "embed":
            # Pour les embeds, on attend titre et description
            if not content or '"' not in content:
                return await ctx.send("❌ Utilisation embed: `+dmall embed \"Titre\" \"Description\"`")
            
            # Parser le titre et la description entre guillemets
            parts = content.split('"')
            if len(parts) < 4:
                return await ctx.send("❌ Format invalide. Utilise: `+dmall embed \"Titre\" \"Description\"`")
            
            title = parts[1].strip()
            description = parts[3].strip() if len(parts) > 3 else ""
            
            if not title:
                return await ctx.send("❌ Le titre ne peut pas être vide")
        
        # Confirmation avant envoi
        total_members = len(ctx.guild.members)
        embed_confirm = nextcord.Embed(
            title="⚠️ Confirmation d'envoi massif",
            description=f"Vous allez envoyer un message à **{total_members}** membres.",
            color=0xFFAA00
        )
        
        if message_type.lower() == "texte":
            embed_confirm.add_field(name="📝 Type", value="Message texte", inline=True)
            embed_confirm.add_field(name="📄 Contenu", value=content[:200] + "..." if len(content) > 200 else content, inline=False)
        else:
            embed_confirm.add_field(name="📝 Type", value="Message embed", inline=True)
            embed_confirm.add_field(name="📋 Titre", value=title, inline=False)
            embed_confirm.add_field(name="📄 Description", value=description[:200] + "..." if len(description) > 200 else description, inline=False)
        
        embed_confirm.add_field(name="⏱️ Temps estimé", value=f"~{total_members * 0.5:.0f} secondes", inline=True)
        embed_confirm.set_footer(text="Répondez 'oui' pour confirmer ou 'non' pour annuler")
        
        await ctx.send(embed=embed_confirm)
        
        # Attendre la confirmation
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ["oui", "yes", "non", "no"]
        
        try:
            response = await self.bot.wait_for("message", timeout=30.0, check=check)
            
            if response.content.lower() in ["non", "no"]:
                return await ctx.send("❌ Envoi annulé.")
            
        except asyncio.TimeoutError:
            return await ctx.send("❌ Temps écoulé. Envoi annulé.")
        
        # Commencer l'envoi
        start_time = time.time()
        sent_count = 0
        failed_count = 0
        blocked_count = 0
        
        # Message de progression
        progress_msg = await ctx.send("🚀 Début de l'envoi massif...")
        
        for i, member in enumerate(ctx.guild.members):
            try:
                if message_type.lower() == "texte":
                    await member.send(content)
                else:
                    embed = create_embed(title, description, ctx.guild, None)
                    await member.send(embed=embed)
                
                sent_count += 1
                
                # Mettre à jour la progression tous les 10 membres
                if i % 10 == 0:
                    progress = (i / total_members) * 100
                    elapsed = time.time() - start_time
                    eta = (elapsed / i * (total_members - i)) if i > 0 else 0
                    
                    await progress_msg.edit(
                        content=f"📊 Progression: {progress:.1f}% ({i}/{total_members})\n"
                               f"✅ Envoyés: {sent_count} | ❌ Échecs: {failed_count} | 🔒 Bloqués: {blocked_count}\n"
                               f"⏱️ Temps restant: ~{eta:.0f}s"
                    )
                
                # Petit délai pour éviter le rate limiting
                await asyncio.sleep(0.5)
                
            except nextcord.Forbidden:
                blocked_count += 1
            except Exception as e:
                failed_count += 1
                print(f"❌ Erreur DM vers {member.display_name}: {e}")
        
        # Message final
        elapsed_time = time.time() - start_time
        
        embed_final = nextcord.Embed(
            title="✅ Envoi massif terminé",
            description=f"Message envoyé avec succès !",
            color=0x2ECC71
        )
        
        embed_final.add_field(name="📊 Statistiques", value=(
            f"**{sent_count}** messages envoyés ✅\n"
            f"**{failed_count}** échecs ❌\n"
            f"**{blocked_count}** membres avec DMs désactivés 🔒"
        ), inline=False)
        
        embed_final.add_field(name="⏱️ Performance", value=(
            f"**{elapsed_time:.1f}s** de durée totale\n"
            f"**{sent_count/elapsed_time:.1f}** messages/seconde"
        ), inline=False)
        
        embed_final.set_footer(text=f"Demandé par {ctx.author.name}")
        
        await progress_msg.edit(embed=embed_final)
        
        # Logger l'action
        try:
            from cogs.logs import log_command
            log_command(ctx, "dmall", f"Type: {message_type} | Envoyés: {sent_count} | Échecs: {failed_count}")
        except:
            pass

    @commands.command(name="dmtest")
    @has_role()
    async def dmtest(self, ctx, message_type: str, *, content: str = None):
        """Tester l'envoi de DM avant envoi massif"""
        
        if message_type.lower() not in ["texte", "embed"]:
            return await ctx.send("❌ Type invalide. Utilise: `texte` ou `embed`")
        
        if message_type.lower() == "embed":
            if not content or '"' not in content:
                return await ctx.send("❌ Utilisation embed: `+dmtest embed \"Titre\" \"Description\"`")
            
            parts = content.split('"')
            if len(parts) < 4:
                return await ctx.send("❌ Format invalide. Utilise: `+dmtest embed \"Titre\" \"Description\"`")
            
            title = parts[1].strip()
            description = parts[3].strip() if len(parts) > 3 else ""
            
            if not title:
                return await ctx.send("❌ Le titre ne peut pas être vide")
        
        try:
            if message_type.lower() == "texte":
                await ctx.author.send(f"🧪 **TEST DM**\n\n{content}")
                await ctx.send("✅ Message texte de test envoyé avec succès !")
            else:
                embed = create_embed(title, description, ctx.guild, None)
                await ctx.author.send("🧪 **TEST DM**", embed=embed)
                await ctx.send("✅ Embed de test envoyé avec succès !")
                
        except nextcord.Forbidden:
            await ctx.send("❌ Vous avez désactivé les DMs. Je ne peux pas vous envoyer de message de test.")
        except Exception as e:
            await ctx.send(f"❌ Erreur lors de l'envoi du test: {e}")

def setup(bot):
    bot.add_cog(DM(bot))
