# ⚠️ Commandes Warn - Guide des Embeds

## 🎨 **Nouveaux Embeds pour les Commandes de Warn**

Toutes les commandes de warn utilisent maintenant des embeds professionnels avec tracking des modérateurs.

---

## 📋 **Commandes Modifiées**

### ⚠️ **+warn @membre "raison"**

#### **Embed de succès :**
```
┌─────────────────────────────────────────┐
│ ⚠️ Avertissement émis                │
│ 📅 01/01/2024 12:00:00          │
├─────────────────────────────────────────┤
│ 👤 Membre averti                     │
│ @JeanDupont                            │
│                                     │
│ 📄 Raison                             │
│ Spam dans le salon général               │
│                                     │
│ 👮 Modérateur                         │
│ @AdminBot                             │
│                                     │
│ 📊 Total de warns                    │
│ **3** avertissements                  │
├─────────────────────────────────────────┤
│ Warn émis par AdminBot 🤖             │
└─────────────────────────────────────────┘
```

#### **Embeds d'erreur :**
- **Membre non mentionné** : "❌ Veuillez mentionner un membre."
- **Auto-warn** : "❌ Vous ne pouvez pas vous warn vous-même."

---

### 📋 **+warnlist @membre**

#### **Embed avec warns :**
```
┌─────────────────────────────────────────┐
│ ⚠️ Liste des avertissements - JeanDupont │
│ 📅 01/01/2024 12:00:00          │
├─────────────────────────────────────────┤
│ Warn #1                             │
│ 📄 **Raison** : Spam général          │
│ 👮 **Par** : AdminBot                 │
│                                     │
│ Warn #2                             │
│ 📄 **Raison** : Langage inapproprié    │
│ 👮 **Par** : ModeratorPro             │
│                                     │
│ Warn #3                             │
│ 📄 **Raison** : Pub non autorisée     │
│ 👮 **Par** : StaffBot                │
├─────────────────────────────────────────┤
│ Total : 3 avertissements              │
└─────────────────────────────────────────┘
```

#### **Embed sans warns :**
```
┌─────────────────────────────────────────┐
│ ✅ Aucun avertissement               │
│ @NouveauMembre n'a aucun avertissement │
│ enregistré.                           │
└─────────────────────────────────────────┘
```

---

### 🧹 **+unwarn @membre <index>**

#### **Embed de succès :**
```
┌─────────────────────────────────────────┐
│ 🧹 Avertissement retiré               │
│ 📅 01/01/2024 12:00:00          │
├─────────────────────────────────────────┤
│ 👤 Membre                             │
│ @JeanDupont                            │
│                                     │
│ 📄 Raison du warn retiré             │
│ Spam dans le salon général               │
│                                     │
│ 👮 Retiré par                        │
│ @AdminBot                             │
├─────────────────────────────────────────┤
│ Retiré par AdminBot 🤖               │
└─────────────────────────────────────────┘
```

---

### 🧼 **+clearwarns @membre**

#### **Embed de succès :**
```
┌─────────────────────────────────────────┐
│ 🧼 Tous les warns supprimés           │
│ 📅 01/01/2024 12:00:00          │
├─────────────────────────────────────────┤
│ 👤 Membre                             │
│ @JeanDupont                            │
│                                     │
│ 📊 Nombre supprimé                   │
│ **5** avertissements                  │
│                                     │
│ 👮 Supprimé par                       │
│ @AdminBot                             │
├─────────────────────────────────────────┤
│ Supprimé par AdminBot 🤖               │
└─────────────────────────────────────────┘
```

---

### 🔍 **+warn_check @membre**

#### **Embed avec warns :**
```
┌─────────────────────────────────────────┐
│ ⚠️ Vérification des avertissements    │
│ 📅 01/01/2024 12:00:00          │
├─────────────────────────────────────────┤
│ 👤 Membre vérifié                    │
│ @JeanDupont                            │
│                                     │
│ 📊 Nombre de warns                   │
│ **3** avertissements                  │
│                                     │
│ 📈 Statut                            │
│ ⚠️ Membre averti                    │
├─────────────────────────────────────────┤
│ Vérifié par AdminBot 🤖               │
└─────────────────────────────────────────┘
```

