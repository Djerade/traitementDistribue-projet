#!/bin/bash

set -e

echo "Starting Spark Thrift Server..."

# Attendre que le Spark Master soit prêt
sleep 60

# Démarrer le Spark Thrift Server
echo "Starting Spark Thrift Server..."
su -c "spark-class org.apache.spark.sql.hive.thriftserver.HiveThriftServer2 --master spark://namenode:7077 --conf spark.sql.warehouse.dir=hdfs://namenode:9000/user/hive/warehouse" spark &

# Garder le conteneur en vie
tail -f /dev/null
