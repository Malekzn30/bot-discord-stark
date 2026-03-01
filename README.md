# 🤖 StarK92 Bot - Documentation

## 📁 Organisation des fichiers

```
📦 bot/
├── 📄 bot.py                    # Point d'entrée du bot
├── 📄 config.py                 # Configuration principale
├── 📄 requirements.txt          # Dépendances Python
├── 📄 Procfile                  # Configuration Render
│
├── 📂 cogs/                     # Commandes et fonctionnalités
│   ├── 🎮 games.py             # Jeux et divertissement
│   ├── 📝 logs.py              # Gestion des logs
│   ├── 🔨 moderation.py        # Modération et administration
│   ├── ⚙️ system.py            # Commandes système
│   ├── 🎫 tickets.py           # Système de tickets (principal)
│   └── 🎤 voice.py             # Gestion vocale avancée
│
├── 📂 data/                     # Données et configurations
│   ├── 📄 tickets_config.json  # Configuration des tickets
│   ├── 📄 tickets_data.json    # Données des tickets
│   └── 📄 tickets_panels.json  # Panels de tickets
│
├── 📂 guides/                   # Guides d'utilisation
│   ├── 📄 TICKETS_GUIDE.md      # Guide complet des tickets
│   └── 📄 VOICE_GUIDE.md        # Guide des commandes vocales
│
├── 📂 docs/                     # Documentation technique
│   └── 📄 RENDER_OPTIMIZATION.md # Optimisation pour Render
│
├── 📂 utils/                    # Utilitaires (à venir)
│
└── 📂 .git/                     # Git (ne pas modifier)
```

## 🚀 Démarrage rapide

1. **Configuration** : Modifie `config.py` avec ton token et IDs
2. **Installation** : `pip install -r requirements.txt`
3. **Lancement** : `python bot.py`

## 📚 Documentation

### 🎫 Système de Tickets
- **Guide** : `guides/TICKETS_GUIDE.md`
- **Configuration** : `data/tickets_config.json`
- **Commande principale** : `+ticket setup`

### 🎤 Gestion Vocale
- **Guide** : `guides/VOICE_GUIDE.md`
- **Commandes** : `+moove`, `+split`, `+autobalance`, etc.

### 🔨 Modération
- **Commandes** : `+ban`, `+kick`, `+mute`, etc.
- **Configuration** : Dans `config.py`

## 🛠️ Maintenance

### Sauvegardes importantes
- `data/` - Contient toutes les données des tickets
- `config.py` - Configuration du bot

### Logs
- Les logs sont gérés par `cogs/logs.py`
- Consultez les logs pour le dépannage

## 📞 Support

Pour toute question :
1. Consultez les guides dans `guides/`
2. Vérifiez la documentation dans `docs/`
3. Regardez les commentaires dans les fichiers de code

---
**Bot développé pour StarK92 ✩**  
*Version 2.0 - Organisation améliorée*
