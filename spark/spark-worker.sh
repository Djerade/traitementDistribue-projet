#!/bin/bash

echo "🚀 Démarrage du Spark Worker..."

# Variables d'environnement
export SPARK_HOME=/opt/bitnami/spark
export SPARK_MASTER_URL=${SPARK_MASTER_URL:-spark://namenode:7077}
export SPARK_WORKER_MEMORY=${SPARK_WORKER_MEMORY:-1G}
export SPARK_WORKER_CORES=${SPARK_WORKER_CORES:-1}

echo "📊 Configuration:"
echo "  - Master URL: $SPARK_MASTER_URL"
echo "  - Worker Memory: $SPARK_WORKER_MEMORY"
echo "  - Worker Cores: $SPARK_WORKER_CORES"
echo "  - Hostname: $(hostname)"

# Attendre que le master soit prêt
echo "⏳ Attente du Spark Master..."
until nc -z namenode 7077; do
    echo "   Master non disponible, attente..."
    sleep 5
done
echo "✅ Spark Master disponible !"

# Démarrer le worker
echo "⚡ Démarrage du Spark Worker..."
$SPARK_HOME/sbin/start-slave.sh \
    --host $(hostname) \
    --port 8081 \
    --webui-port 8081 \
    --cores $SPARK_WORKER_CORES \
    --memory $SPARK_WORKER_MEMORY \
    $SPARK_MASTER_URL

echo "🎉 Spark Worker démarré !"
tail -f /dev/null
