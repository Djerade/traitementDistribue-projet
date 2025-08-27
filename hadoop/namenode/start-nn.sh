#!/bin/bash

set -e

echo "Starting NameNode..."

# Attendre que les services soient prêts
sleep 10

# Formater le NameNode si nécessaire
if [ ! -f /hadoop/dfs/name/current/VERSION ]; then
    echo "Formatting NameNode..."
    su -c "hdfs namenode -format" hadoop
fi

# Démarrer le NameNode
echo "Starting HDFS NameNode..."
su -c "hdfs namenode" hadoop &

# Attendre que le NameNode soit prêt
sleep 15

# Démarrer le ResourceManager
echo "Starting YARN ResourceManager..."
su -c "yarn resourcemanager" hadoop &

# Démarrer le Spark Master
echo "Starting Spark Master..."
su -c "spark-class org.apache.spark.deploy.master.Master --host 0.0.0.0 --port 7077 --webui-port 8080" spark &

# Démarrer le JobHistory Server
echo "Starting JobHistory Server..."
su -c "mapred jobhistoryserver" hadoop &

# Créer les répertoires HDFS nécessaires
echo "Creating HDFS directories..."
su -c "hdfs dfs -mkdir -p /data/raw /data/staging /data/curated /user/hive/warehouse /tmp" hadoop || true
su -c "hdfs dfs -chmod -R 777 /data /user/hive/warehouse /tmp" hadoop || true

# Garder le conteneur en vie
tail -f /dev/null
