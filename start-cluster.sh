#!/bin/bash

# Script de démarrage pour l'architecture de traitement distribué
# Hadoop + Spark + Pig + MongoDB + Streamlit

set -e

echo "🚀 Démarrage de l'architecture de traitement distribué"
echo "=================================================="

# Vérifier que Docker et Docker Compose sont installés
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé. Veuillez installer Docker."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose n'est pas installé. Veuillez installer Docker Compose."
    exit 1
fi

# Créer le fichier .env à partir de env.example si il n'existe pas
echo "📝 Configuration des variables d'environnement..."
if [ ! -f ".env" ]; then
    echo "⚠️  Fichier .env manquant. Création à partir de env.example..."
    cp env.example .env
    echo "✅ Fichier .env créé avec succès"
else
    echo "✅ Fichier .env déjà présent"
fi

# Vérifier que les connecteurs sont présents
echo "📦 Vérification des connecteurs..."
if [ ! -f "connectors/mongo-spark-connector_2.12-10.1.1.jar" ]; then
    echo "⚠️  Connecteur MongoDB Spark manquant. Téléchargement..."
    mkdir -p connectors
    cd connectors
    wget -q https://search.maven.org/remotecontent?filepath=org/mongodb/spark/mongo-spark-connector_2.12/10.1.1/mongo-spark-connector_2.12-10.1.1.jar -O mongo-spark-connector_2.12-10.1.1.jar
    cd ..
fi



# Construire les images Docker
echo "🔨 Construction des images Docker..."
docker-compose build

# Démarrer les services
echo "🚀 Démarrage des services..."
docker-compose up -d

# Attendre que les services soient prêts
echo "⏳ Attente du démarrage des services..."
sleep 30

# Vérifier l'état des services
echo "🔍 Vérification de l'état des services..."
docker-compose ps

# Attendre que HDFS soit prêt
echo "⏳ Attente que HDFS soit prêt..."
sleep 60

# Vérifier HDFS
echo "🔍 Vérification de HDFS..."
docker exec namenode hdfs dfsadmin -report | head -20

# Vérifier que le service d'export automatique est démarré
echo "📥 Vérification du service d'export automatique MongoDB vers HDFS..."
sleep 30

if docker ps | grep -q "mongo-exporter.*Up"; then
    echo "✅ Service d'export automatique démarré avec succès"
    echo "🔄 Les données MongoDB seront exportées automatiquement vers HDFS toutes les 5 minutes"
else
    echo "⚠️  Service d'export automatique non détecté, démarrage manuel..."
    docker-compose up -d mongo-exporter
    sleep 30
fi

# Lancer le script Pig EDA (optionnel - peut être lancé manuellement)
echo "🐷 Lancement de l'analyse Pig (optionnel)..."
docker exec pig pig -x mapreduce /scripts/eda.pig || echo "⚠️  Analyse Pig non disponible pour le moment"

echo ""
echo "✅ Architecture démarrée avec succès!"
echo ""
echo "📊 Interfaces web disponibles:"
echo "  - HDFS NameNode: http://localhost:9870"
echo "  - YARN ResourceManager: http://localhost:8088"
echo "  - Spark Master: http://localhost:8080"
echo "  - Spark Worker 1: http://localhost:8081"
echo "  - Spark Worker 2: http://localhost:8082"
echo "  - Spark Worker 3: http://localhost:8083"
echo "  - MongoDB Express: http://localhost:8089"
echo "  - Application Streamlit: http://localhost:8501"
echo ""
echo "🔄 Services automatiques:"
echo "  - Export MongoDB → HDFS: Automatique toutes les 5 minutes"
echo "  - Logs du service d'export: docker logs -f mongo-exporter"
echo ""
echo "🔧 Commandes utiles:"
echo "  - Voir les logs: docker-compose logs -f [service]"
echo "  - Arrêter: docker-compose down"
echo "  - Redémarrer: docker-compose restart [service]"
echo ""
echo "🎯 Prochaines étapes:"
echo "  1. Ouvrir http://localhost:8501 pour accéder au dashboard"
echo "  2. Vérifier les données dans MongoDB Express: http://localhost:8089"
echo "  3. Consulter les interfaces de monitoring Hadoop/Spark"
