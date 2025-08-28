#!/bin/bash

echo "🔍 Vérification des Workers Spark"
echo "================================="

echo ""
echo "1. État des conteneurs workers..."
docker ps | grep spark-worker

echo ""
echo "2. Logs de connexion des workers..."
echo "=== Worker 1 ==="
docker logs spark-worker-1 --tail 2 | grep "Successfully registered"
echo "=== Worker 2 ==="
docker logs spark-worker-2 --tail 2 | grep "Successfully registered"
echo "=== Worker 3 ==="
docker logs spark-worker-3 --tail 2 | grep "Successfully registered"

echo ""
echo "3. Test de connectivité directe..."
docker exec spark-worker-1 bash -c "timeout 3 bash -c '</dev/tcp/namenode/7077' && echo '✅ Worker 1 -> Master OK' || echo '❌ Worker 1 -> Master FAILED'"
docker exec spark-worker-2 bash -c "timeout 3 bash -c '</dev/tcp/namenode/7077' && echo '✅ Worker 2 -> Master OK' || echo '❌ Worker 2 -> Master FAILED'"
docker exec spark-worker-3 bash -c "timeout 3 bash -c '</dev/tcp/namenode/7077' && echo '✅ Worker 3 -> Master OK' || echo '❌ Worker 3 -> Master FAILED'"

echo ""
echo "4. État du Spark Master..."
curl -s http://localhost:8085/ | grep -i "alive workers"

echo ""
echo "5. Test d'une application Spark simple..."
docker exec app bash -c "
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64 && 
python -c \"
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName('TestWorkers').config('spark.master', 'spark://namenode:7077').getOrCreate()
print('✅ Spark Session créée avec succès')
print('Master URL:', spark.conf.get('spark.master'))
spark.stop()
print('✅ Test terminé')
\"
"

echo ""
echo "6. URLs d'accès:"
echo "   - Spark Master UI: http://localhost:8085"
echo "   - Worker 1 UI: http://localhost:8091"
echo "   - Worker 2 UI: http://localhost:8092"
echo "   - Worker 3 UI: http://localhost:8093"

echo ""
echo "✅ Vérification terminée !"
