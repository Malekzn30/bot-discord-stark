# 🔧 Guide de dépannage - Commandes vocales

## ❌ Problèmes courants et solutions

### 🚨 "Les commandes ne fonctionnent pas à moitié"

#### **Problème 1 : Permissions du bot**
Le bot n'a pas les permissions nécessaires pour déplacer les membres.

**✅ Solution :**
1. Va dans **Paramètres du serveur > Rôles**
2. Sélectionne le rôle du bot
3. Active la permission **"Déplacer les membres"**
4. Vérifie aussi **"Voir les salons vocaux"** et **"Se connecter"**

#### **Problème 2 : Rate limiting de Discord**
Discord limite le nombre de déplacements par seconde.

**✅ Solution :**
- Le bot ajoute maintenant des délais automatiques (0.3s entre chaque déplacement)
- Pour les grands groupes, attends la fin du processus

#### **Problème 3 : Membres qui quittent le vocal**
Un membre quitte le vocal pendant le déplacement.

**✅ Solution :**
- Le bot vérifie maintenant si le membre est toujours en vocal
- Les membres qui partent sont comptés comme "échecs" mais ne bloquent plus la commande

## 🎯 Commandes corrigées

### ✅ `+moove @user #salon`
- **Nouveau** : Vérification des permissions
- **Nouveau** : Messages d'erreur détaillés
- **Nouveau** : Gestion des exceptions

### ✅ `+mooveusers @u1 @u2 #salon`
- **Nouveau** : Progression en temps réel
- **Nouveau** : Compte-rendu des succès/échecs
- **Nouveau** : Délais anti-rate limiting

### ✅ `+mooveall #salon`
- **Nouveau** : Message de progression
- **Nouveau** : Vérification des permissions
- **Nouveau** : Gestion des erreurs individuelles

### ✅ `+server #salon` (alias de `+mooveserver`)
- **Nouveau** : Délais plus longs (0.5s)
- **Nouveau** : Vérification des membres en vocal
- **Nouveau** : Rapport détaillé

## 🔍 Comment débugger

### 1. **Vérifier les permissions**
```bash
# Test simple
+moove @toi-même #autre-salon
```

Si ça échoue avec "Permissions", c'est un problème de permissions du bot.

### 2. **Vérifier la console**
Le bot affiche maintenant les erreurs dans la console :
```
❌ Erreur déplacement NomUser: HTTPException: 400 Bad Request
```

### 3. **Tester avec un petit groupe**
```bash
# Test avec 2-3 personnes maximum
+mooveusers @user1 @user2 #salon
```

## 📋 Messages d'erreur expliqués

### `❌ Permissions`
Le bot ne peut pas déplacer les membres dans ce salon.
→ **Solution** : Donne la permission "Déplacer les membres" au bot.

### `❌ Utilisation`
Syntaxe incorrecte de la commande.
→ **Solution** : Vérifie la syntaxe dans le guide.

### `❌ Erreur: Ce membre n'est pas en vocal`
Le membre ciblé n'est pas dans un salon vocal.
→ **Solution** : Vérifie que le membre est bien en vocal.

## 🎮 Conseils d'utilisation

### ✅ Bonnes pratiques
1. **Vérifie les permissions** du bot avant les grandes opérations
2. **Utilise des petits groupes** d'abord pour tester
3. **Attends la fin** du processus avant de lancer une autre commande
4. **Surveille la console** pour voir les erreurs détaillées

### ❌ À éviter
1. Lancer plusieurs commandes en même temps
2. Déplacer des bots (ils peuvent résister)
3. Utiliser sur des serveurs très actifs sans délais

## 🆘 Si ça ne marche toujours pas

1. **Redémarre le bot** : `+restart` (si disponible)
2. **Vérifie le rôle** : Assure-toi d'avoir le rôle autorisé (ID: 1469665367881420841)
3. **Contacte le support** : Fournit les messages d'erreur exacts

---
**Les commandes sont maintenant beaucoup plus fiables !** 🚀
