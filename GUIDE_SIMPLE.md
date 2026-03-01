# 🤖 StarK92 Bot - Guide Simple

## 📁 Structure des fichiers

```
📦 bot/
├── 🤖 bot.py              # Point d'entrée du bot
├── ⚙️ config.py           # Configuration principale
├── 📋 requirements.txt      # Dépendances Python
├── 📄 Procfile           # Configuration Render
├── 📂 cogs/              # Modules du bot
│   ├──  voice.py        # Gestion vocale
│   ├── 🔨 moderation.py   # Modération
│   ├── ⚙️ system.py       # Commandes système
│   ├── 📝 logs.py         # Logs
│   └── 🎮 games.py        # Jeux
├── 📂 data/              # Données
└── 📂 guides/            # Guides utilisateurs
    └── VOICE_GUIDE.md     # Guide commandes vocales
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

## � Commandes principales

### Vocal
- `+moove @user #salon` - Déplacer un membre
- `+mooveall #salon` - Déplacer tout le vocal
- `+server #salon` - Déplacer tout le serveur
- `+split <ID_CAT>` - Séparer en 2 groupes
- `+autobalance <ID_CAT>` - Équilibrer automatiquement

### Jeux
- `+devinelenombre 1 100 #salon` - Jeu de devinette
- `+jeuxencours` - Voir les jeux en cours

### Modération
- `+kick @user` - Expulser un membre
- `+ban @user` - Bannir un membre
- `+mute @user` - Rendre muet
- `+warn @user "raison"` - Avertir
- `+warn_leaderboard` - Classement des avertissements

### Système
- `+botinfo` - Informations du bot
- `+serverinfo` - Informations du serveur
- `+restart` - Redémarrer le bot
- `+embed "Titre" "Description" "Footer"` - Créer un embed personnalisé

## 🔧 Configuration

Dans `config.py` tu peux modifier :
- `AUTHORIZED_ROLE_ID` - Rôle autorisé (défaut: 1469665367881420841)
- `BOT_PREFIX` - Préfixe des commandes (défaut: "+")
- `BOT_COLOR` - Couleur du bot (défaut: 0x3498db)

## 📚 Documentation complète

- `guides/VOICE_GUIDE.md` - Guide complet des commandes vocales

---
**Bot développé pour StarK92 ✩ Version 2.0**