#### **Embed sans warns :**
```
┌─────────────────────────────────────────┐
│ ✅ Vérification des avertissements    │
│ 📅 01/01/2024 12:00:00          │
├─────────────────────────────────────────┤
│ 👤 Membre vérifié                    │
│ @NouveauMembre                        │
│                                     │
│ 📊 Nombre de warns                   │
│ **0** avertissement                   │
│                                     │
│ 📈 Statut                            │
│ ✅ Membre clean                      │
├─────────────────────────────────────────┤
│ Vérifié par AdminBot 🤖               │
└─────────────────────────────────────────┘
```

---

## 🎨 **Caractéristiques des Embeds**

### ✅ **Informations systématiques**
- **Timestamp** : Date et heure de l'action
- **Avatar** : Photo du membre concerné
- **Footer** : Nom et avatar du modérateur
- **Couleur** : Rouge pour les erreurs, vert pour les succès

### ✅ **Tracking des modérateurs**
- **Qui a warn** : Affiché dans tous les embeds
- **Qui a retiré** : Visible dans les actions de suppression
- **Qui a vérifié** : Indiqué dans les vérifications

### ✅ **Design cohérent**
- **Mêmes icônes** : 🤖 👤 👮 📄 📊 📈
- **Mêmes couleurs** : Rouge (0xff6b6b) / Vert (0x2ecc71)
- **Mêmes structures** : Fields organisés logiquement

---

## 🗄️ **Base de Données Améliorée**

### 📊 **Nouvelle structure**
```sql
CREATE TABLE warns (
    user_id INTEGER,        -- ID du membre averti
    reason TEXT,           -- Raison du warn
    moderator_id INTEGER    -- ID du modérateur (NOUVEAU)
);
```

### 🔄 **Compatibilité**
- **Migration automatique** : Ajout de la colonne `moderator_id`
- **Anciens warns** : `moderator_id` sera `NULL` (compatibilité)
- **Nouveaux warns** : `moderator_id` enregistré automatiquement

---

## 🎯 **Avantages des Nouveaux Embeds**

### ✅ **Transparence**
- **Qui a fait l'action** : Toujours visible
- **Quand l'action** : Timestamp précis
- **Pourquoi** : Raison détaillée

### ✅ **Professionnalisme**
- **Design unifié** : Tous les embeds ont le même style
- **Informations riches** : Plus de détails qu'avant
- **Faciles à lire** : Structure claire et organisée

### ✅ **Traçabilité**
- **Historique complet** : Chaque warn est tracé
- **Responsabilité** : Chaque modérateur est identifié
- **Audit trail** : Parfait pour la modération

---

## 🔧 **Personnalisation**

### 🎨 **Modifier les couleurs**
```python
# Rouge pour les erreurs
color=0xff6b6b

# Vert pour les succès  
color=0x2ecc71

# Orange pour les avertissements
color=0xf39c12

# Bleu pour les informations
color=0x3498db
```

### 🖼️ **Modifier les icônes**
```python
# Icônes possibles
👤 # Membre
👮 # Modérateur  
📄 # Raison
📊 # Statistiques
📈 # État
⚠️ # Avertissement
✅ # Succès
❌ # Erreur
🧹 # Suppression
🧼 # Nettoyage
```

---

## 🚀 **Utilisation Recommandée**

### 📋 **Workflow de modération**
1. **Vérifier** : `+warn_check @membre`
2. **Lister** : `+warnlist @membre` 
3. **Agir** : `+warn @membre "raison"`
4. **Suivre** : `+warn_leaderboard`

### 📊 **Monitoring**
- **Classement** : `+warn_leaderboard` pour les tendances
- **Vérification** : `+warn_check` pour un quick check
- **Historique** : `+warnlist` pour les détails

---

## 🎉 **Conclusion**

Les commandes de warn sont maintenant :
- ✅ **100% en embeds** : Plus un seul message texte
- ✅ **Tracking complet** : Qui a fait quoi et quand
- ✅ **Design professionnel** : Cohérent et informatif
- ✅ **Base de données améliorée** : Support des modérateurs
- ✅ **Transparence totale** : Toutes les actions tracées

**Un système de modération moderne et professionnel !** ⚠️✨
