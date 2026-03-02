import functools
import time
import asyncio
from typing import Callable, Any

class CommandOptimizer:
    """Optimiseur de commandes pour améliorer les performances"""
    
    def __init__(self):
        self.command_stats = {}
        self.cooldown_cache = {}
        self.rate_limits = {}
    
    def cooldown(self, seconds: int = 1, max_calls: int = 1):
        """Décorateur de cooldown optimisé"""
        def decorator(func: Callable):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                # Récupérer l'ID de l'utilisateur
                ctx = args[0] if args else kwargs.get('ctx')
                if not ctx:
                    return await func(*args, **kwargs)
                
                user_id = ctx.author.id
                command_name = func.__name__
                
                # Vérifier le cooldown
                current_time = time.time()
                cache_key = f"{user_id}_{command_name}"
                
                if cache_key in self.cooldown_cache:
                    last_calls = self.cooldown_cache[cache_key]
                    # Nettoyer les anciens appels
                    last_calls = [call_time for call_time in last_calls if current_time - call_time < seconds]
                    
                    if len(last_calls) >= max_calls:
                        remaining_time = seconds - (current_time - last_calls[0])
                        await ctx.send(f"⏱️ Cooldown: {remaining_time:.1f}s restantes")
                        return
                    
                    self.cooldown_cache[cache_key] = last_calls + [current_time]
                else:
                    self.cooldown_cache[cache_key] = [current_time]
                
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    # Nettoyer le cooldown en cas d'erreur
                    if cache_key in self.cooldown_cache:
                        last_calls = self.cooldown_cache[cache_key]
                        self.cooldown_cache[cache_key] = [call_time for call_time in last_calls if current_time - call_time < seconds]
                    raise e
            
            return wrapper
        return decorator
    
    def rate_limit(self, calls_per_minute: int = 30):
        """Limite de taux par utilisateur"""
        def decorator(func: Callable):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                ctx = args[0] if args else kwargs.get('ctx')
                if not ctx:
                    return await func(*args, **kwargs)
                
                user_id = ctx.author.id
                current_time = time.time()
                
                # Nettoyer les anciens appels
                if user_id in self.rate_limits:
                    self.rate_limits[user_id] = [
                        call_time for call_time in self.rate_limits[user_id]
                        if current_time - call_time < 60
                    ]
                else:
                    self.rate_limits[user_id] = []
                
                # Vérifier la limite
                if len(self.rate_limits[user_id]) >= calls_per_minute:
                    await ctx.send(f"⚠️ Limite de taux atteinte: {calls_per_minute} appels/minute")
                    return
                
                self.rate_limits[user_id].append(current_time)
                
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    # Nettoyer en cas d'erreur
                    if user_id in self.rate_limits:
                        current_time = time.time()
                        self.rate_limits[user_id] = [
                            call_time for call_time in self.rate_limits[user_id]
                            if current_time - call_time < 60
                        ]
                    raise e
            
            return wrapper
        return decorator
    
    def cache_result(self, ttl_seconds: int = 300):
        """Cache les résultats des commandes"""
        def decorator(func: Callable):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                ctx = args[0] if args else kwargs.get('ctx')
                if not ctx:
                    return await func(*args, **kwargs)
                
                # Créer une clé de cache
                cache_key = f"{func.__name__}_{str(args)}_{str(kwargs)}"
                current_time = time.time()
                
                # Vérifier le cache
                if hasattr(self, '_result_cache'):
                    if cache_key in self._result_cache:
                        cached_data = self._result_cache[cache_key]
                        if current_time - cached_data['timestamp'] < ttl_seconds:
                            return cached_data['result']
                
                # Exécuter la fonction
                start_time = time.time()
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Mettre en cache
                if not hasattr(self, '_result_cache'):
                    self._result_cache = {}
                
                self._result_cache[cache_key] = {
                    'result': result,
                    'timestamp': current_time,
                    'execution_time': execution_time
                }
                
                # Nettoyer le cache
                if len(self._result_cache) > 1000:
                    current_time = time.time()
                    self._result_cache = {
                        key: data for key, data in self._result_cache.items()
                        if current_time - data['timestamp'] < ttl_seconds
                    }
                
                return result
            
            return wrapper
        return decorator
    
    def measure_performance(self, func: Callable):
        """Mesure les performances d'une commande"""
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            start_memory = self._get_memory_usage()
            
            try:
                result = await func(*args, **kwargs)
                
                end_time = time.time()
                end_memory = self._get_memory_usage()
                
                execution_time = (end_time - start_time) * 1000  # ms
                memory_diff = end_memory - start_memory
                
                # Logger les stats
                if not hasattr(self, 'performance_stats'):
                    self.performance_stats = {}
                
                func_name = func.__name__
                if func_name not in self.performance_stats:
                    self.performance_stats[func_name] = {
                        'calls': 0,
                        'total_time': 0,
                        'avg_time': 0,
                        'max_time': 0,
                        'memory_usage': []
                    }
                
                stats = self.performance_stats[func_name]
                stats['calls'] += 1
                stats['total_time'] += execution_time
                stats['avg_time'] = stats['total_time'] / stats['calls']
                stats['max_time'] = max(stats['max_time'], execution_time)
                stats['memory_usage'].append(memory_diff)
                
                # Garder seulement les 100 dernières mesures
                if len(stats['memory_usage']) > 100:
                    stats['memory_usage'] = stats['memory_usage'][-50:]
                
                return result
                
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                print(f"Erreur dans {func.__name__} après {execution_time:.2f}ms: {e}")
                raise e
        
        return wrapper
    
    def _get_memory_usage(self):
        """Obtenir l'utilisation mémoire actuelle"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # MB
        except:
            return 0
    
    def batch_process(self, items: list, batch_size: int = 10, delay: float = 0.1):
        """Traiter les éléments par lots pour éviter les rate limits"""
        async def process_batches(process_func: Callable):
            results = []
            
            for i in range(0, len(items), batch_size):
                batch = items[i:i + batch_size]
                
                try:
                    batch_results = await process_func(batch)
                    if isinstance(batch_results, list):
                        results.extend(batch_results)
                    else:
                        results.append(batch_results)
                    
                    # Délai entre les batches
                    if i + batch_size < len(items):
                        await asyncio.sleep(delay)
                        
                except Exception as e:
                    print(f"Erreur batch {i//batch_size}: {e}")
                    continue
            
            return results
        
        return process_batches
    
    def optimize_discord_calls(self, func: Callable):
        """Optimiser les appels Discord"""
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            ctx = args[0] if args else kwargs.get('ctx')
            if not ctx:
                return await func(*args, **kwargs)
            
            # Désactuer les typing pour les commandes longues
            if hasattr(ctx, 'typing'):
                await ctx.typing()
            
            # Limiter les appels API
            original_send = ctx.send
            call_count = 0
            
            async def rate_limited_send(*send_args, **send_kwargs):
                nonlocal call_count
                call_count += 1
                
                if call_count > 5:  # Limite de 5 messages par commande
                    await asyncio.sleep(1)
                    call_count = 1
                
                return await original_send(*send_args, **send_kwargs)
            
            ctx.send = rate_limited_send
            
            try:
                result = await func(*args, **kwargs)
                ctx.send = original_send  # Restaurer
                return result
            except Exception as e:
                ctx.send = original_send  # Restaurer
                raise e
        
        return wrapper
    
    def get_performance_stats(self):
        """Obtenir les statistiques de performance"""
        if not hasattr(self, 'performance_stats'):
            return {}
        
        stats = {}
        for func_name, data in self.performance_stats.items():
            stats[func_name] = {
                'calls': data['calls'],
                'avg_time': data['avg_time'],
                'max_time': data['max_time'],
                'memory_avg': sum(data['memory_usage']) / len(data['memory_usage']) if data['memory_usage'] else 0
            }
        
        return stats
    
    def clear_cache(self):
        """Vider tous les caches"""
        self.cooldown_cache.clear()
        self.rate_limits.clear()
        if hasattr(self, '_result_cache'):
            self._result_cache.clear()
        if hasattr(self, 'performance_stats'):
            self.performance_stats.clear()

# Instance globale
command_optimizer = CommandOptimizer()
