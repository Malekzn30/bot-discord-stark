# 🤖 StarK92 Bot - Guide Simple

## 📁 Structure des fichiers

```
📦 bot/
├── 🤖 bot.py              # Point d'entrée du bot
├── ⚙️ config.py           # Configuration principale
├── 📋 requirements.txt      # Dépendances Python
├── 📄 Procfile           # Configuration Render
├── 📂 cogs/              # Modules du bot
│   ├── 🎫 tickets.py      # Système de tickets
│   ├── 🎤 voice.py        # Gestion vocale
│   ├── 🔨 moderation.py   # Modération
│   ├── ⚙️ system.py       # Commandes système
│   ├── 📝 logs.py         # Logs
│   └── 🎮 games.py        # Jeux
├── 📂 data/              # Données
│   ├── tickets_config.json  # Configuration tickets
│   ├── tickets_data.json    # Données tickets
│   └── tickets_panels.json  # Panels de tickets
├── 📂 guides/            # Guides utilisateurs
│   ├── TICKETS_GUIDE.md   # Guide complet tickets
│   └── VOICE_GUIDE.md     # Guide commandes vocales
└── 📂 docs/              # Documentation technique
```

## 🚀 Démarrage rapide

1. **Configuration** :
   - Crée un fichier `.env` avec `DISCORD_TOKEN=votre_token`
   - Modifie `config.py` si besoin

2. **Installation** :
   ```bash
   pip install -r requirements.txt
   ```

3. **Lancement** :
   ```bash
   python bot.py
   ```

## 🎫 Commandes principales

### Tickets
- `+ticket` - Voir les panels et créer des tickets
- `+ticket setup` - Configuration des tickets
- `+ticket setup panel_add #salon "Titre"` - Créer un panel

### Vocal
- `+moove @user #salon` - Déplacer un membre
- `+mooveall #salon` - Déplacer tout le vocal
- `+server #salon` - Déplacer tout le serveur
- `+split <ID_CAT>` - Séparer en 2 groupes
- `+autobalance <ID_CAT>` - Équilibrer automatiquement

### Jeux
- `+devinelenombre 1 100 #salon` - Jeu de devinette
- `+jeuxencours` - Voir les jeux en cours

## 🔧 Configuration

Dans `config.py` tu peux modifier :
- `AUTHORIZED_ROLE_ID` - Rôle autorisé (défaut: 1469665367881420841)
- `BOT_PREFIX` - Préfixe des commandes (défaut: "+")
- `BOT_COLOR` - Couleur du bot (défaut: 0x3498db)

## 📚 Documentation complète

- `guides/TICKETS_GUIDE.md` - Guide détaillé des tickets
- `guides/VOICE_GUIDE.md` - Guide complet des commandes vocales

---
**Bot développé pour StarK92 ✩ Version 2.0**
