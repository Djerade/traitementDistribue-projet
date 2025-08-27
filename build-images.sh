#!/bin/bash

# Script pour construire toutes les images Docker nécessaires
# Architecture de traitement distribué

set -e

echo "🔨 Construction des images Docker"
echo "================================="

# Vérifier que Docker est installé
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé. Veuillez installer Docker."
    exit 1
fi

# Construire l'image de base Hadoop/Spark
echo "🏗️  Construction de l'image de base Hadoop/Spark..."
docker build -t hadoop-base:latest ./hadoop/base/

# Construire l'image NameNode
echo "🏗️  Construction de l'image NameNode..."
docker build -t namenode:latest ./hadoop/namenode/

# Construire l'image Secondary NameNode
echo "🏗️  Construction de l'image Secondary NameNode..."
docker build -t secondary-nn:latest ./hadoop/secondary-nn/

# Construire l'image DataNode
echo "🏗️  Construction de l'image DataNode..."
docker build -t datanode:latest ./hadoop/datanode/

# Construire l'image Spark Thrift Server
echo "🏗️  Construction de l'image Spark Thrift Server..."
docker build -t spark-thrift:latest ./spark/thrift/

# Construire l'image Hive Metastore
echo "🏗️  Construction de l'image Hive Metastore..."
docker build -t metastore:latest ./hive/metastore/

# Construire l'image Pig
echo "🏗️  Construction de l'image Pig..."
docker build -t pig:latest ./pig/

echo ""
echo "✅ Toutes les images ont été construites avec succès!"
echo ""
echo "📋 Images construites:"
echo "  - hadoop-base:latest"
echo "  - namenode:latest"
echo "  - secondary-nn:latest"
echo "  - datanode:latest"
echo "  - spark-thrift:latest"
echo "  - metastore:latest"
echo "  - pig:latest"
echo ""
echo "🚀 Vous pouvez maintenant démarrer l'architecture complète avec:"
echo "  docker-compose up -d"

