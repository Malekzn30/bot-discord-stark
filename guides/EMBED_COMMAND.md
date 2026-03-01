# 📝 Commande +embed - Guide Complet

## 🎯 Description

La commande `+embed` permet de créer des embeds Discord personnalisés avec l'icône du serveur et le footer du bot.

## 📋 Syntaxe

```bash
+embed "Titre" "Description" "Footer optionnel"
```

### Paramètres
- **Titre** (obligatoire) : Titre de l'embed
- **Description** (obligatoire) : Contenu principal de l'embed
- **Footer** (optionnel) : Texte personnalisé dans le footer

## 🔐 Permissions

- **Administrateur requis** : Seuls les membres avec la permission "Administrateur" peuvent utiliser cette commande

## 🎨 Fonctionnalités automatiques

### ✅ **Icône du serveur**
- Ajoute automatiquement l'icône du serveur comme thumbnail
- Si le serveur n'a pas d'icône, l'embed s'affiche sans thumbnail

### ✅ **Footer du bot**
- Ajoute automatiquement le nom du bot dans le footer
- Inclut l'avatar du bot comme icône du footer
- Si un footer personnalisé est fourni, il est ajouté avant le nom du bot

### ✅ **Auteur du message**
- Ajoute automatiquement le nom de l'auteur comme author
- Inclut l'avatar de l'auteur comme icône de l'author

### ✅ **Timestamp**
- Ajoute automatiquement la date et heure de création

## 📝 Exemples d'utilisation

### Exemple 1 : Embed simple
```bash
+embed "Règles du serveur" "1. Respectez les autres\n2. Pas de spam\n3. Soyez gentil"
```

### Exemple 2 : Embed avec footer personnalisé
```bash
+embed "Nouveau membre" "Bienvenue sur notre serveur ! N'oublie pas de lire les règles." "Staff"
```

### Exemple 3 : Annonce importante
```bash
+embed "Maintenance" "Le serveur sera en maintenance demain de 14h à 16h." "Administration"
```

## 🎨 Rendu visuel

L'embed créé ressemblera à :

```
┌─────────────────────────────────────┐
│ 👤 Nom de l'auteur                  │
├─────────────────────────────────────┤
│ 📄 Titre de l'embed                 │
│                                     │
│ Description du message              │
│                                     │
│                                     │
├─────────────────────────────────────┤
│ Footer personnalisé • Nom du bot 🤖 │
│ [Timestamp: 01/01/2024 12:00]      │
└─────────────────────────────────────┘
```

## 📋 Caractéristiques techniques

### 🎨 **Couleur**
- Couleur par défaut : `0x3498db` (bleu)
- Modifiable dans `config.py` avec `BOT_COLOR`

### 🖼️ **Images**
- **Thumbnail** : Icône du serveur (automatique)
- **Footer icon** : Avatar du bot (automatique)
- **Author icon** : Avatar de l'auteur (automatique)

### 📝 **Formatage**
- Supporte le Markdown dans la description
- Supporte les emojis dans tous les champs
- Supporte les mentions Discord

## 🔧 Conseils d'utilisation

### ✅ **Bonnes pratiques**
1. **Utilise des guillemets** pour les titres et descriptions avec espaces
2. **Sois concis** dans les titres (limite Discord)
3. **Utilise le footer** pour indiquer qui a envoyé le message
4. **Teste avant** d'envoyer des messages importants

### ❌ **À éviter**
1. **Titres trop longs** (limite Discord)
2. **Descriptions excessivement longues**
3. **Caractères spéciaux** qui pourraient causer des erreurs
4. **Mentions excessives** dans les embeds

## 🚀 Cas d'usage

### 📢 **Annonces serveur**
```bash
+embed "🎉 Événement ce week-end !" "Rejoignez-nous pour un tournoi gaming samedi à 20h !" "Équipe d'organisation"
```

### 📋 **Règles et informations**
```bash
+embed "📚 Règles du salon vocal" "1. Pas de musique forte\n2. Respectez les autres\n3. Pas de spam vocal" "Modération"
```

### 🎮 **Informations jeux**
```bash
+embed "🎮 Serveur Minecraft" "IP: play.example.com\nVersion: 1.20.1\nMode: Survie" "Staff Minecraft"
```

## ⚙️ Personnalisation avancée

### 🎨 **Changer la couleur par défaut**
Dans `config.py` :
```python
BOT_COLOR = 0xe74c3c  # Rouge
BOT_COLOR = 0x2ecc71  # Vert
BOT_COLOR = 0x9b59b6  # Violet
```

### 🔐 **Modifier les permissions**
Si tu veux utiliser un rôle spécifique au lieu de "Administrateur" :
```python
# Dans cogs/system.py, remplace :
@commands.has_permissions(administrator=True)
# Par :
@commands.has_role(AUTHORIZED_ROLE_ID)
```

---

## 🎉 Résultat

La commande `+embed` te permet de créer rapidement des messages professionnels et esthétiques pour ton serveur Discord, avec une apparence cohérente et automatique !

**Parfait pour les annonces, règles, et messages importants !** 📝✨
