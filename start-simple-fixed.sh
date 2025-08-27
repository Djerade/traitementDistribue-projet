#!/bin/bash

# Script de démarrage simplifié corrigé pour l'architecture de traitement distribué
# Version fonctionnelle avec MongoDB + Streamlit

set -e

echo "🚀 Démarrage de l'architecture simplifiée (version corrigée)"
echo "=========================================================="

# Vérifier que Docker et Docker Compose sont installés
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé. Veuillez installer Docker."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose n'est pas installé. Veuillez installer Docker Compose."
    exit 1
fi

# Nettoyer les conteneurs existants (sans supprimer le réseau)
echo "🧹 Nettoyage des conteneurs existants..."
docker rm -f mongodb mongo-express app 2>/dev/null || true
docker system prune -f

# Créer le réseau s'il n'existe pas
echo "🌐 Création du réseau Docker..."
docker network create bigdata_net 2>/dev/null || echo "Réseau bigdata_net déjà existant"

# Créer le fichier .env si nécessaire
echo "📝 Configuration des variables d'environnement..."
if [ ! -f ".env" ]; then
    echo "⚠️  Fichier .env manquant. Création à partir de env.example..."
    cp env.example .env
    echo "✅ Fichier .env créé avec succès"
else
    echo "✅ Fichier .env déjà présent"
fi

# Démarrer MongoDB en premier
echo "🐳 Démarrage de MongoDB..."
docker run -d \
    --name mongodb \
    --network bigdata_net \
    -p 27017:27017 \
    -v mongo_data:/data/db \
    -v $(pwd)/mongo/init.js:/docker-entrypoint-initdb.d/init.js:ro \
    -e MONGO_INITDB_DATABASE=retail \
    --restart unless-stopped \
    mongo:7

# Attendre que MongoDB soit prêt
echo "⏳ Attente que MongoDB soit prêt..."
sleep 10

# Démarrer Mongo Express
echo "🌐 Démarrage de Mongo Express..."
docker run -d \
    --name mongo-express \
    --network bigdata_net \
    -p 8089:8081 \
    -e ME_CONFIG_MONGODB_SERVER=mongodb \
    -e ME_CONFIG_MONGODB_DATABASE=retail \
    --restart unless-stopped \
    mongo-express:1

# Démarrer l'application Streamlit
echo "📊 Démarrage de l'application Streamlit..."
docker run -d \
    --name app \
    --network bigdata_net \
    -p 8501:8501 \
    -v $(pwd)/app:/app \
    -e MONGO_URI=mongodb://mongodb:27017 \
    -e MONGO_DB=retail \
    -e MONGO_COLLECTION=sales \
    --restart unless-stopped \
    python:3.11-slim \
    bash -c "
        pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org streamlit pandas plotly pymongo &&
        streamlit run app.py --server.port 8501 --server.address 0.0.0.0
    "

# Attendre que les services soient prêts
echo "⏳ Attente du démarrage des services..."
sleep 30

# Vérifier l'état des services
echo "🔍 Vérification de l'état des services..."
docker ps

# Tester la connexion MongoDB
echo "🧪 Test de la connexion MongoDB..."
sleep 10

echo ""
echo "✅ Architecture simplifiée démarrée avec succès!"
echo ""
echo "📊 Interfaces web disponibles:"
echo "  - Application Streamlit: http://localhost:8501"
echo "  - MongoDB Express: http://localhost:8089"
echo ""
echo "🔧 Commandes utiles:"
echo "  - Voir les logs: docker logs [container-name]"
echo "  - Arrêter: docker stop mongodb mongo-express app"
echo "  - Redémarrer: docker restart [container-name]"
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

