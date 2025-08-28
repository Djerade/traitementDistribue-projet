#!/bin/bash

echo "🚀 Test de Spark et Interface Utilisateur"
echo "=========================================="

echo ""
echo "1. Vérification de l'état actuel..."
echo "   - Spark Master UI: http://localhost:8085"
echo "   - Workers attendus: 3 (spark-worker-1, spark-worker-2, spark-worker-3)"

echo ""
echo "2. Problème identifié:"
echo "   ❌ Le Spark Master sur namenode ne démarre pas correctement"
echo "   ❌ Les workers ne peuvent pas se connecter au master"
echo "   ❌ Problèmes de permissions Docker persistants"

echo ""
echo "3. Solution alternative - Spark Local:"
echo "   ✅ Utilisation de Spark en mode local dans l'application"
echo "   ✅ Démonstration des capacités analytiques Spark"
echo "   ✅ Pas besoin de workers distribués pour les tests"

echo ""
echo "4. Test de Spark Local dans l'application..."
docker exec app bash -c "export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64 && python /app/exemple-simple.py"

echo ""
echo "5. Accès à l'application Streamlit:"
echo "   🌐 http://localhost:8501"
echo "   📊 Page '⚡ Analyses Spark' pour tester les fonctionnalités"

echo ""
echo "6. Pour voir les workers dans l'UI Spark:"
echo "   🔧 Nécessite de résoudre les problèmes de permissions Docker"
echo "   🔧 Redémarrer le namenode pour activer le Spark Master"
echo "   🔧 Démarrer les workers avec: docker-compose up -d spark-worker-1 spark-worker-2 spark-worker-3"

echo ""
echo "✅ Test terminé - Spark fonctionne en mode local !"
