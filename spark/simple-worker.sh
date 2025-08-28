#!/bin/bash

echo "🚀 Démarrage du Spark Worker Simple..."

# Configuration
MASTER_URL="spark://namenode:7077"
WORKER_MEMORY="1G"
WORKER_CORES="1"
HOSTNAME=$(hostname)

echo "📊 Configuration:"
echo "  - Master: $MASTER_URL"
echo "  - Memory: $WORKER_MEMORY"
echo "  - Cores: $WORKER_CORES"
echo "  - Hostname: $HOSTNAME"

# Attendre que le master soit prêt
echo "⏳ Attente du Spark Master..."
while ! nc -z namenode 7077; do
    echo "   Master non disponible, attente..."
    sleep 5
done
echo "✅ Spark Master disponible !"

# Démarrer le worker avec la commande directe
echo "⚡ Démarrage du Spark Worker..."
exec /opt/bitnami/spark/bin/spark-class org.apache.spark.deploy.worker.Worker \
    --webui-port 8081 \
    --host $HOSTNAME \
    --cores $WORKER_CORES \
    --memory $WORKER_MEMORY \
    $MASTER_URL
