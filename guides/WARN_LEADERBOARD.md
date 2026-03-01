# ⚠️ Commande +warn_leaderboard - Guide Complet

## 🎯 Description

La commande `+warn_leaderboard` affiche un classement des membres avec le plus d'avertissements sur le serveur.

## 📋 Syntaxe

```bash
+warn_leaderboard [nombre]
```

### Paramètres
- **nombre** (optionnel) : Nombre de membres à afficher dans le classement (défaut: 10, maximum: 50)

### Aliases
- `+warnlb` - Raccourci court
- `+warnrank` - Alternative

## 🔐 Permissions

- **Kick Members** requis : Seuls les membres avec la permission "Expulser des membres" peuvent utiliser cette commande

## 🎨 Fonctionnalités

### ✅ **Classement automatique**
- Affiche les membres avec le plus de warns
- Trié par ordre décroissant
- Limite configurable (défaut: 10)

### ✅ **Médailles visuelles**
- 🥇 **1er place** : Médaille d'or
- 🥈 **2ème place** : Médaille d'argent  
- 🥉 **3ème place** : Médaille de bronze
- 🔢 **Autres** : Numéro de position

### ✅ **Informations détaillées**
- Nom d'affichage du membre
- Nombre exact de warns
- Total des warns enregistrés
- Icône du serveur en thumbnail

### ✅ **Gestion des membres absents**
- Affiche "Utilisateur inconnu" si le membre a quitté le serveur
- Conserve les données historiques

## 📝 Exemples d'utilisation

### Exemple 1 : Afficher le top 10 (défaut)
```bash
+warn_leaderboard
```

### Exemple 2 : Afficher le top 5
```bash
+warn_leaderboard 5
```

### Exemple 3 : Afficher le top 20
```bash
+warn_leaderboard 20
```

### Exemple 4 : Avec l'alias court
```bash
+warnlb 15
```

## 🎨 Rendu visuel

L'embed affiché ressemblera à :

```
┌─────────────────────────────────────────┐
│ ⚠️ Classement des Avertissements     │
│ Top 5 membres avec le plus de warns   │
├─────────────────────────────────────────┤
│ 🥇 JeanDupont                        │
│ **15** avertissements                │
│                                     │
│ 🥈 MarieDurand                       │
│ **12** avertissements                │
│                                     │
│ 🥉 PaulMartin                       │
│ **8** avertissements                 │
│                                     │
│ #4 AliceBernard                     │
│ **5** avertissements                 │
│                                     │
│ #5 ThomasPetit                      │
│ **3** avertissements                 │
├─────────────────────────────────────────┤
│ Total: 43 warns enregistrés           │
└─────────────────────────────────────────┘
```

## 📊 Informations techniques

### 🗄️ **Base de données**
- Utilise la table `warns` SQLite
- Requête SQL optimisée avec `GROUP BY`
- Tri automatique par `ORDER BY DESC`

### ⚡ **Performance**
- Une seule requête SQL pour tout le classement
- Limite configurable pour éviter les surcharges
- Gestion efficace des membres absents

### 🔒 **Sécurité**
- Vérification des permissions avant exécution
- Protection contre les injections SQL
- Validation des paramètres

## 🔧 Cas d'usage

### 📊 **Monitoring de modération**
```bash
# Voir les membres les plus problématiques
+warn_leaderboard
```

### 📈 **Analyse des tendances**
```bash
# Suivre l'évolution sur 30 jours
+warn_leaderboard 20
```

### 🏆 **Motivation positive**
```bash
# Afficher le classement pour encourager l'amélioration
+warnlb 10
```

### 📋 **Rapports d'activité**
```bash
# Préparer un rapport pour l'équipe de modération
+warnrank 15
```

## ⚙️ Personnalisation

### 🎨 **Modifier la couleur**
Dans le code de la commande, modifiez :
```python
color=0xff6b6b  # Rouge par défaut
color=0xe74c3c  # Rouge vif
color=0xf39c12  # Orange
color=0x3498db  # Bleu
```

### 📊 **Changer la limite par défaut**
```python
limit: int = 10  # Modifier cette valeur
```

### 🏆 **Personnaliser les médailles**
```python
if i == 1:
    medal = "👑"  # Couronne
elif i == 2:
    medal = "🥈"   # Médaille d'argent
elif i == 3:
    medal = "🥉"   # Médaille de bronze
```

## 🔄 Intégration avec d'autres commandes

### 📝 **Commandes liées**
- `+warn @user "raison"` - Ajouter un avertissement
- `+warnlist @user` - Voir les warns d'un membre
- `+unwarn @user <index>` - Retirer un warn spécifique
- `+clearwarns @user` - Supprimer tous les warns d'un membre

### 📊 **Workflow de modération**
1. **Identifier** les membres problématiques avec `+warn_leaderboard`
2. **Analyser** les warns spécifiques avec `+warnlist @user`
3. **Agir** avec `+warn`, `+mute`, ou `+kick`
4. **Suivre** l'évolution avec `+warn_leaderboard`

## 🎯 Bonnes pratiques

### ✅ **Utilisation appropriée**
- Utiliser pour identifier les tendances de comportement
- Partager avec l'équipe de modération
- Suivre l'efficacité des mesures prises

### ❌ **À éviter**
- Ne pas utiliser pour humilier publiquement
- Éviter de partager dans des salons publics
- Ne pas se baser uniquement sur le nombre de warns

### 🔒 **Confidentialité**
- Les warns sont visibles uniquement par l'équipe de modération
- Les membres ne peuvent pas voir les warns des autres
- Respecter la vie privée des membres concernés

## 🚀 Évolutions possibles

### 📈 **Fonctionnalités futures**
- Graphique d'évolution des warns
- Filtrage par période (7 jours, 30 jours)
- Export en CSV/PDF
- Notifications automatiques pour les seuils

### 🎨 **Améliorations visuelles**
- Graphiques en barres
- Évolution temporelle
- Comparaison entre périodes
- Statistiques détaillées par membre

---

## 🎉 Conclusion

La commande `+warn_leaderboard` est un outil puissant pour :
- 📊 **Analyser** les tendances de comportement
- 🔍 **Identifier** les membres nécessitant une attention
- 📈 **Suivre** l'efficacité de la modération
- 🏆 **Motiver** l'amélioration du comportement

**Un outil essentiel pour une modération proactive et efficace !** ⚠️✨
