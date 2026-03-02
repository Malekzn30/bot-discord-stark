import nextcord
from nextcord.ext import commands
import asyncio
import datetime
import json
import os
from utils.config_manager import config_manager

class ModerationEnhanced(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warn_data = {}
        self.mute_data = {}
        self.ban_data = {}
        self.mod_logs = []
        
    # ============= SYSTÈME DE WARN AVANCÉ =============
    @commands.command(name="warn")
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx, member: nextcord.Member, *, reason: str):
        """Avertir un membre avec système de points"""
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            return await ctx.send("❌ Tu ne peux pas warn ce membre.")
        
        guild_id = ctx.guild.id
        if guild_id not in self.warn_data:
            self.warn_data[guild_id] = {}
        
        if member.id not in self.warn_data[guild_id]:
            self.warn_data[guild_id][member.id] = []
        
        # Ajouter le warn
        warn_info = {
            "reason": reason,
            "moderator": ctx.author.id,
            "timestamp": datetime.datetime.now().isoformat(),
            "points": 1
        }
        
        self.warn_data[guild_id][member.id].append(warn_info)
        total_warns = len(self.warn_data[guild_id][member.id])
        
        # Sauvegarder
        self.save_warn_data(guild_id)
        
        # Envoyer le message
        embed = nextcord.Embed(
            title="⚠️ AVERTISSEMENT",
            description=f"{member.mention} a reçu un avertissement !",
            color=0xF39C12
        )
        
        embed.add_field(name="Raison", value=reason, inline=False)
        embed.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
        embed.add_field(name="Total warns", value=str(total_warns), inline=True)
        embed.set_thumbnail(url=member.display_avatar.url)
        
        await ctx.send(embed=embed)
        
        # Message privé au membre
        try:
            dm_embed = nextcord.Embed(
                title="⚠️ Tu as reçu un avertissement",
                description=f"Tu as reçu un avertissement dans **{ctx.guild.name}**",
                color=0xF39C12
            )
            
            dm_embed.add_field(name="Raison", value=reason, inline=False)
            dm_embed.add_field(name="Modérateur", value=ctx.author.display_name, inline=True)
            dm_embed.add_field(name="Total warns", value=str(total_warns), inline=True)
            
            await member.send(embed=dm_embed)
        except:
            pass
        
        # Sanction automatique
        await self.check_auto_sanction(ctx, member, total_warns)
    
    @commands.command(name="warns")
    async def warns_list(self, ctx, member: nextcord.Member = None):
        """Voir les warns d'un membre"""
        target = member or ctx.author
        guild_id = ctx.guild.id
        
        if guild_id not in self.warn_data or target.id not in self.warn_data[guild_id]:
            return await ctx.send(f"✅ {target.mention} n'a aucun avertissement.")
        
        warns = self.warn_data[guild_id][target.id]
        
        embed = nextcord.Embed(
            title=f"⚠️ Avertissements de {target.name}",
            color=0xF39C12
        )
        
        for i, warn in enumerate(warns[-10:], 1):  # Derniers 10 warns
            moderator = self.bot.get_user(warn["moderator"])
            timestamp = datetime.datetime.fromisoformat(warn["timestamp"])
            
            embed.add_field(
                name=f"Warn #{i}",
                value=f"**Raison:** {warn['reason']}\n"
                       f"**Modérateur:** {moderator.name if moderator else 'Inconnu'}\n"
                       f"**Date:** {timestamp.strftime('%d/%m/%Y %H:%M')}",
                inline=False
            )
        
        embed.set_footer(text=f"Total: {len(warns)} warns")
        await ctx.send(embed=embed)
    
    @commands.command(name="clearwarns")
    @commands.has_permissions(administrator=True)
    async def clear_warns(self, ctx, member: nextcord.Member):
        """Supprimer tous les warns d'un membre"""
        guild_id = ctx.guild.id
        
        if guild_id in self.warn_data and member.id in self.warn_data[guild_id]:
            del self.warn_data[guild_id][member.id]
            self.save_warn_data(guild_id)
            await ctx.send(f"✅ Tous les warns de {member.mention} ont été supprimés.")
        else:
            await ctx.send(f"❌ {member.mention} n'a aucun warn.")
    
    async def check_auto_sanction(self, ctx, member, warn_count):
        """Vérifier les sanctions automatiques"""
        sanctions = config_manager.get("moderation.auto_sanctions", {
            3: {"type": "mute", "duration": 3600},  # 1h
            5: {"type": "kick", "duration": None},
            10: {"type": "tempban", "duration": 86400}  # 24h
        })
        
        for threshold, sanction in sanctions.items():
            if warn_count >= threshold:
                if sanction["type"] == "mute":
                    await self.mute_user(ctx, member, sanction["duration"], f"Auto-sanction: {warn_count} warns")
                elif sanction["type"] == "kick":
                    await member.kick(reason=f"Auto-sanction: {warn_count} warns")
                elif sanction["type"] == "tempban":
                    await self.tempban_user(ctx, member, sanction["duration"], f"Auto-sanction: {warn_count} warns")
                break
    
    # ============= SYSTÈME DE MUTE AVANCÉ =============
    @commands.command(name="mute")
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: nextcord.Member, duration: str = None, *, reason: str = "Non spécifiée"):
        """Rendre muet un membre"""
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            return await ctx.send("❌ Tu ne peux pas mute ce membre.")
        
        # Calculer la durée
        seconds = self.parse_duration(duration) if duration else 3600  # 1h par défaut
        
        # Créer ou récupérer le rôle mute
        mute_role = await self.get_mute_role(ctx.guild)
        
        await member.add_roles(mute_role, reason=reason)
        
        # Sauvegarder les données de mute
        guild_id = ctx.guild.id
        if guild_id not in self.mute_data:
            self.mute_data[guild_id] = {}
        
        self.mute_data[guild_id][member.id] = {
            "end_time": datetime.datetime.now() + datetime.timedelta(seconds=seconds),
            "reason": reason,
            "moderator": ctx.author.id
        }
        
        embed = nextcord.Embed(
            title="🔇 MEMBRE RENDU MUET",
            description=f"{member.mention} a été rendu muet",
            color=0xE74C3C
        )
        
        embed.add_field(name="Durée", value=self.format_duration(seconds), inline=True)
        embed.add_field(name="Raison", value=reason, inline=True)
        embed.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
        
        await ctx.send(embed=embed)
        
        # Démarrer le timer de unmute automatique
        self.bot.loop.create_task(self.auto_unmute(ctx.guild.id, member.id, seconds))
    
    @commands.command(name="unmute")
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: nextcord.Member):
        """Rendre la parole à un membre"""
        mute_role = nextcord.utils.get(ctx.guild.roles, name="Muted")
        
        if not mute_role or mute_role not in member.roles:
            return await ctx.send(f"❌ {member.mention} n'est pas muet.")
        
        await member.remove_roles(mute_role)
        
        # Supprimer des données de mute
        guild_id = ctx.guild.id
        if guild_id in self.mute_data and member.id in self.mute_data[guild_id]:
            del self.mute_data[guild_id][member.id]
        
        embed = nextcord.Embed(
            title="🔊 MEMBRE DÉMUTÉ",
            description=f"{member.mention} peut de nouveau parler",
            color=0x2ECC71
        )
        
        embed.add_field(name="Modérateur", value=ctx.author.mention)
        await ctx.send(embed=embed)
    
    async def get_mute_role(self, guild):
        """Créer ou récupérer le rôle mute"""
        mute_role = nextcord.utils.get(guild.roles, name="Muted")
        
        if not mute_role:
            # Créer le rôle avec les permissions appropriées
            overwrites = {
                guild.default_role: nextcord.PermissionOverwrite(
                    send_messages=False,
                    add_reactions=False,
                    speak=False
                )
            }
            
            mute_role = await guild.create_role(
                name="Muted",
                color=nextcord.Color.red(),
                reason="Rôle pour les membres muets"
            )
            
            # Appliquer les permissions à tous les salons
            for channel in guild.text_channels:
                await channel.set_permissions(mute_role, **overwrites)
        
        return mute_role
    
    async def auto_unmute(self, guild_id, member_id, delay):
        """Unmute automatique après la durée"""
        await asyncio.sleep(delay)
        
        guild = self.bot.get_guild(guild_id)
        member = guild.get_member(member_id)
        
        if not member:
            return
        
        mute_role = nextcord.utils.get(guild.roles, name="Muted")
        if mute_role and mute_role in member.roles:
            await member.remove_roles(mute_role)
            
            # Supprimer des données
            if guild_id in self.mute_data and member_id in self.mute_data[guild_id]:
                del self.mute_data[guild_id][member_id]
    
    # ============= SYSTÈME DE BAN AVANCÉ =============
    @commands.command(name="tempban")
    @commands.has_permissions(ban_members=True)
    async def tempban(self, ctx, member: nextcord.Member, duration: str, *, reason: str = "Non spécifiée"):
        """Bannir temporairement un membre"""
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            return await ctx.send("❌ Tu ne peux pas bannir ce membre.")
        
        seconds = self.parse_duration(duration)
        
        await member.ban(reason=reason)
        
        # Sauvegarder les données de ban
        guild_id = ctx.guild.id
        if guild_id not in self.ban_data:
            self.ban_data[guild_id] = {}
        
        self.ban_data[guild_id][member.id] = {
            "end_time": datetime.datetime.now() + datetime.timedelta(seconds=seconds),
            "reason": reason,
            "moderator": ctx.author.id
        }
        
        embed = nextcord.Embed(
            title="🔨 MEMBRE BANNI TEMPORAIREMENT",
            description=f"{member.mention} a été banni",
            color=0xE74C3C
        )
        
        embed.add_field(name="Durée", value=self.format_duration(seconds), inline=True)
        embed.add_field(name="Raison", value=reason, inline=True)
        embed.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
        
        await ctx.send(embed=embed)
        
        # Démarrer le timer de unban automatique
        self.bot.loop.create_task(self.auto_unban(ctx.guild.id, member.id, seconds))
    
    async def auto_unban(self, guild_id, user_id, delay):
        """Unban automatique après la durée"""
        await asyncio.sleep(delay)
        
        guild = self.bot.get_guild(guild_id)
        user = self.bot.get_user(user_id)
        
        if guild and user:
            try:
                await guild.unban(user)
                
                # Supprimer des données
                if guild_id in self.ban_data and user_id in self.ban_data[guild_id]:
                    del self.ban_data[guild_id][user_id]
            except:
                pass
    
    # ============= SYSTÈME DE LOGS =============
    @commands.command(name="modlogs")
    async def mod_logs(self, ctx, limit: int = 10):
        """Afficher les logs de modération"""
        guild_id = ctx.guild.id
        
        # Récupérer les logs depuis le fichier
        logs = self.load_mod_logs(guild_id)
        
        if not logs:
            return await ctx.send("❌ Aucun log de modération trouvé.")
        
        embed = nextcord.Embed(
            title="📋 LOGS DE MODÉRATION",
            description=f"Derniers {min(limit, len(logs))} logs",
            color=0x3498db
        )
        
        for log in logs[-limit:]:
            moderator = self.bot.get_user(log["moderator_id"])
            target = self.bot.get_user(log["target_id"])
            timestamp = datetime.datetime.fromisoformat(log["timestamp"])
            
            embed.add_field(
                name=f"{log['action'].upper()} - {timestamp.strftime('%d/%m/%Y %H:%M')}",
                value=f"**Modérateur:** {moderator.name if moderator else 'Inconnu'}\n"
                       f"**Cible:** {target.name if target else 'Inconnu'}\n"
                       f"**Raison:** {log['reason']}",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    def log_action(self, guild_id, action, moderator_id, target_id, reason):
        """Logger une action de modération"""
        log_entry = {
            "action": action,
            "moderator_id": moderator_id,
            "target_id": target_id,
            "reason": reason,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        if guild_id not in self.mod_logs:
            self.mod_logs[guild_id] = []
        
        self.mod_logs[guild_id].append(log_entry)
        
        # Garder seulement les 1000 derniers logs
        if len(self.mod_logs[guild_id]) > 1000:
            self.mod_logs[guild_id] = self.mod_logs[guild_id][-1000:]
        
        self.save_mod_logs(guild_id)
    
    # ============= UTILITAIRES =============
    def parse_duration(self, duration_str):
        """Parser une durée (1h, 30m, 1d)"""
        if not duration_str:
            return 3600  # 1h par défaut
        
        duration_str = duration_str.lower()
        
        if duration_str.endswith('h'):
            return int(duration_str[:-1]) * 3600
        elif duration_str.endswith('m'):
            return int(duration_str[:-1]) * 60
        elif duration_str.endswith('d'):
            return int(duration_str[:-1]) * 86400
        elif duration_str.endswith('w'):
            return int(duration_str[:-1]) * 604800
        else:
            return int(duration_str)  # Secondes
    
    def format_duration(self, seconds):
        """Formatter une durée en texte lisible"""
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        
        parts = []
        if days > 0:
            parts.append(f"{days}j")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        
        return " ".join(parts) if parts else "0m"
    
    def save_warn_data(self, guild_id):
        """Sauvegarder les données de warns"""
        os.makedirs("data/warns", exist_ok=True)
        with open(f"data/warns/{guild_id}.json", "w") as f:
            json.dump(self.warn_data.get(guild_id, {}), f, indent=2)
    
    def load_warn_data(self, guild_id):
        """Charger les données de warns"""
        try:
            with open(f"data/warns/{guild_id}.json", "r") as f:
                return json.load(f)
        except:
            return {}
    
    def save_mod_logs(self, guild_id):
        """Sauvegarder les logs de modération"""
        os.makedirs("data/modlogs", exist_ok=True)
        with open(f"data/modlogs/{guild_id}.json", "w") as f:
            json.dump(self.mod_logs.get(guild_id, []), f, indent=2)
    
    def load_mod_logs(self, guild_id):
        """Charger les logs de modération"""
        try:
            with open(f"data/modlogs/{guild_id}.json", "r") as f:
                return json.load(f)
        except:
            return []
    
    # ============= LISTENERS =============
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        """Logger les bans"""
        if guild.id in self.ban_data and user.id in self.ban_data[guild.id]:
            ban_info = self.ban_data[guild.id][user.id]
            self.log_action(guild.id, "ban", ban_info["moderator"], user.id, ban_info["reason"])
    
    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        """Logger les unbans"""
        self.log_action(guild.id, "unban", self.bot.user.id, user.id, "Unban automatique")

def setup(bot):
    bot.add_cog(ModerationEnhanced(bot))
