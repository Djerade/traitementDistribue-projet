#!/bin/bash

set -e

echo "Starting DataNode..."

# Attendre que le NameNode soit prêt
sleep 45

# Démarrer le DataNode
echo "Starting HDFS DataNode..."
su -c "hdfs datanode" hadoop &

# Attendre que le ResourceManager soit prêt
sleep 15

# Démarrer le NodeManager
echo "Starting YARN NodeManager..."
su -c "yarn nodemanager" hadoop &

# Démarrer le Spark Worker
echo "Starting Spark Worker..."
su -c "spark-class org.apache.spark.deploy.worker.Worker --webui-port 8081 spark://namenode:7077" spark &

# Garder le conteneur en vie
tail -f /dev/null
