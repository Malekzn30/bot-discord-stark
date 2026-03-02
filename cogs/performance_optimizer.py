import nextcord
from nextcord.ext import commands
import asyncio
import gc
import psutil
import time
import threading
from utils.config_manager import config_manager

class PerformanceOptimizer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()
        self.command_usage = {}
        self.performance_stats = {
            "commands_executed": 0,
            "errors_count": 0,
            "memory_usage": [],
            "cpu_usage": [],
            "response_times": []
        }
        
        # Démarrer le monitoring
        self.bot.loop.create_task(self.performance_monitor())
        self.bot.loop.create_task(self.auto_cleanup())
    
    # ============= MONITORING DE PERFORMANCE =============
    async def performance_monitor(self):
        """Monitorer les performances du bot"""
        while True:
            try:
                # Stats mémoire
                memory = psutil.virtual_memory()
                self.performance_stats["memory_usage"].append(memory.percent)
                
                # Stats CPU
                cpu = psutil.cpu_percent()
                self.performance_stats["cpu_usage"].append(cpu)
                
                # Garder seulement les 100 dernières mesures
                if len(self.performance_stats["memory_usage"]) > 100:
                    self.performance_stats["memory_usage"] = self.performance_stats["memory_usage"][-100:]
                if len(self.performance_stats["cpu_usage"]) > 100:
                    self.performance_stats["cpu_usage"] = self.performance_stats["cpu_usage"][-100:]
                
            except Exception as e:
                print(f"Erreur monitoring: {e}")
            
            await asyncio.sleep(60)  # Toutes les minutes
    
    async def auto_cleanup(self):
        """Nettoyage automatique pour optimiser les performances"""
        while True:
            try:
                # Forcer le garbage collection
                gc.collect()
                
                # Nettoyer les anciennes données
                await self.cleanup_old_data()
                
                print("✅ Auto-cleanup effectué")
                
            except Exception as e:
                print(f"Erreur auto-cleanup: {e}")
            
            await asyncio.sleep(300)  # Toutes les 5 minutes
    
    async def cleanup_old_data(self):
        """Nettoyer les anciennes données"""
        current_time = time.time()
        
        # Nettoyer les commandes usage anciennes
        to_remove = []
        for cmd, data in self.command_usage.items():
            if current_time - data["last_used"] > 3600:  # 1 heure
                to_remove.append(cmd)
        
        for cmd in to_remove:
            del self.command_usage[cmd]
        
        # Nettoyer les stats de performance anciennes
        if len(self.performance_stats["response_times"]) > 1000:
            self.performance_stats["response_times"] = self.performance_stats["response_times"][-500:]
    
    # ============= COMMANDES DE PERFORMANCE =============
    @commands.command(name="performance")
    @commands.has_permissions(administrator=True)
    async def performance_stats_cmd(self, ctx):
        """Afficher les statistiques de performance"""
        uptime = time.time() - self.start_time
        days = uptime // 86400
        hours = (uptime % 86400) // 3600
        minutes = (uptime % 3600) // 60
        
        memory = psutil.virtual_memory()
        cpu = psutil.cpu_percent()
        
        embed = nextcord.Embed(
            title="📊 Statistiques de Performance",
            color=0x3498db
        )
        
        embed.add_field(
            name="⏱️ Uptime",
            value=f"{int(days)}j {int(hours)}h {int(minutes)}m",
            inline=True
        )
        
        embed.add_field(
            name="💾 Mémoire",
            value=f"{memory.percent:.1f}%\n{memory.used // 1024 // 1024}MB / {memory.total // 1024 // 1024}MB",
            inline=True
        )
        
        embed.add_field(
            name="🖥️ CPU",
            value=f"{cpu:.1f}%",
            inline=True
        )
        
        embed.add_field(
            name="📈 Commandes",
            value=f"Exécutées: {self.performance_stats['commands_executed']}\nErreurs: {self.performance_stats['errors_count']}",
            inline=True
        )
        
        # Temps de réponse moyen
        if self.performance_stats["response_times"]:
            avg_response = sum(self.performance_stats["response_times"]) / len(self.performance_stats["response_times"])
            embed.add_field(
                name="⚡ Temps de réponse",
                value=f"{avg_response:.2f}ms",
                inline=True
            )
        
        # Top commandes
        if self.command_usage:
            top_commands = sorted(self.command_usage.items(), key=lambda x: x[1]["count"], reverse=True)[:5]
            top_text = "\n".join([f"• {cmd}: {data['count']} fois" for cmd, data in top_commands])
            embed.add_field(name="🔥 Top commandes", value=top_text, inline=False)
        
        embed.set_footer(text="Performance monitoring actif")
        await ctx.send(embed=embed)
    
    @commands.command(name="optimize")
    @commands.has_permissions(administrator=True)
    async def optimize_bot(self, ctx):
        """Optimiser manuellement le bot"""
        start_time = time.time()
        
        embed = nextcord.Embed(
            title="⚡ OPTIMISATION EN COURS",
            description="Optimisation du bot en cours...",
            color=0xF39C12
        )
        
        msg = await ctx.send(embed=embed)
        
        try:
            # 1. Nettoyage mémoire
            gc.collect()
            
            # 2. Nettoyage cache
            await self.cleanup_old_data()
            
            # 3. Optimisation des cogs
            for cog_name, cog in self.bot.cogs.items():
                if hasattr(cog, 'cleanup'):
                    try:
                        await cog.cleanup()
                    except:
                        pass
            
            # 4. Vérification de la mémoire
            memory_before = psutil.virtual_memory().percent
            await asyncio.sleep(2)
            memory_after = psutil.virtual_memory().percent
            
            duration = time.time() - start_time
            
            embed = nextcord.Embed(
                title="✅ OPTIMISATION TERMINÉE",
                description=f"Optimisation terminée en {duration:.2f}s",
                color=0x2ECC71
            )
            
            embed.add_field(
                name="📊 Résultats",
                value=f"**Mémoire avant:** {memory_before:.1f}%\n**Mémoire après:** {memory_after:.1f}%\n**Gain:** {memory_before - memory_after:.1f}%",
                inline=False
            )
            
            await msg.edit(embed=embed)
            
        except Exception as e:
            embed = nextcord.Embed(
                title="❌ ERREUR D'OPTIMISATION",
                description=f"Erreur: {e}",
                color=0xE74C3C
            )
            await msg.edit(embed=embed)
    
    @commands.command(name="cache")
    @commands.has_permissions(administrator=True)
    async def cache_info(self, ctx):
        """Informations sur le cache"""
        embed = nextcord.Embed(
            title="💾 Informations Cache",
            color=0x3498db
        )
        
        # Cache des commandes
        embed.add_field(
            name="🔧 Cache Commandes",
            value=f"Entrées: {len(self.command_usage)}",
            inline=True
        )
        
        # Cache de performance
        embed.add_field(
            name="📈 Cache Performance",
            value=f"Temps réponse: {len(self.performance_stats['response_times'])}\nMémoire: {len(self.performance_stats['memory_usage'])}",
            inline=True
        )
        
        # Cache du bot
        bot_cache_size = len(self.bot._connection._messages) if hasattr(self.bot, '_connection') else 0
        embed.add_field(
            name="🤖 Cache Bot",
            value=f"Messages: {bot_cache_size}",
            inline=True
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="clearcache")
    @commands.has_permissions(administrator=True)
    async def clear_cache(self, ctx, cache_type: str = "all"):
        """Vider le cache du bot"""
        cleared = []
        
        if cache_type.lower() in ("all", "commands"):
            self.command_usage.clear()
            cleared.append("Cache commandes")
        
        if cache_type.lower() in ("all", "performance"):
            self.performance_stats["response_times"].clear()
            self.performance_stats["memory_usage"].clear()
            self.performance_stats["cpu_usage"].clear()
            cleared.append("Cache performance")
        
        if cache_type.lower() in ("all", "bot"):
            # Vider le cache du bot Discord
            if hasattr(self.bot, '_connection'):
                self.bot._connection._messages.clear()
            cleared.append("Cache bot")
        
        if not cleared:
            return await ctx.send("❌ Type de cache invalide. Utilise: all, commands, performance, bot")
        
        embed = nextcord.Embed(
            title="✅ CACHE VIDÉ",
            description=f"Cache vidé: {', '.join(cleared)}",
            color=0x2ECC71
        )
        
        await ctx.send(embed=embed)
    
    # ============= LISTENERS POUR LES STATS =============
    @commands.Cog.listener()
    async def on_command(self, ctx):
        """Logger l'utilisation des commandes"""
        start_time = time.time()
        
        # Stats de la commande
        cmd_name = ctx.command.name
        if cmd_name not in self.command_usage:
            self.command_usage[cmd_name] = {"count": 0, "total_time": 0, "last_used": 0}
        
        self.command_usage[cmd_name]["count"] += 1
        self.command_usage[cmd_name]["last_used"] = time.time()
        self.performance_stats["commands_executed"] += 1
    
    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        """Calculer le temps de réponse"""
        # Cette méthode sera appelée après l'exécution de la commande
        pass
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Logger les erreurs"""
        self.performance_stats["errors_count"] += 1
        
        # Logger détaillé
        error_info = {
            "command": ctx.command.name if ctx.command else "Unknown",
            "error": str(error),
            "user": ctx.author.id,
            "timestamp": time.time()
        }
        
        print(f"Command Error: {error_info}")
    
    # = UTILITAIRES D'OPTIMISATION =============
    def get_memory_usage(self):
        """Obtenir l'utilisation mémoire"""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024  # MB
    
    def get_cpu_usage(self):
        """Obtenir l'utilisation CPU"""
        return psutil.cpu_percent()
    
    async def measure_command_time(self, func, *args, **kwargs):
        """Mesurer le temps d'exécution d'une fonction"""
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = (time.time() - start_time) * 1000  # ms
            
            self.performance_stats["response_times"].append(execution_time)
            
            # Garder seulement les 1000 dernières mesures
            if len(self.performance_stats["response_times"]) > 1000:
                self.performance_stats["response_times"] = self.performance_stats["response_times"][-500:]
            
            return result
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            self.performance_stats["response_times"].append(execution_time)
            raise e

def setup(bot):
    bot.add_cog(PerformanceOptimizer(bot))
