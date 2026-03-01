# Optimisations Render Gratuit (512MB + 0.15 CPU)

## Configuration pour Render

### Environment Variables
```
PYTHONUNBUFFERED=1
```

### Bot Optimizations Appliquées

1. **Intents Minimaux**
   - `members=False` — pas de cache de membres
   - `presences=False` — pas de presences
   - `typing=False` — pas de typing
   - `chunk_guilds_at_startup=False` — pas de chunking au démarrage

2. **Caches Agressifs**
   - `last_moves`: max 50 entrées (voice.py)
   - `active_games`: max 10 jeux simultanés (games.py)
   - Cleanup tous les 10 minutes (au lieu de 30)
   - Timeout des jeux: 30 min (au lieu de 1h)

3. **SQLite Optimisé** (moderation.py)
   - `PRAGMA journal_mode=WAL` — moins d'I/O
   - `PRAGMA synchronous=NORMAL` — performance
   - Index sur `user_id` pour requêtes rapides

4. **Limits de Données**
   - Limit sur `members_top`: 5-10 max
   - Limit sur itérations membres: 500 max par commande
   - Nettoyage garbage collection toutes les 10 min

## Commandes à Éviter sur Render Gratuit

- Très grosses allocations mémoire (serveurs > 50k membres)
- Boucles infinies sans limites

## Suivi Mémoire

```bash
# Sur Render, vérifier la mémoire:
ps aux | grep python
# ou dans le dashboard Render
```

## Troubleshooting

- Si OOM: réduire MAX_CACHE_SIZE à 25
- Si lent: augmenter GAME_TIMEOUT nettoyage
- Si CPU élevé: réduire fréquence cleanup

