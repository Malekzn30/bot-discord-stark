"""
Module d'optimisation pour Render gratuit
Optimisations pour tenir 1 mois avec les limitations gratuites
"""

import gc
import asyncio
import psutil
import os
from datetime import datetime, timedelta
import functools

class RenderOptimizer:
    """Optimisations spécifiques pour Render gratuit"""
    
    def __init__(self, bot):
        self.bot = bot
        self.last_cleanup = datetime.now()
        self.cleanup_interval = timedelta(minutes=30)  # Nettoyage toutes les 30 minutes
        self.memory_limit_mb = 512  # Limite mémoire pour Render gratuit
        self.cpu_limit_percent = 80  # Limite CPU pour éviter les timeouts
        
        # Cache limité pour économiser la mémoire
        self.message_cache = {}
        self.user_cache = {}
        self.max_cache_size = 100
        
        # Démarrer les tâches d'optimisation
        self.bot.loop.create_task(self.optimization_loop())
    
    async def optimization_loop(self):
        """Boucle d'optimisation automatique"""
        while True:
            try:
                await self.perform_optimizations()
                await asyncio.sleep(300)  # Toutes les 5 minutes
            except Exception as e:
                print(f"[OPTIMIZATION] Erreur: {e}")
                await asyncio.sleep(60)
    
    async def perform_optimizations(self):
        """Effectuer toutes les optimisations"""
        now = datetime.now()
        
        # Nettoyage mémoire si nécessaire
        if now - self.last_cleanup > self.cleanup_interval:
            await self.cleanup_memory()
            self.last_cleanup = now
        
        # Vérifier l'utilisation mémoire
        await self.check_memory_usage()
        
        # Nettoyer les caches
        await self.cleanup_caches()
        
        # Optimiser les tâches en cours
        await self.optimize_tasks()
    
    async def cleanup_memory(self):
        """Nettoyage de la mémoire"""
        try:
            # Forcer le garbage collection
            collected = gc.collect()
            
            # Nettoyer les références circulaires
            gc.set_debug(gc.DEBUG_SAVEALL)
            unreachable = len(gc.garbage)
            gc.garbage.clear()
            
            print(f"[MEMORY] Nettoyage: {collected} objets collectés, {unreachable} références circulaires")
            
        except Exception as e:
            print(f"[MEMORY] Erreur nettoyage: {e}")
    
    async def check_memory_usage(self):
        """Vérifier et gérer l'utilisation mémoire"""
        try:
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            print(f"[MEMORY] Utilisation: {memory_mb:.1f} MB / {self.memory_limit_mb} MB")
            
            if memory_mb > self.memory_limit_mb * 0.8:  # 80% de la limite
                await self.emergency_cleanup()
                print(f"[MEMORY] ⚠️ Utilisation mémoire élevée: {memory_mb:.1f} MB")
            
        except Exception as e:
            print(f"[MEMORY] Erreur vérification: {e}")
    
    async def emergency_cleanup(self):
        """Nettoyage d'urgence"""
        try:
            # Vider les caches
            self.message_cache.clear()
            self.user_cache.clear()
            
            # Forcer garbage collection multiple fois
            for _ in range(3):
                gc.collect()
            
            # Fermer les connexions inactives
            if hasattr(self.bot, 'http'):
                self.bot.http.close()
            
            print("[MEMORY] 🚨 Nettoyage d'urgence effectué")
            
        except Exception as e:
            print(f"[MEMORY] Erreur nettoyage d'urgence: {e}")
    
    async def cleanup_caches(self):
        """Nettoyer les caches expirés"""
        try:
            # Limiter la taille du cache de messages
            if len(self.message_cache) > self.max_cache_size:
                # Garder seulement les plus récents
                items = list(self.message_cache.items())
                items.sort(key=lambda x: x[1].get('timestamp', 0), reverse=True)
                
                self.message_cache = dict(items[:self.max_cache_size//2])
                print(f"[CACHE] Cache messages nettoyé: {len(self.message_cache)} éléments")
            
            # Limiter la taille du cache utilisateurs
            if len(self.user_cache) > self.max_cache_size:
                items = list(self.user_cache.items())
                items.sort(key=lambda x: x[1].get('last_seen', 0), reverse=True)
                
                self.user_cache = dict(items[:self.max_cache_size//2])
                print(f"[CACHE] Cache utilisateurs nettoyé: {len(self.user_cache)} éléments")
                
        except Exception as e:
            print(f"[CACHE] Erreur nettoyage caches: {e}")
    
    async def optimize_tasks(self):
        """Optimiser les tâches en cours"""
        try:
            # Annuler les tâches trop longues
            tasks = [task for task in asyncio.all_tasks() if not task.done()]
            
            for task in tasks[:10]:  # Limiter à 10 tâches
                if hasattr(task, '_start_time'):
                    runtime = datetime.now() - task._start_time
                    if runtime.total_seconds() > 300:  # 5 minutes max
                        task.cancel()
                        print(f"[TASK] Tâche annulée (trop longue): {task.get_name()}")
                        
        except Exception as e:
            print(f"[TASK] Erreur optimisation tâches: {e}")
    
    def cache_message(self, message_id, message_data):
        """Mettre en cache un message avec limitation"""
        if len(self.message_cache) < self.max_cache_size:
            self.message_cache[message_id] = {
                **message_data,
                'timestamp': datetime.now().timestamp()
            }
    
    def cache_user(self, user_id, user_data):
        """Mettre en cache un utilisateur avec limitation"""
        if len(self.user_cache) < self.max_cache_size:
            self.user_cache[user_id] = {
                **user_data,
                'last_seen': datetime.now().timestamp()
            }
    
    def get_cached_message(self, message_id):
        """Récupérer un message du cache"""
        return self.message_cache.get(message_id)
    
    def get_cached_user(self, user_id):
        """Récupérer un utilisateur du cache"""
        return self.user_cache.get(user_id)

def optimized_task(func):
    """Décorateur pour optimiser les tâches"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = datetime.now()
        task = asyncio.current_task()
        task._start_time = start_time
        
        try:
            result = await func(*args, **kwargs)
            
            # Logger si la tâche prend trop de temps
            runtime = datetime.now() - start_time
            if runtime.total_seconds() > 10:
                print(f"[TASK] Tâche lente: {func.__name__} - {runtime.total_seconds():.1f}s")
            
            return result
            
        except Exception as e:
            runtime = datetime.now() - start_time
            print(f"[TASK] Erreur tâche {func.__name__} ({runtime.total_seconds():.1f}s): {e}")
            raise
            
    return wrapper

def memory_efficient(max_items=100):
    """Décorateur pour les fonctions gourmandes en mémoire"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Vérifier la mémoire avant
            try:
                process = psutil.Process(os.getpid())
                memory_mb = process.memory_info().rss / 1024 / 1024
                
                if memory_mb > 400:  # Approche de la limite
                    gc.collect()  # Nettoyer avant d'exécuter
                
            except:
                pass
            
            try:
                result = await func(*args, **kwargs)
                
                # Limiter la taille des résultats
                if hasattr(result, '__len__') and len(result) > max_items:
                    result = result[:max_items]
                
                return result
                
            except Exception as e:
                print(f"[MEMORY] Erreur fonction {func.__name__}: {e}")
                return []
                
        return wrapper
    return decorator

# Optimisations spécifiques pour les cogs
class CogOptimizer:
    """Optimisations pour les cogs"""
    
    @staticmethod
    def optimize_voice_cog():
        """Optimisations pour le cog vocal"""
        return {
            'max_members_per_operation': 20,  # Réduit de 50 à 20
            'move_delay': 1.0,  # Augmenté pour éviter le rate limiting
            'cache_size': 25,  # Réduit de 50 à 25
            'batch_size': 5  # Traiter par petits lots
        }
    
    @staticmethod
    def optimize_logs_cog():
        """Optimisations pour le cog logs"""
        return {
            'max_history_messages': 50,  # Réduit
            'cache_duration': 300,  # 5 minutes au lieu de 1 heure
            'max_embed_fields': 10,  # Limiter les champs embed
            'compression_enabled': True
        }
    
    @staticmethod
    def optimize_search_cog():
        """Optimisations pour les recherches"""
        return {
            'max_channels_to_search': 20,  # Réduit de 50 à 20
            'max_messages_per_channel': 50,  # Réduit de 100 à 50
            'search_timeout': 30,  # Timeout plus court
            'result_limit': 15  # Moins de résultats
        }

# Configuration pour Render gratuit
RENDER_CONFIG = {
    # Limites de ressources
    'memory_limit_mb': 512,
    'cpu_limit_percent': 80,
    'disk_limit_mb': 100,
    
    # Optimisations automatiques
    'auto_cleanup': True,
    'cleanup_interval_minutes': 30,
    'cache_size_limit': 100,
    
    # Limites de performance
    'max_concurrent_tasks': 10,
    'task_timeout_seconds': 300,
    'message_rate_limit': 5,  # Messages par seconde
    
    # Monitoring
    'enable_monitoring': True,
    'log_level': 'WARNING',  # Réduire les logs
    'debug_mode': False
}

# Fonctions de monitoring
async def check_render_health():
    """Vérifier la santé du bot sur Render"""
    try:
        process = psutil.Process(os.getpid())
        
        stats = {
            'memory_mb': process.memory_info().rss / 1024 / 1024,
            'cpu_percent': process.cpu_percent(),
            'threads': process.num_threads(),
            'open_files': process.num_fds() if hasattr(process, 'num_fds') else 0
        }
        
        # Alertes si nécessaire
        if stats['memory_mb'] > 450:
            print(f"[HEALTH] ⚠️ Mémoire élevée: {stats['memory_mb']:.1f} MB")
        
        if stats['cpu_percent'] > 90:
            print(f"[HEALTH] ⚠️ CPU élevé: {stats['cpu_percent']:.1f}%")
        
        return stats
        
    except Exception as e:
        print(f"[HEALTH] Erreur monitoring: {e}")
        return None

# Optimisations pour les événements Discord
class EventOptimizer:
    """Optimiser les événements Discord"""
    
    @staticmethod
    def should_process_message(message):
        """Déterminer si un message doit être traité"""
        # Ignorer les messages trop longs
        if len(message.content) > 2000:
            return False
        
        # Ignorer les messages des bots
        if message.author.bot:
            return False
        
        # Limiter le traitement par utilisateur
        if hasattr(EventOptimizer, '_user_message_counts'):
            user_id = message.author.id
            now = datetime.now().timestamp()
            
            if user_id not in EventOptimizer._user_message_counts:
                EventOptimizer._user_message_counts[user_id] = []
            
            # Nettoyer les anciens messages (plus de 1 minute)
            EventOptimizer._user_message_counts[user_id] = [
                ts for ts in EventOptimizer._user_message_counts[user_id]
                if now - ts < 60
            ]
            
            # Limiter à 10 messages par minute par utilisateur
            if len(EventOptimizer._user_message_counts[user_id]) >= 10:
                return False
            
            EventOptimizer._user_message_counts[user_id].append(now)
        else:
            EventOptimizer._user_message_counts = {}
        
        return True
    
    @staticmethod
    def optimize_embed(embed):
        """Optimiser un embed pour économiser la mémoire"""
        # Limiter la taille des descriptions
        if embed.description and len(embed.description) > 1000:
            embed.description = embed.description[:997] + "..."
        
        # Limiter le nombre de champs
        if len(embed.fields) > 15:
            embed.fields = embed.fields[:15]
        
        # Limiter la taille des champs
        for field in embed.fields:
            if len(field.value) > 500:
                field.value = field.value[:497] + "..."
        
        return embed
