#!/bin/bash

# Configuration pour les workers Spark
echo "🔧 Configuration du worker Spark..."

# Variables d'environnement Spark
export SPARK_HOME=/opt/bitnami/spark
export SPARK_MASTER_URL=${SPARK_MASTER_URL:-spark://namenode:7077}
export SPARK_WORKER_MEMORY=${SPARK_WORKER_MEMORY:-1G}
export SPARK_WORKER_CORES=${SPARK_WORKER_CORES:-1}

echo "📊 Configuration:"
echo "  - Master URL: $SPARK_MASTER_URL"
echo "  - Worker Memory: $SPARK_WORKER_MEMORY"
echo "  - Worker Cores: $SPARK_WORKER_CORES"

# Démarrer le worker Spark
echo "🚀 Démarrage du worker Spark..."
$SPARK_HOME/sbin/start-slave.sh $SPARK_MASTER_URL

# Garder le conteneur en vie
tail -f /dev/null
