# 📂 Dossier COGS

Ce dossier contient tous les modules du bot :

## 🎮 Modules principaux

### 🎫 tickets.py - **LE PLUS IMPORTANT**
**Système complet de tickets avec panels interactifs**
- Configuration : `+ticket setup`
- Catégories personnalisables avec questionnaires
- Panels permanents avec boutons
- Messages personnalisables
- Gestion complète des tickets

### 🎤 voice.py - **Gestion vocale avancée**
**Commandes vocales puissantes**
- Déplacements : `+moove`, `+server`, `+split`
- Auto-balance : `+autobalance`, `+smartbalance`
- Fun : `+shuffle`, `+spin`, `+russianroulette`
- Contrôle : `+muteall`, `+lockvoice`

### 🔨 moderation.py - **Modération**
**Outils de modération**
- Classiques : `+ban`, `+kick`, `+mute`
- Avancés : Anti-raid, logs, sanctions

### ⚙️ system.py - **Commandes système**
**Administration du bot**
- Informations : `+botinfo`, `+serverinfo`
- Maintenance : `+restart`, `+reload`
- Utilitaires divers

### 📝 logs.py - **Gestion des logs**
**Système de logging**
- Logs des actions
- Surveillance
- Rapports

### 🎮 games.py - **Jeux et fun**
**Mini-jeux Discord**
- Jeux de société
 divertissement

## 🔧 Structure d'un module

```python
class NomModule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def commande(self, ctx):
        # Logique de la commande
```

## 📝 Développement

- **Respecte les permissions** avec `@has_role()`
- **Gère les erreurs** avec try/except
- **Utilise les embeds** pour les réponses
- **Sauvegarde les données** dans le dossier `data/`

---
*Chaque module est indépendant et peut être activé/désactivé*
