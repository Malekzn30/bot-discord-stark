# 🎫 GUIDE D'UTILISATION DU SYSTÈME DE TICKETS

## 📋 Configuration par le propriétaire

### 1. Configuration de base
```bash
+ticket setup category #tickets        # Définir la catégorie Discord
+ticket setup logs #ticket-logs         # Définir le salon de logs
+ticket setup addmanager @Staff         # Ajouter les rôles gestionnaires
```

### 2. Personnaliser les messages
```bash
+ticket setup message pre "🎫 Bienvenue ! Choisissez une catégorie pour votre ticket."
+ticket setup message open "✅ Votre ticket a été créé ! Notre staff vous aidera rapidement."
```

### 3. Gérer les catégories (le plus important !)
```bash
+ticket setup categories                # Menu interactif pour gérer les catégories
```

Dans le menu interactif, le propriétaire peut :
- ➕ **Ajouter une catégorie** : Ex: "Support Technique", "Questions Générales", "Signalements"
- 🗑️ **Supprimer une catégorie**
- ❓ **Gérer les questions** de chaque catégorie

### 4. Créer le panel de tickets (très important !)
```bash
+ticket setup panel_add #tickets "🎫 Création de Ticket"
```

Cette commande crée un **embed permanent** avec des boutons pour chaque catégorie configurée !

### 5. Exemple de configuration complète

#### Catégorie : Support Technique
- **Nom** : Support Technique
- **Emoji** : 🛠️
- **Description** : Problèmes techniques, bugs, aide
- **Questions** :
  - "Décrivez votre problème en détail"
  - "Quelle est votre version du logiciel ?"

#### Catégorie : Questions Générales  
- **Nom** : Questions Générales
- **Emoji** : 💬
- **Description** : Questions, suggestions, autre
- **Questions** :
  - "Quel est le sujet de votre demande ?"

## 👟 Utilisation par les membres

### ⚠️ IMPORTANT : Les membres n'utilisent PAS `+ticket` !

Les membres **cliquent directement sur les boutons** dans le panel créé par le propriétaire :

1. 🎫 **Vont dans le salon du panel** (ex: #tickets)
2. 👀 **Voient l'embed avec les boutons** des catégories
3. �️ **Cliquent sur un bouton** (ex: 🛠️ Support Technique)
4. ❓ **Remplissent le questionnaire** (modal) si la catégorie en a
5. 💬 **Reçoivent leur ticket** où ils peuvent parler

## 🎯 Processus complet

### Pour le propriétaire :
```bash
# 1. Configurer les catégories
+ticket setup categories
# → Ajoute "Support" et "Questions" avec leurs questions

# 2. Créer le panel
+ticket setup panel_add #tickets "🎫 Support"
# → Crée un embed permanent avec boutons 🛠️ et 💬
```

### Pour les membres :
```bash
# PAS DE COMMANDE ! Juste cliquer sur les boutons !

# 1. Aller dans #tickets
# 2. Voir l'embed avec les boutons
# 3. Cliquer sur 🛠️ Support Technique
# 4. Remplir le questionnaire
# 5. Parler dans son ticket personnel
```

## � Avantages du nouveau système

✅ **Ultra simple pour les membres** : Juste cliquer sur un bouton !
✅ **Pas de commandes à retenir** : Interface visuelle intuitive
✅ **Panels permanents** : L'embed reste toujours disponible
✅ **Personnalisable** : Chaque catégorie a ses questions/messages
✅ **Organisé** : Tickets classés par catégorie avec emoji
✅ **Professionnel** : Système moderne comme les grands serveurs

## 📝 Résumé

- **Propriétaire** : Configure avec `+ticket setup` puis crée un panel avec `+ticket setup panel_add`
- **Membres** : Juste cliquent sur les boutons dans le panel, plus besoin de `+ticket`

Le système est maintenant **exactement** comme les serveurs Discord professionnels ! 🚀
