# 🤖 Bot Stark - Bot Discord Public Complet

## 📋 Table des matières

- [🎯 Présentation](#-présentation)
- [✨ Fonctionnalités principales](#-fonctionnalités-principales)
- [🛡️ Modération avancée](#️-modération-avancée)
- [🎤 Gestion vocale complète](#-gestion-vocale-complète)
- [🎮 Jeux et divertissement](#-jeux-et-divertissement)
- [🎉 Fonctionnalités communautaires](#-fonctionnalités-communautaires)
- [🛠️ Utilitaires avancés](#️-utilitaires-avancés)
- [😂 Fun et amusement](#-fun-et-amusement)
- [⚙️ Personnalisation complète](#️-personnalisation-complète)
- [📊 Optimisation des performances](#-optimisation-des-performances)
- [🚀 Installation](#-installation)
- [📚 Documentation complète](#-documentation-complète)

---

## 🎯 Présentation

**Bot Stark** est un bot Discord **complet et modulable** conçu pour les serveurs communautaires. Avec plus de **100 commandes** réparties en **8 catégories**, il offre toutes les fonctionnalités nécessaires pour gérer un serveur Discord moderne.

### 🌟 Points forts

- ✅ **100+ commandes** dans 8 catégories
- ✅ **Interface de configuration** complète et intuitive
- ✅ **Personnalisation totale** du bot
- ✅ **Optimisation des performances** automatique
- ✅ **Système de permissions** flexible
- ✅ **Monitoring** en temps réel
- ✅ **Compatible** avec tous les serveurs

---

## ✨ Fonctionnalités principales

### 🎛️ Interface moderne
- **Menu sélecteur** de catégories interactif
- **Panneau de configuration** avec boutons
- **Help intelligent** avec recherche et suggestions
- **Embeds stylisés** et colorés

### 🔧 Configuration complète
- **Nom, avatar, bannière** personnalisables
- **Préfixe** modifiable
- **Bio et statut** configurables
- **Thèmes de couleurs** personnalisables
- **Fonctionnalités** activables/désactivables

### 📊 Monitoring avancé
- **Statistiques de performance** en temps réel
- **Optimisation automatique** toutes les 5 minutes
- **Gestion du cache** intelligente
- **Alertes** de performance

---

## 🛡️ Modération avancée

### ⚠️ Système de warns
```bash
+warn @User Spam                    # Avertir un membre
+warns @User                        # Voir les warns d'un membre
+clearwarns @User                    # Supprimer tous les warns
```

**Fonctionnalités :**
- 📊 **Système de points** avec sanctions automatiques
- 📝 **Logs détaillés** de toutes les actions
- ⏰ **Sanctions auto** (mute, kick, ban) selon les warns
- 💾 **Persistance** des données

### 🔇 Système de mute avancé
```bash
+mute @User 1h Spam               # Muet pour 1h
+unmute @User                       # Rendre la parole
+tempban @User 1d Infraction       # Ban temporaire
```

### 🔒 Modération serveur
```bash
+slowmode 5                         # Mode lent 5 secondes
+lockdown                            # Verrouiller tout le serveur
+unlockdown                          # Déverrouiller le serveur
+modlogs                             # Voir les logs de modération
```

---

## 🎤 Gestion vocale complète

### 🔄 Équilibrage intelligent
```bash
+equilibrer #Gaming 3             # Équilibrer 3 par salon
+equilibrer_auto #Gaming            # Équilibrage automatique
+immobiles                          # Voir les membres immobiles
+force_move @User #Salon           # Forcer déplacement
```

### 🎯 Déplacements avancés
```bash
+move_all_except @Admin #Réunion    # Déplacer tout sauf un
+move_from_category #Gaming #Général # Déplacer d'une catégorie
+shuffle_category #Gaming            # Mélanger aléatoirement
+gather_all #Réunion                 # Rassembler tout le monde
```

### 🏗️ Gestion des salons
```bash
+create_voice_rooms #Gaming 5 Team  # Créer 5 salons
+clone_voice_channel #Gaming Clone   # Cloner un salon
+swap_channels #Team1 #Team2        # Échanger les membres
+tempvoice Salon Privé               # Salon temporaire
```

### 📊 Monitoring vocal
```bash
+voice_activity #Gaming              # Activité détaillée
+move_afk #AFK 15                 # Déplacer les AFK
+voice_backup #Gaming               # Sauvegarder distribution
+voice_restore backup_gaming.json   # Restaurer distribution
```

---

## 🎮 Jeux et divertissement

### 🎲 Jeux de hasard
```bash
+dice 6                              # Lancer un dé 6 faces
+coin                                 # Pile ou face
+rps pierre                            # Pierre feuille ciseaux
+8ball "Vais-je réussir ?"           # Boule magique 8
```

### 🎭 Jeux interactifs
```bash
+devinelenombre                       # Deviner un nombre
+truth spicy                          # Question vérité épicée
+dare hard                            # Défi difficile
+wyr                                  # Préfères-tu
+rate @User                           # Noter quelqu'un
+ship @User1 @User2                   # Calculer compatibilité
```

---

## 🎉 Fonctionnalités communautaires

### 💡 Suggestions et sondages
```bash
+suggest Ajouter un salon de mèmes     # Faire une suggestion
+poll "Quel est le meilleur ?" "Option 1" "Option 2"  # Créer un sondage
+giveaway 1h Nitro Classic           # Lancer un giveaway
+reactionrole 123456789 🎮 @Gamer   # Rôle par réaction
```

### 📊 Statistiques serveur
```bash
+serverstats                          # Statistiques complètes
+userinfo @User                       # Info utilisateur
+serverinfo                           # Info serveur
+roleinfo @Admin                      # Info rôle
+channelinfo #général                # Info salon
```

---

## 🛠️ Utilitaires avancés

### 🔍 Outils de modération
```bash
+snipe                                # Voir dernier message supprimé
+editsnipe                            # Voir dernier message modifié
+slowmode 5                           # Mode lent
+lockdown / unlockdown                 # Lockdown serveur
```

### 🎭 Fun utilitaires
```bash
+afk Pause déjeuner                   # Mode AFK
+emoji 😊                              # Info émoji
+steal 😊 CoolEmoji                    # Voler émoji
+firstmessage #général                # Premier message du salon
+createinvite #général 5 24           # Créer invitation
```

### 🧮 Outils pratiques
```bash
+calc 2+2*3                           # Calculatrice
+remind 1h Réunion importante          # Rappel
+translate fr "Hello world"             # Traduction
+reverse "Bonjour le monde"             # Inverser texte
+clap "C'est super"                   # Ajouter applause
+uwu "Hello world"                    # Transformer en uwu
+ascii HELLO                           # Art ASCII
+emojify "HELLO"                      # Texte en émojis
```

---

## 😂 Fun et amusement

### 😂 Divertissement
```bash
+meme gaming                           # Mème aléatoire
+joke                                 # Blague aléatoire
+fact                                 # Fait intéressant
+quote @User                          # Citer un utilisateur
+8ball "Question ?"                   # Boule magique
```

### 🎭 Transformations
```bash
+reverse "Texte à inverser"          # Inverser texte
+clap "Texte à applaudir"           # Ajouter applause
+uwu "Texte à transformer"           # Transformer en uwu
+ascii "TEXTE"                        # Art ASCII
+emojify "TEXTE"                      # Texte en émojis
```

---

## ⚙️ Personnalisation complète

### 🎨 Apparence du bot
```bash
+setname "Mon Bot Personnalisé"        # Changer nom
+setprefix "!"                        # Changer préfixe
+setbio "Bot de modération avancé"   # Changer bio
+setavatar https://example.com/img.png  # Changer avatar
+setbanner https://example.com/banner.png # Changer bannière
+setstatus dnd                        # Changer statut
+setactivity watching "vos serveurs"   # Changer activité
```

### ⚙️ Configuration avancée
```bash
+config                               # Panneau de configuration interactif
+toggle moderation                    # Activer/désactiver modération
+toggle vocal                         # Activer/désactiver vocal
+toggle games                         # Activer/désactiver jeux
+setconfig features.vocal.max_members 10 # Configuration spécifique
+getconfig bot.name                   # Voir configuration
```

### 🔐 Gestion des permissions
```bash
+addadmin @Admin                      # Ajouter rôle admin
+removeadmin @Admin                   # Retirer rôle admin
+addmod @Modérateur                   # Ajouter rôle modo
+trust @User                          # Ajouter utilisateur de confiance
+blacklist @User                      # Liste noire
```

### 💬 Messages personnalisés
```bash
+setwelcome "Bienvenue {user} sur {server} !"    # Message accueil
+setgoodbye "Au revoir {user} !"              # Message départ
+setlevelup "Félicitations {user}, niveau {level} !" # Message niveau
```

---

## 📊 Optimisation des performances

### 📈 Monitoring en temps réel
```bash
+performance                          # Statistiques complètes
+optimize                            # Optimisation manuelle
+cache                               # Informations cache
+clearcache all                       # Vider tout le cache
```

### ⚡ Optimisations automatiques
- **Garbage collection** toutes les 5 minutes
- **Nettoyage du cache** intelligent
- **Monitoring** CPU et mémoire
- **Rate limiting** automatique
- **Batch processing** pour éviter les limites

---

## 🚀 Installation

### 📋 Prérequis
- Python 3.8+
- nextcord 2.0+
- psutil (pour le monitoring)
- aiohttp (pour les requêtes HTTP)

### 🔧 Installation rapide
```bash
# Cloner le dépôt
git clone https://github.com/votre-repo/bot-stark.git

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec votre token Discord

# Lancer le bot
python bot.py
```

### 📁 Structure des fichiers
```
bot-stark/
├── bot.py                 # Fichier principal
├── config.py              # Configuration
├── requirements.txt        # Dépendances
├── .env                  # Variables d'environnement
├── cogs/                 # Modules du bot
│   ├── moderation_enhanced.py
│   ├── community_features.py
│   ├── utility_commands.py
│   ├── fun_commands.py
│   ├── performance_optimizer.py
│   ├── vocal.py
│   ├── social.py
│   ├── config_panel.py
│   ├── help_system.py
│   ├── bot_customization.py
│   └── ...
├── utils/                # Utilitaires
│   ├── config_manager.py
│   ├── command_optimizer.py
│   └── ...
└── data/                 # Données sauvegardées
    ├── warns/
    ├── modlogs/
    ├── backups/
    └── bot_config.json
```

---

## 📚 Documentation complète

### 🎯 Commande d'aide principale
```bash
+help                    # Menu avec sélecteur de catégories
+help <commande>        # Aide détaillée sur une commande
```

### 📚 Catégories disponibles

#### 🛡️ **Modération** (15 commandes)
- warn, warns, clearwarns, mute, unmute, tempban, kick, ban, slowmode, lockdown, unlockdown, modlogs

#### 🎤 **Vocal** (21 commandes)
- déplacer, équilibrer, équilibrer_auto, immobiles, force_move, move_all_except, move_from_category, shuffle_category, gather_all, create_voice_rooms, clone_voice_channel, swap_channels, tempvoice, voice_activity, move_afk, voice_backup, voice_restore, voice_limits, voice_cleanup

#### 🎮 **Jeux** (10 commandes)
- dice, coin, rps, devinelenombre, 8ball, truth, dare, wyr, rate, ship

#### 🎉 **Communauté** (10 commandes)
- suggest, poll, giveaway, reactionrole, serverstats, userinfo, serverinfo, roleinfo, channelinfo

#### 🛠️ **Utilitaires** (12 commandes)
- afk, snipe, editsnipe, emoji, steal, firstmessage, createinvite, calc, remind, translate, reverse, clap, uwu, ascii, emojify

#### 😂 **Fun** (10 commandes)
- meme, joke, fact, quote, reverse, clap, uwu, ascii, emojify

#### ⚙️ **Configuration** (10 commandes)
- config, setname, setprefix, setbio, setavatar, setbanner, setstatus, setactivity, toggle, setconfig, getconfig

#### 📊 **Performance** (4 commandes)
- performance, optimize, cache, clearcache

---

### 🔧 Configuration détaillée

#### 🎨 Personnalisation de l'apparence
```json
{
  "bot": {
    "name": "Bot Stark",
    "prefix": "+",
    "description": "Bot Discord multifonctionnel"
  },
  "appearance": {
    "profile_picture": "url_avatar",
    "banner": "url_banner",
    "bio": "Bot Discord multifonctionnel",
    "status": "online",
    "activity_type": "watching",
    "activity_text": "vos serveurs",
    "color_scheme": {
      "primary": 0x3498db,
      "success": 0x2ECC71,
      "warning": 0xF39C12,
      "error": 0xE74C3C
    }
  }
}
```

#### ⚙️ Configuration des fonctionnalités
```json
{
  "features": {
    "moderation": {
      "enabled": true,
      "auto_mod": false
    },
    "vocal": {
      "enabled": true,
      "auto_balance": false,
      "max_members_per_channel": 5
    },
    "social": {
      "enabled": true,
      "live_notifications": true
    },
    "games": {
      "enabled": true,
      "daily_rewards": false
    }
  }
}
```

---

## 🌟 Avantages uniques

### 🚀 **Performance optimisée**
- **Monitoring** en temps réel du CPU et mémoire
- **Auto-cleanup** toutes les 5 minutes
- **Cache intelligent** pour éviter les requêtes répétées
- **Rate limiting** automatique
- **Batch processing** pour les opérations massives

### 🎨 **Personnalisation totale**
- **Interface de configuration** graphique
- **Thèmes de couleurs** personnalisables
- **Messages** entièrement modifiables
- **Permissions** granulaires
- **Configuration** par serveur possible

### 🛡️ **Modération avancée**
- **Système de warns** avec sanctions automatiques
- **Logs détaillés** de toutes les actions
- **Rôles par réaction** automatiques
- **Lockdown** serveur complet
- **Snipe** et éditions

### 🎤 **Gestion vocale complète**
- **21 commandes** vocales spécialisées
- **Équilibrage** automatique intelligent
- **Salons temporaires** auto-supprimés
- **Sauvegarde/Restauration** des distributions
- **Détection** des membres immobiles

---

## 🤝 Support et communauté

### 📞 Obtenir de l'aide
- **Documentation complète** dans ce README
- **Commande +help** avec menu interactif
- **Support** sur le serveur Discord officiel
- **Issues GitHub** pour les rapports de bugs

### 🔄 Mises à jour
- **Mises à jour** automatiques
- **Changelog** détaillé
- **Migration** automatique des configurations
- **Backward compatibility** préservée

---

## 📜 Licence

Ce projet est sous licence **MIT**. Vous êtes libre de :
- ✅ Utiliser le bot
- ✅ Le modifier
- ✅ Le distribuer
- ✅ L'utiliser commercialement

---

## 🎯 Conclusion

**Bot Stark** est la solution **complète** pour votre serveur Discord. Avec plus de **100 commandes**, une **interface moderne**, et des **performances optimisées**, il offre tout ce dont un serveur communautaire moderne a besoin.

### 🚀 Prêt à commencer ?

1. **Clonez** le dépôt
2. **Installez** les dépendances
3. **Configurez** votre token
4. **Lancez** le bot
5. **Personnalisez** avec `+config`

---

*Bot Stark - Fait avec ❤️ par la communauté Discord*
