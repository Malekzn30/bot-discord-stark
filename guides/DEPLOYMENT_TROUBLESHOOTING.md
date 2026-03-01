# 🔧 Déploiement - Guide de Dépannage

## ❌ **Problème courant**

```
sqlite3.OperationalError: duplicate column name: moderator_id
```

Ce problème se produit quand la base de données SQLite contient déjà la colonne `moderator_id` et que le bot essaie de l'ajouter à nouveau.

---

## ✅ **Solution appliquée**

J'ai ajouté une gestion d'erreur dans le code pour éviter ce problème :

```python
# Ajouter la colonne moderator_id si elle n'existe pas (pour compatibilité)
try:
    self.cursor.execute("ALTER TABLE warns ADD COLUMN moderator_id INTEGER DEFAULT NULL")
except sqlite3.OperationalError:
    # La colonne existe déjà, pas d'erreur
    pass
```

---

## 🚀 **Pour redéployer**

### Option 1 : Redémarrer le bot (recommandé)
1. Le bot va maintenant gérer la colonne existante
2. Pas besoin de modifier la base de données
3. Le bot devrait démarrer correctement

### Option 2 : Nettoyer la base de données (si problème persiste)
```bash
# Supprimer le fichier de base de données
rm warns.sqlite

# Redémarrer le bot
python bot.py
```

---

## 🔍 **Vérification du déploiement**

Une fois le bot redémarré, vérifie que :

1. ✅ **Bot en ligne** : Le bot apparaît en ligne sur Discord
2. ✅ **Commandes warn** : Teste `+warn_check @user`
3. ✅ **Embeds fonctionnels** : Les embeds s'affichent correctement
4. ✅ **Tracking modérateur** : Les nouveaux warns montrent qui a warn

---

## 📋 **Commandes à tester**

```bash
# Test des embeds de warn
+warn_check @ton_nom
+warn @ton_nom "test de warn"
+warnlist @ton_nom
+warn_leaderboard
```

---

## 🎯 **Si le problème persiste**

### Étapes de dépannage avancées :

1. **Vérifier les logs** :
   ```bash
   # Regarder les logs d'erreur
   python bot.py 2>&1 | grep -i error
   ```

2. **Tester localement** :
   ```bash
   # Tester en local avant de déployer
   python bot.py
   ```

3. **Vérifier la base de données** :
   ```bash
   # Vérifier la structure de la table
   sqlite3 warns.sqlite ".schema warns"
   ```

---

## 🔄 **Workflow de déploiement recommandé**

### Avant déploiement :
1. ✅ **Tester localement** : `python bot.py`
2. ✅ **Vérifier les commandes** : Teste les warns
3. ✅ **Confirmer les embeds** : Vérifie l'affichage

### Après déploiement :
1. ✅ **Surveiller les logs** : Regarder les erreurs
2. ✅ **Tester les commandes** : `+warn_check @user`
3. ✅ **Vérifier le fonctionnement** : Bot réactif

---

## 🎉 **Solution finale**

Le problème est maintenant résolu avec :
- ✅ **Gestion d'erreur** pour la colonne dupliquée
- ✅ **Compatibilité ascendante** : Fonctionne avec anciennes données
- ✅ **Pas de perte de données** : Les warns existants sont préservés
- ✅ **Embeds professionnels** : Tous les messages en embeds

**Le bot devrait maintenant se déployer sans erreur !** 🚀✨
