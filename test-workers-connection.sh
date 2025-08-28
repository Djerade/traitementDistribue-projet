#!/bin/bash

echo "🔍 Test de Connexion des Workers Spark"
echo "======================================"

echo ""
echo "1. Vérification du Spark Master..."
docker exec namenode ps aux | grep spark | grep -v grep

echo ""
echo "2. Test de connectivité au port 7077..."
docker exec spark-worker-1 bash -c "timeout 5 bash -c '</dev/tcp/namenode/7077' && echo '✅ Connexion OK' || echo '❌ Connexion échouée'"

echo ""
echo "3. État actuel du cluster..."
curl -s http://localhost:8085/ | grep -i "alive workers"

echo ""
echo "4. Démarrage des autres workers..."

# Modifier les scripts worker2 et worker3 pour ne pas utiliser nc
sed -i 's/while ! nc -z namenode 7077; do/sleep 10; echo "✅ Tentative de connexion..."; #/' spark/worker2.sh
sed -i 's/while ! nc -z namenode 7077; do/sleep 10; echo "✅ Tentative de connexion..."; #/' spark/worker3.sh

# Démarrer worker 2
docker run -d --name spark-worker-2 --hostname spark-worker-2 --network bigdata_net -p 8092:8081 -v $(pwd)/spark/worker2.sh:/worker2.sh bitnami/spark:3.5.1 /worker2.sh

# Démarrer worker 3
docker run -d --name spark-worker-3 --hostname spark-worker-3 --network bigdata_net -p 8093:8081 -v $(pwd)/spark/worker3.sh:/worker3.sh bitnami/spark:3.5.1 /worker3.sh

echo ""
echo "5. Attente de la connexion des workers..."
sleep 20

echo ""
echo "6. État final du cluster..."
curl -s http://localhost:8085/ | grep -i "alive workers"

echo ""
echo "7. Liste des conteneurs workers..."
docker ps | grep spark-worker

echo ""
echo "✅ Test terminé !"
