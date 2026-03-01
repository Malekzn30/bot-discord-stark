# 📂 Dossier DATA

Ce dossier contient toutes les données du bot :

## 📄 Fichiers de configuration

### 🎫 Tickets
- **`tickets_config.json`** - Configuration principale des tickets
  - Catégories, messages, rôles, etc.
  - Sauvegardé automatiquement

- **`tickets_data.json`** - Données actives des tickets
  - Tickets ouverts, propriétaires, threads
  - Mis à jour en temps réel

- **`tickets_panels.json`** - Configuration des panels
  - Panels de tickets créés
  - Messages et interactions

## ⚠️ Important

- **Ne modifiez pas manuellement** ces fichiers pendant que le bot tourne
- **Sauvegardez régulièrement** ce dossier
- **Vérifiez les permissions** : le bot doit pouvoir lire/écrire ici

## 🔧 Maintenance

```bash
# Sauvegarder les données
cp -r data/ backup_data_$(date +%Y%m%d)/

# Vérifier l'intégrité
python -c "import json; print('JSON valides')" data/*.json
```

---
*Ce dossier est crucial pour le fonctionnement du bot*
