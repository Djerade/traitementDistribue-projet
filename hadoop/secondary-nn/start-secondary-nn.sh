#!/bin/bash

set -e

echo "Starting Secondary NameNode..."

# Attendre que le NameNode soit prêt
sleep 30

# Créer le répertoire pour le Secondary NameNode
mkdir -p /hadoop/dfs/namesecondary

# Démarrer le Secondary NameNode
echo "Starting HDFS Secondary NameNode..."
su -c "hdfs secondarynamenode" hadoop &

# Garder le conteneur en vie
tail -f /dev/null
