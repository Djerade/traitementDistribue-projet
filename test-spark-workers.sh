#!/bin/bash

echo "🚀 Test des Workers Spark"
echo "========================="

# Vérifier l'état du cluster Spark
echo "1. Vérification du Spark Master..."
if curl -s http://localhost:8085 > /dev/null; then
    echo "✅ Spark Master accessible"
    WORKERS=$(curl -s http://localhost:8085/json/ | grep -o '"workers" : \[[^]]*\]' | grep -o '\[.*\]')
    if [ "$WORKERS" = "[]" ]; then
        echo "⚠️  Aucun worker connecté"
    else
        echo "✅ Workers connectés: $WORKERS"
    fi
else
    echo "❌ Spark Master non accessible"
fi

echo ""
echo "2. Test du traitement distribué..."
echo "   Exécution de l'exemple de travail Spark..."

# Exécuter l'exemple de travail
docker exec spark-processor python /app/exemple-travail-complet.py

echo ""
echo "3. Vérification des résultats sur HDFS..."
echo "   Les résultats sont sauvegardés dans:"
echo "   - hdfs://namenode:9000/spark-results/ventes-par-categorie"
echo "   - hdfs://namenode:9000/spark-results/top-produits"
echo "   - hdfs://namenode:9000/spark-results/utilisateurs-actifs"
echo "   - hdfs://namenode:9000/spark-results/tendances-temporelles"

echo ""
echo "4. Accès aux interfaces web:"
echo "   - Spark Master UI: http://localhost:8085"
echo "   - HDFS NameNode: http://localhost:9870"
echo "   - Application Streamlit: http://localhost:8501"

echo ""
echo "✅ Test terminé !"
