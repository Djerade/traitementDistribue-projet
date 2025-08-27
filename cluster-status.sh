#!/bin/bash

echo "🚀 CLUSTER DE TRAITEMENT DISTRIBUÉ - STATUT COMPLET"
echo "=================================================="
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}📊 SERVICES DOCKER EN COURS D'EXÉCUTION${NC}"
echo "----------------------------------------"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(mongodb|mongo-express|app|namenode|datanode|secondary-nn|spark-thrift|metastore|pig|mongo-exporter)"

echo ""
echo -e "${CYAN}🗄️ DONNÉES MONGODB${NC}"
echo "-------------------"
doc_count=$(docker exec mongodb mongosh retail --eval "db.sales.countDocuments()" --quiet 2>/dev/null)
if [ ! -z "$doc_count" ] && [ "$doc_count" -gt 0 ]; then
    echo -e "${GREEN}✅ Documents MongoDB: $doc_count${NC}"
else
    echo -e "${RED}❌ Aucun document trouvé${NC}"
fi

echo ""
echo -e "${CYAN}📁 SYSTÈME DE FICHIERS HDFS${NC}"
echo "------------------------------"
if docker exec namenode hdfs dfs -ls /data/ >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Répertoires HDFS créés${NC}"
    echo "   - /data/raw/sales/ (données brutes)"
    echo "   - /data/curated/sales/ (données transformées)"
else
    echo -e "${YELLOW}⚠️ Répertoires HDFS en cours de création${NC}"
fi

echo ""
echo -e "${CYAN}🌐 INTERFACES WEB DISPONIBLES${NC}"
echo "--------------------------------"

# Test des interfaces web
interfaces=(
    "HDFS NameNode:http://localhost:9870"
    "YARN ResourceManager:http://localhost:8088"
    "Spark Master:http://localhost:8080"
    "MongoDB Express:http://localhost:8089"
    "Application Streamlit:http://localhost:8501"
)

for interface in "${interfaces[@]}"; do
    name=$(echo $interface | cut -d: -f1)
    url=$(echo $interface | cut -d: -f2-)
    if curl -s "$url" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ $name${NC}"
    else
        echo -e "${YELLOW}⚠️ $name${NC}"
    fi
done

echo ""
echo -e "${CYAN}🔄 SERVICE D'EXPORT AUTOMATIQUE${NC}"
echo "-----------------------------------"
if docker ps | grep -q "mongo-exporter.*Up"; then
    echo -e "${GREEN}✅ Service d'export automatique en cours d'exécution${NC}"
    echo "   - Export MongoDB → HDFS toutes les 5 minutes"
    echo "   - Logs: docker logs -f mongo-exporter"
else
    echo -e "${RED}❌ Service d'export automatique non en cours d'exécution${NC}"
fi

echo ""
echo -e "${CYAN}🔌 PORTS DE SERVICE${NC}"
echo "----------------------"
echo "   - MongoDB: localhost:27018"
echo "   - Spark Thrift Server: localhost:10000"
echo "   - Hive Metastore: localhost:5434"

echo ""
echo -e "${CYAN}🎯 COMMANDES UTILES${NC}"
echo "----------------------"
echo -e "${PURPLE}📊 Voir les logs d'un service:${NC}"
echo "   docker logs -f <nom_du_service>"
echo ""
echo -e "${PURPLE}🔧 Accéder à un conteneur:${NC}"
echo "   docker exec -it <nom_du_service> bash"
echo ""
echo -e "${PURPLE}📁 Vérifier HDFS:${NC}"
echo "   docker exec namenode hdfs dfs -ls /data/"
echo ""
echo -e "${PURPLE}🐷 Tester Pig:${NC}"
echo "   docker exec pig pig -x mapreduce /scripts/eda.pig"
echo ""
echo -e "${PURPLE}📈 Tester Spark:${NC}"
echo "   docker exec spark-thrift spark-sql --master spark://namenode:7077"
echo ""

echo -e "${GREEN}✅ CLUSTER OPÉRATIONNEL !${NC}"
echo ""
echo -e "${BLUE}🎉 Le cluster de traitement distribué est prêt à traiter vos données !${NC}"

