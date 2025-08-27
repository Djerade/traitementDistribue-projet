#!/bin/bash

# Script de démarrage simplifié pour l'architecture de traitement distribué
# Version fonctionnelle avec MongoDB + Streamlit

set -e

echo "🚀 Démarrage de l'architecture simplifiée"
echo "========================================"

# Vérifier que Docker et Docker Compose sont installés
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé. Veuillez installer Docker."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose n'est pas installé. Veuillez installer Docker Compose."
    exit 1
fi

# Créer le fichier .env si nécessaire
echo "📝 Configuration des variables d'environnement..."
if [ ! -f ".env" ]; then
    echo "⚠️  Fichier .env manquant. Création à partir de env.example..."
    cp env.example .env
    echo "✅ Fichier .env créé avec succès"
else
    echo "✅ Fichier .env déjà présent"
fi

# Arrêter les conteneurs existants s'ils existent
echo "🛑 Arrêt des conteneurs existants..."
docker-compose -f docker-compose.simple.yml down 2>/dev/null || true

# Démarrer les services
echo "🚀 Démarrage des services..."
docker-compose -f docker-compose.simple.yml up -d

# Attendre que les services soient prêts
echo "⏳ Attente du démarrage des services..."
sleep 30

# Vérifier l'état des services
echo "🔍 Vérification de l'état des services..."
docker-compose -f docker-compose.simple.yml ps

# Attendre que MongoDB soit prêt
echo "⏳ Attente que MongoDB soit prêt..."
sleep 15

# Tester la connexion MongoDB
echo "🧪 Test de la connexion MongoDB..."
docker run --rm --network bigdata_net -v $(pwd):/workspace python:3.11-slim bash -c "
cd /workspace &&
pip install pymongo pandas &&
python test-mongo.py
"

echo ""
echo "✅ Architecture simplifiée démarrée avec succès!"
echo ""
echo "📊 Interfaces web disponibles:"
echo "  - Application Streamlit: http://localhost:8501"
echo "  - MongoDB Express: http://localhost:8089"
echo ""
echo "🔧 Commandes utiles:"
echo "  - Voir les logs: docker-compose -f docker-compose.simple.yml logs -f [service]"
echo "  - Arrêter: docker-compose -f docker-compose.simple.yml down"
echo "  - Redémarrer: docker-compose -f docker-compose.simple.yml restart [service]"
echo ""
echo "🎯 Prochaines étapes:"
echo "  1. Ouvrir http://localhost:8501 pour accéder au dashboard"
echo "  2. Vérifier les données dans MongoDB Express: http://localhost:8089"
echo "  3. Consulter les logs pour le debugging"
echo ""
echo "📝 Note: Cette version simplifiée inclut:"
echo "   - MongoDB avec données d'exemple"
echo "   - Application Streamlit pour visualisation"
echo "   - Tests automatiques de connexion"
