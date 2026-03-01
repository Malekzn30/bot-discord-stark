# 🎤 GUIDE DES COMMANDES VOCAL

## 📋 Commandes de déplacement

### 🚚 Déplacements simples
```bash
+moove @user #salon              # Déplacer 1 personne
+mooveusers @u1 @u2 #salon       # Déplacer plusieurs personnes
+mooveall #salon                 # Déplacer tout le vocal actuel
+mooverandom @user <ID_CAT>      # Déplacer 1 personne aléatoirement
+mooverandomusers @u1 @u2 <ID_CAT> # Déplacer plusieurs aléatoirement
+mooveallrandom <ID_CAT>         # Déplacer tout le vocal aléatoirement
```

### 🌐 Commandes serveur
```bash
+server #salon                   # Déplacer tout le serveur (alias de +mooveserver)
+mooveserver #salon              # Déplacer tout le serveur
+autoregroup #salon              # Regrouper tout le serveur
```

### 🔄 Rotations et mélanges
```bash
+rotateusers @u1 @u2 <ID_CAT>    # Faire tourner des personnes
+rotateall <ID_CAT>              # Faire tourner tout le vocal
+rotaterandom <ID_CAT>           # Rotation aléatoire
+rotategroups <ID_CAT>           # Rotation des groupes entiers
```

### 🎲 Splits et séparations
```bash
+split <ID_CAT>                  # Séparer en 2 groupes et déplacer
+randomsplit                     # Montrer les 2 groupes (sans déplacer)
+autosplit <ID_CAT> <GROUPES>    # Séparer automatiquement en X groupes
```

### ⚖️ Auto-balance
```bash
+autobalance <ID_CAT>            # Équilibrer automatiquement les salons
+autosort <ID_CAT>               # Trier par rôle
+smartbalance <ID_CAT>           # Équilibrer intelligent
+rebalanceserver                 # Rééquilibrer tout le serveur
```

## 🎯 Utilisation pratique

### Pour obtenir un ID de catégorie :
1. Fais clic droit sur une catégorie vocale
2. Copie l'ID (active le mode développeur dans Paramètres > Avancé)

### Exemples concrets :
```bash
# Déplacer StarK92 dans le salon Support
+moove @StarK92 #support

# Séparer tout le monde en 2 groupes dans la catégorie "Jeux"
+split 123456789012345678

# Équilibrer automatiquement la catégorie "Team"
+autobalance 123456789012345678

# Déplacer tout le serveur dans le salon Général
+server #général
```

## 🔧 Dépannage

### Si les commandes ne répondent pas :
1. **Vérifie le rôle** : Assure-toi d'avoir le rôle autorisé (ID: 1469665367881420841)
2. **Permissions bot** : Le bot doit avoir les permissions de déplacer les membres
3. **Sois en vocal** : Certaines commandes nécessitent que tu sois en vocal

### Messages d'erreur courants :
- `❌ Tu dois être en vocal` → Rejoins un salon vocal
- `❌ Utilisation` → Vérifie la syntaxe de la commande
- `❌ Aucun membre` → Mentionne des membres valides

### Permissions requises :
- **Bot** : Déplacer les membres, Voir les salons vocaux
- **Utilisateur** : Rôle autorisé, être en vocal (pour certaines commandes)

## 🎮 Commandes fun

### 🎲 Fun et jeux
```bash
+shuffle start @user <ID_CAT>    # Lancer le shuffle
+shufflestop                     # Arrêter tous les shuffles
+spin @user <ID_CAT>             # Faire tourner quelqu'un
+spinall <ID_CAT>                # Faire tourner tout le monde
+russianroulette <ID_CAT>        # Roulette russe vocale
+randomkickvoice                 # Kick vocal aléatoire
```

### 🎵 Musique et contrôle
```bash
+muteall                         # Mute tout le vocal
+unmuteall                       # Unmute tout le vocal
+deafenall                       # Deafen tout le vocal
+undeafenall                     # Undeafen tout le vocal
+clearvoice #salon               # Vider un salon
+lockvoice #salon                # Verrouiller un salon
+unlockvoice #salon              # Déverrouiller un salon
```

## 📝 Notes importantes

- **ID de catégorie** : Clique droit > Copier l'ID (mode développeur activé)
- **Rôle requis** : Tu dois avoir le rôle autorisé pour utiliser ces commandes
- **Permissions bot** : Le bot doit pouvoir déplacer les membres
- **Sauvegarde** : La commande `+back` renvoie tout le monde d'où ils viennent

Le système est maintenant complet avec toutes les commandes dont tu as besoin ! 🚀
