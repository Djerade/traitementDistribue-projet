#!/bin/bash

# Script de test pour valider l'architecture de traitement distribué

set -e

echo "🧪 Tests de validation de l'architecture"
echo "========================================"

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher les résultats
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

FAILED_TESTS=0

# Test 1: Vérifier que tous les services sont en cours d'exécution
echo "1. Vérification de l'état des services..."
SERVICES=("namenode" "secondary-nn" "datanode-1" "datanode-2" "datanode-3" "spark-thrift" "metastore" "mongodb" "mongo-express" "app")

for service in "${SERVICES[@]}"; do
    if docker-compose ps | grep -q "$service.*Up"; then
        print_result 0 "Service $service est en cours d'exécution"
    else
        print_result 1 "Service $service n'est pas en cours d'exécution"
    fi
done

# Test 2: Vérifier HDFS
echo -e "\n2. Test de HDFS..."
if docker exec namenode hdfs dfsadmin -report > /dev/null 2>&1; then
    print_result 0 "HDFS NameNode est accessible"
    
    # Vérifier les DataNodes
    DN_COUNT=$(docker exec namenode hdfs dfsadmin -report | grep "Live datanodes" | awk '{print $3}')
    if [ "$DN_COUNT" -eq 3 ]; then
        print_result 0 "3 DataNodes sont actifs"
    else
        print_result 1 "Seulement $DN_COUNT DataNodes sont actifs (attendu: 3)"
    fi
else
    print_result 1 "HDFS NameNode n'est pas accessible"
fi

# Test 3: Vérifier YARN
echo -e "\n3. Test de YARN..."
if docker exec namenode yarn node -list > /dev/null 2>&1; then
    print_result 0 "YARN ResourceManager est accessible"
    
    # Vérifier les NodeManagers
    NM_COUNT=$(docker exec namenode yarn node -list | grep "RUNNING" | wc -l)
    if [ "$NM_COUNT" -eq 3 ]; then
        print_result 0 "3 NodeManagers sont actifs"
    else
        print_result 1 "Seulement $NM_COUNT NodeManagers sont actifs (attendu: 3)"
    fi
else
    print_result 1 "YARN ResourceManager n'est pas accessible"
fi

# Test 4: Vérifier Spark
echo -e "\n4. Test de Spark..."
if docker exec namenode curl -s http://localhost:8080 > /dev/null 2>&1; then
    print_result 0 "Spark Master est accessible"
    
    # Vérifier les Workers
    WORKER_COUNT=$(docker exec namenode curl -s http://localhost:8080 | grep -o "Workers" | wc -l)
    if [ "$WORKER_COUNT" -gt 0 ]; then
        print_result 0 "Spark Workers sont connectés"
    else
        print_result 1 "Aucun Spark Worker n'est connecté"
    fi
else
    print_result 1 "Spark Master n'est pas accessible"
fi

# Test 5: Vérifier MongoDB
echo -e "\n5. Test de MongoDB..."
if docker exec mongodb mongo --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
    print_result 0 "MongoDB est accessible"
    
    # Vérifier les données
    DOC_COUNT=$(docker exec mongodb mongo retail --eval "db.sales.count()" --quiet)
    if [ "$DOC_COUNT" -gt 0 ]; then
        print_result 0 "Collection sales contient $DOC_COUNT documents"
    else
        print_result 1 "Collection sales est vide"
    fi
else
    print_result 1 "MongoDB n'est pas accessible"
fi

# Test 6: Vérifier Spark Thrift Server
echo -e "\n6. Test de Spark Thrift Server..."
sleep 10  # Attendre que le service soit prêt
if docker exec spark-thrift netstat -tlnp | grep -q ":10000"; then
    print_result 0 "Spark Thrift Server écoute sur le port 10000"
else
    print_result 1 "Spark Thrift Server n'écoute pas sur le port 10000"
fi

# Test 7: Vérifier l'application Streamlit
echo -e "\n7. Test de l'application Streamlit..."
sleep 10  # Attendre que l'application soit prête
if docker exec app netstat -tlnp | grep -q ":8501"; then
    print_result 0 "Application Streamlit écoute sur le port 8501"
else
    print_result 1 "Application Streamlit n'écoute pas sur le port 8501"
fi

# Test 8: Vérifier les données HDFS
echo -e "\n8. Test des données HDFS..."
if docker exec namenode hdfs dfs -test -d /data/raw/sales 2>/dev/null; then
    print_result 0 "Répertoire /data/raw/sales existe dans HDFS"
    
    # Vérifier les fichiers Parquet
    FILE_COUNT=$(docker exec namenode hdfs dfs -ls /data/raw/sales | grep -c "parquet")
    if [ "$FILE_COUNT" -gt 0 ]; then
        print_result 0 "Fichiers Parquet trouvés dans /data/raw/sales"
    else
        print_result 1 "Aucun fichier Parquet trouvé dans /data/raw/sales"
    fi
else
    print_result 1 "Répertoire /data/raw/sales n'existe pas dans HDFS"
fi

# Test 9: Vérifier les tables Hive
echo -e "\n9. Test des tables Hive..."
if docker exec spark-thrift beeline -u jdbc:hive2://localhost:10000 -e "SHOW TABLES;" 2>/dev/null | grep -q "raw_sales"; then
    print_result 0 "Table raw_sales existe dans Hive"
    
    # Vérifier le contenu de la table
    ROW_COUNT=$(docker exec spark-thrift beeline -u jdbc:hive2://localhost:10000 -e "SELECT COUNT(*) FROM raw_sales;" 2>/dev/null | grep -v "INFO" | tail -1)
    if [ "$ROW_COUNT" -gt 0 ]; then
        print_result 0 "Table raw_sales contient $ROW_COUNT lignes"
    else
        print_result 1 "Table raw_sales est vide"
    fi
else
    print_result 1 "Table raw_sales n'existe pas dans Hive"
fi

# Test 10: Test de performance simple
echo -e "\n10. Test de performance..."
start_time=$(date +%s)
docker exec spark-thrift beeline -u jdbc:hive2://localhost:10000 -e "SELECT category, COUNT(*) FROM raw_sales GROUP BY category;" > /dev/null 2>&1
end_time=$(date +%s)
duration=$((end_time - start_time))

if [ "$duration" -lt 30 ]; then
    print_result 0 "Requête SQL exécutée en ${duration}s (acceptable)"
else
    print_result 1 "Requête SQL trop lente: ${duration}s"
fi

# Résumé des tests
echo -e "\n📊 Résumé des tests"
echo "=================="

if [ "$FAILED_TESTS" -eq 0 ]; then
    echo -e "${GREEN}🎉 Tous les tests sont passés avec succès!${NC}"
    echo -e "${GREEN}L'architecture est opérationnelle et prête à être utilisée.${NC}"
else
    echo -e "${RED}⚠️  $FAILED_TESTS test(s) ont échoué.${NC}"
    echo -e "${YELLOW}Vérifiez les logs des services et relancez les tests.${NC}"
fi

echo -e "\n🔗 Interfaces disponibles:"
echo "  - Dashboard: http://localhost:8501"
echo "  - HDFS NameNode: http://localhost:9870"
echo "  - YARN ResourceManager: http://localhost:8088"
echo "  - Spark Master: http://localhost:8080"
echo "  - MongoDB Express: http://localhost:8089"

echo -e "\n📝 Commandes utiles:"
echo "  - Logs: docker-compose logs -f [service]"
echo "  - Redémarrer: docker-compose restart [service]"
echo "  - Arrêter: docker-compose down"

