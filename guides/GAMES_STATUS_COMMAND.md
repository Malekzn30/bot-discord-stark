# 🎮 Commande +jeuxencours

## 📋 Description

La commande `+jeuxencours` (alias : `+games`, `+activegames`) permet de voir tous les jeux de "devinelenombre" actuellement en cours sur le serveur.

## 🎯 Utilisation

```bash
+jeuxencours
+games
+activegames
```

## 📊 Informations affichées

Pour chaque jeu en cours, tu verras :

### 🔢 **Nom du salon**
Le salon où le jeu est en cours

### 🔒 **Nombre secret**
Le nombre à deviner (caché avec spoiler)
- Clique sur || pour révéler
- Seul les membres du rôle voient le DM avec le nombre

### 📏 **Intervalle**
Les bornes du nombre (ex: 1-100)

### ⏰ **Démarré il y a**
Temps écoulé depuis le début du jeu

### 👤 **Lancé par**
Le pseudo du membre qui a lancé le jeu

## 📱 Exemple de rendu

```
🎮 Jeux de devinelenombre en cours

🔢 jeux-devin
**Nombre secret** : ||42||
**Intervalle** : 1 - 100
**Démarré il y a** : 5min 23s
**Lancé par** : StarK92

🔢 jeux-fun
**Nombre secret** : ||78||
**Intervalle** : 10 - 50
**Démarré il y a** : 2min 15s
**Lancé par** : AdminBot

Total : 2 jeu(x) en cours
```

## 🔧 Fonctionnalités

### ✅ **Sécurité**
- Seuls les membres avec le rôle autorisé peuvent voir les nombres
- Les nombres sont cachés avec des spoilers
- Le lanceur est identifié

### ✅ **Temps réel**
- Temps écoulé mis à jour automatiquement
- Affichage en minutes et secondes
- Timestamp sur l'embed

### ✅ **Information complète**
- Intervalles exacts des jeux
- Nom du lanceur
- Salon concerné
- Total des jeux en cours

## 🎮 Cas d'usage

### 1. **Vérification rapide**
```bash
+jeuxencours
```
Pour voir si des jeux sont en cours avant d'en lancer un nouveau.

### 2. **Modération**
```bash
+games
```
Pour vérifier quels jeux sont actifs et qui les a lancés.

### 3. **Dépannage**
```bash
+activegames
```
Pour voir les jeux qui pourraient être "bloqués" ou oubliés.

## 🚨 Messages d'erreur

### `🎮 Aucun jeu de devinelenombre en cours.`
- Aucun jeu n'est actuellement actif sur le serveur
- Normal si personne n'a lancé de jeu

### `❌ Vous n'avez pas la permission`
- Tu n'as pas le rôle requis pour voir les jeux
- Demande au propriétaire du serveur

## 💡 Conseils d'utilisation

1. **Vérifie régulièrement** : Les jeux peuvent durer longtemps
2. **Note les nombres** : Si tu as le rôle, garde les nombres secrets
3. **Surveille le temps** : Les jeux s'auto-détruisent après 30 minutes
4. **Utilise les alias** : `+games` est plus court à taper

## 🔗 Commandes liées

- `+devinelenombre` - Lancer un nouveau jeu
- `+dice` - Lancer un dé
- `+coin` - Pile ou face
- `+rps` - Pierre-papier-ciseaux

---
**Parfait pour surveiller tous les jeux du serveur !** 🎯✨
