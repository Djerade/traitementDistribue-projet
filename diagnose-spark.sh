#!/bin/bash

echo "🔍 Diagnostic des Workers Spark"
echo "==============================="

echo ""
echo "1. Vérification des conteneurs existants..."
docker ps -a | grep spark

echo ""
echo "2. Vérification des images Spark..."
docker images | grep spark

echo ""
echo "3. Vérification du Spark Master..."
curl -s http://localhost:8085/json/ | grep -A 5 -B 5 "workers"

echo ""
echo "4. Nettoyage des conteneurs zombies..."
sudo docker kill $(sudo docker ps -q --filter "name=spark-worker") 2>/dev/null || echo "Aucun conteneur à tuer"
sudo docker rm -f $(sudo docker ps -aq --filter "name=spark-worker") 2>/dev/null || echo "Aucun conteneur à supprimer"

echo ""
echo "5. Vérification des ports utilisés..."
netstat -tuln | grep -E "(8091|8092|8093|8081)" || echo "Aucun port utilisé"

echo ""
echo "6. Test de connexion au Spark Master..."
docker exec app nc -z namenode 7077 && echo "✅ Connexion au master OK" || echo "❌ Connexion au master échouée"

echo ""
echo "✅ Diagnostic terminé"
