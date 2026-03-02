#!/bin/bash

# ============= SCRIPT DE DÉMARRAGE POUR RENDER =============

echo "🚀 Démarrage du Bot Stark..."

# Variables d'environnement
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

# Vérifier les dépendances
echo "📦 Vérification des dépendances..."
pip install -r requirements.txt

# Lancer le bot
echo "🤖 Lancement du bot Discord..."
python bot.py
