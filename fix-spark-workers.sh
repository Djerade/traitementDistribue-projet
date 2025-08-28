#!/bin/bash

echo "🔧 Correction des Workers Spark"
echo "==============================="

echo ""
echo "1. Arrêt de tous les services..."
docker-compose down

echo ""
echo "2. Nettoyage des conteneurs zombies..."
sudo docker system prune -f
sudo docker volume prune -f

echo ""
echo "3. Redémarrage de Docker..."
sudo systemctl restart docker
sleep 5

echo ""
echo "4. Démarrage du namenode..."
docker-compose up -d namenode

echo ""
echo "5. Attente du démarrage du namenode..."
sleep 30

echo ""
echo "6. Vérification du Spark Master..."
docker exec namenode ps aux | grep spark || echo "❌ Spark Master non trouvé"

echo ""
echo "7. Démarrage des workers..."
docker-compose up -d spark-worker-1 spark-worker-2 spark-worker-3

echo ""
echo "8. Attente de la connexion des workers..."
sleep 20

echo ""
echo "9. Vérification de l'état du cluster..."
curl -s http://localhost:8085/json/ | grep -A 10 "workers"

echo ""
echo "10. Test de connexion au master..."
docker exec app nc -z namenode 7077 && echo "✅ Connexion OK" || echo "❌ Connexion échouée"

echo ""
echo "🎯 Résultats:"
echo "   - Spark Master UI: http://localhost:8085"
echo "   - Workers UI: http://localhost:8091, 8092, 8093"
echo "   - Application: http://localhost:8501"

echo ""
echo "✅ Correction terminée !"
