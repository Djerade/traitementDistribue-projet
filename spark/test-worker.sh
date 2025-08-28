#!/bin/bash

echo "🔍 Test de diagnostic du Worker Spark"
echo "======================================"

# Vérifier la connectivité réseau
echo "1. Test de connectivité vers le master..."
if nc -z namenode 7077; then
    echo "✅ Connexion au master réussie"
else
    echo "❌ Impossible de se connecter au master"
    echo "   Vérification des ports..."
    netstat -tuln | grep 7077 || echo "   Port 7077 non trouvé"
fi

# Vérifier les variables d'environnement
echo ""
echo "2. Variables d'environnement:"
echo "   HOSTNAME: $(hostname)"
echo "   SPARK_HOME: ${SPARK_HOME:-Non défini}"
echo "   JAVA_HOME: ${JAVA_HOME:-Non défini}"

# Vérifier les fichiers Spark
echo ""
echo "3. Vérification des fichiers Spark:"
if [ -d "/opt/bitnami/spark" ]; then
    echo "✅ Répertoire Spark trouvé"
    ls -la /opt/bitnami/spark/bin/spark-class
else
    echo "❌ Répertoire Spark non trouvé"
fi

# Test de démarrage simple
echo ""
echo "4. Test de démarrage du worker..."
echo "   Commande: /opt/bitnami/spark/bin/spark-class org.apache.spark.deploy.worker.Worker --help"

# Afficher les logs du namenode pour voir s'il y a des erreurs
echo ""
echo "5. Vérification des logs du namenode..."
docker logs namenode --tail 5 2>/dev/null || echo "   Impossible d'accéder aux logs"

echo ""
echo "🔍 Diagnostic terminé"
