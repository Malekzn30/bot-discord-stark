# 📚 Bot Stark - Documentation Complète

## 🎯 **Guide Principal**

### � **Démarrage Rapide**

#### 1️⃣ **Installation**
```bash
# Cloner le projet
git clone <lien-du-bot>
cd bot

# Installer les dépendances
pip install -r requirements.txt

# Configurer le token
# Créer un fichier .env avec:
# DISCORD_TOKEN=ton_token_ici
```

#### 2️⃣ **Lancer le bot**
```bash
python bot.py
```

---

### 🎮 **Commandes Essentielles**

#### 🔨 **Modération**
- `+warn @user "raison"` - Avertir un membre
- `+kick @user` - Expulser un membre
- `+ban @user` - Bannir un membre
- `+mute @user` - Rendre muet
- `+clear 50` - Supprimer 50 messages

#### 🎤 **Vocal**
- `+moove @user #salon` - Déplacer un membre
- `+mooveall #salon` - Déplacer tout le vocal
- `+autobalance <ID_CAT>` - Équilibrer automatiquement
- `+randomsplit` - Séparer en 2 équipes

#### ⚙️ **Système**
- `+botinfo` - Informations du bot
- `+serverinfo` - Informations du serveur
- `+embed "Titre" "Description"` - Créer un embed
- `+help` - Afficher l'aide

#### 🎉 **Bienvenue**
- **Message public** automatique dans le channel de bienvenue
- **Message privé** avec lien d'invitation permanent
- **Comptage correct** des membres (exclut les bots)

#### 🎮 **Jeux**
- `+devinelenombre 1 100 #salon` - Jeu de devinette
- `+dice 6` - Lancer un dé
- `+coin` - Pile ou face
- `+rps pierre` - Pierre-papier-ciseaux

---

### 📊 **Statistiques du Bot**

- **121 commandes** au total
- **6 modules** spécialisés
- **Système de logs** complet
- **Design unifié** professionnel

---

### 🔧 **Configuration**

#### 📁 **Fichiers importants**
- `config.py` - Configuration principale
- `.env` - Token Discord
- `logs/` - Logs du bot
- `cogs/` - Modules de commandes

#### ⚙️ **Personnalisation**
- **PREFIX** : `+` (modifiable dans `config.py`)
- **COULEUR** : Bleu (0x3498db)
- **BRANDING** : `𝐒𝐭𝐚𝐫𝐊𝟗𝟐☆🇵🇸`

---

### �️ **Dépannage Rapide**

#### ❌ **Bot ne démarre pas**
1. **Vérifier le token** dans `.env`
2. **Permissions** : Bot doit avoir les permissions nécessaires
3. **Dépendances** : `pip install -r requirements.txt`

#### ❌ **Commandes ne fonctionnent pas**
1. **Permissions** : Vérifier les rôles du bot
2. **Syntaxe** : Utiliser `+help` pour voir l'aide
3. **Logs** : Regarder dans `logs/bot_YYYYMMDD.log`

#### ❌ **DM de bienvenue non reçu**
1. **Paramètres Discord** : Autoriser les DMs des membres du serveur
2. **Logs du bot** : Voir les erreurs dans les fichiers de logs

---

### 📞 **Support**

#### � **Pour aller plus loin**
- **Documentation complète** : Guides détaillés disponibles
- **Logs avancés** : Système de traçabilité complet
- **Design professionnel** : Embeds standardisés

#### � **En cas de problème**
1. **Regarder les logs** : `logs/bot_YYYYMMDD.log`
2. **Vérifier la configuration** : `config.py`
3. **Consulter l'aide** : `+help`

---

## 🎉 **Conclusion**

Le Bot Stark est un bot Discord **complet et professionnel** avec :

- ✅ **121 commandes** couvrant tous les besoins
- ✅ **6 modules** spécialisés et optimisés
- ✅ **Design unifié** avec branding professionnel
- ✅ **Système de logs** complet pour le monitoring
- ✅ **Messages de bienvenue** automatiques et personnalisés
- ✅ **Documentation** complète et accessible

**Un bot moderne, puissant et facile à utiliser !** 🚀✨

---

*Bot Stark - Créé avec ❤️ pour la communauté Discord*K92 ✩**  
*Version 2.0 - Organisation améliorée*
