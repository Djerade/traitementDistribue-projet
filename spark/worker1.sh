#!/bin/bash

echo "🚀 Démarrage du Spark Worker 1..."
echo "=================================="

# Configuration spécifique au worker 1
WORKER_ID="worker1"
MASTER_URL="spark://namenode:7077"
WORKER_MEMORY="2G"
WORKER_CORES="2"
HOSTNAME="spark-worker-1"

echo "📊 Configuration Worker 1:"
echo "  - ID: $WORKER_ID"
echo "  - Master: $MASTER_URL"
echo "  - Memory: $WORKER_MEMORY"
echo "  - Cores: $WORKER_CORES"
echo "  - Hostname: $HOSTNAME"

# Attendre que le master soit prêt
echo "⏳ Attente du Spark Master..."
sleep 10
echo "✅ Tentative de connexion au Spark Master..."

# Démarrer le worker
echo "⚡ Démarrage du Spark Worker 1..."
exec /opt/bitnami/spark/bin/spark-class org.apache.spark.deploy.worker.Worker \
    --webui-port 8081 \
    --host $HOSTNAME \
    --cores $WORKER_CORES \
    --memory $WORKER_MEMORY \
    $MASTER_URL
