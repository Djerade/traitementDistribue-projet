#!/bin/bash

echo "🚀 Test de l'architecture Spark"
echo "================================"

# Vérifier le statut des services Spark
echo "📊 Vérification des services Spark..."
docker ps | grep -E "(namenode|datanode|spark)"

echo ""
echo "🔍 Test de connexion Spark Master..."
curl -s http://localhost:8085 | grep -i "spark" || echo "❌ Spark Master UI non accessible"

echo ""
echo "⚡ Test du processeur Spark..."
docker exec spark-processor python spark-processor.py

echo ""
echo "📈 Test de l'application Streamlit avec Spark..."
curl -s http://localhost:8501 | grep -i "streamlit" || echo "❌ Streamlit non accessible"

echo ""
echo "✅ Tests terminés !"
