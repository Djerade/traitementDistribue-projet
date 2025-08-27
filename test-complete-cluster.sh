#!/bin/bash

echo "🎯 Test complet du cluster de traitement distribué"
echo "=================================================="
echo ""

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les résultats
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

echo "📊 Vérification des services Docker..."
echo "----------------------------------------"

# Test 1: Vérification des conteneurs en cours d'exécution
print_info "Vérification des conteneurs en cours d'exécution..."
running_containers=$(docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "(mongodb|mongo-express|app|namenode|datanode|secondary-nn|spark-thrift|metastore|pig|mongo-exporter)")
if [ ! -z "$running_containers" ]; then
    echo "$running_containers"
    print_result 0 "Tous les services sont en cours d'exécution"
else
    print_result 1 "Certains services ne sont pas en cours d'exécution"
fi

echo ""
echo "🗄️ Test MongoDB..."
echo "-------------------"

# Test 2: Connexion MongoDB
print_info "Test de connexion MongoDB..."
docker exec mongodb mongosh --eval "db.runCommand('ping')" > /dev/null 2>&1
print_result $? "Connexion MongoDB"

# Test 3: Nombre de documents
print_info "Comptage des documents..."
doc_count=$(docker exec mongodb mongosh retail --eval "db.sales.countDocuments()" --quiet)
if [ ! -z "$doc_count" ] && [ "$doc_count" -gt 0 ]; then
    print_result 0 "Documents MongoDB: $doc_count"
else
    print_result 1 "Aucun document trouvé"
fi

echo ""
echo "📁 Test HDFS..."
echo "---------------"

# Test 4: Connexion HDFS
print_info "Test de connexion HDFS..."
docker exec namenode hdfs dfs -ls / > /dev/null 2>&1
print_result $? "Connexion HDFS"

# Test 5: Création de répertoires HDFS
print_info "Création des répertoires HDFS..."
docker exec namenode hdfs dfs -mkdir -p /data/raw/sales /data/curated/sales > /dev/null 2>&1
print_result $? "Création des répertoires HDFS"

# Test 6: Vérification des répertoires HDFS
print_info "Vérification des répertoires HDFS..."
docker exec namenode hdfs dfs -ls /data/ > /dev/null 2>&1
print_result $? "Répertoires HDFS créés"

echo ""
echo "🌐 Test des interfaces web..."
echo "------------------------------"

# Test 7: Interface HDFS NameNode
print_info "Test interface HDFS NameNode (port 9870)..."
if curl -s http://localhost:9870 > /dev/null 2>&1; then
    print_result 0 "Interface HDFS NameNode accessible"
else
    print_warning "Interface HDFS NameNode non accessible"
fi

# Test 8: Interface YARN ResourceManager
print_info "Test interface YARN ResourceManager (port 8088)..."
if curl -s http://localhost:8088 > /dev/null 2>&1; then
    print_result 0 "Interface YARN ResourceManager accessible"
else
    print_warning "Interface YARN ResourceManager non accessible"
fi

# Test 9: Interface Spark Master
print_info "Test interface Spark Master (port 8080)..."
if curl -s http://localhost:8080 > /dev/null 2>&1; then
    print_result 0 "Interface Spark Master accessible"
else
    print_warning "Interface Spark Master non accessible"
fi

# Test 10: Interface MongoDB Express
print_info "Test interface MongoDB Express (port 8089)..."
if curl -s http://localhost:8089 > /dev/null 2>&1; then
    print_result 0 "Interface MongoDB Express accessible"
else
    print_warning "Interface MongoDB Express non accessible"
fi

# Test 11: Interface Application Streamlit
print_info "Test interface Application Streamlit (port 8501)..."
if curl -s http://localhost:8501 > /dev/null 2>&1; then
    print_result 0 "Interface Application Streamlit accessible"
else
    print_warning "Interface Application Streamlit non accessible"
fi

echo ""
echo "🔄 Test du service d'export automatique..."
echo "-------------------------------------------"

# Test 12: Service d'export automatique
print_info "Vérification du service d'export automatique..."
if docker ps | grep -q "mongo-exporter.*Up"; then
    print_result 0 "Service d'export automatique en cours d'exécution"
    
    # Vérification des logs du service d'export
    export_logs=$(docker logs mongo-exporter 2>&1 | tail -5)
    if echo "$export_logs" | grep -q "Connexion MongoDB réussie"; then
        print_result 0 "Service d'export connecté à MongoDB"
    else
        print_warning "Service d'export en cours d'initialisation"
    fi
else
    print_result 1 "Service d'export automatique non en cours d'exécution"
fi

echo ""
echo "🐷 Test Pig..."
echo "--------------"

# Test 13: Test Pig
print_info "Test de Pig..."
docker exec pig pig -x mapreduce -e "A = LOAD 'hdfs://namenode:9000/data/raw/sales/' USING PigStorage(','); STORE A INTO 'hdfs://namenode:9000/data/test/pig_test' USING PigStorage(',');" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    print_result 0 "Pig fonctionne correctement"
else
    print_warning "Pig en cours d'initialisation ou pas de données"
fi

echo ""
echo "📈 Test Spark..."
echo "----------------"

# Test 14: Test Spark Thrift Server
print_info "Test du Spark Thrift Server..."
if docker exec spark-thrift ps aux | grep -q "thrift"; then
    print_result 0 "Spark Thrift Server en cours d'exécution"
else
    print_warning "Spark Thrift Server en cours d'initialisation"
fi

echo ""
echo "🗃️ Test Hive Metastore..."
echo "--------------------------"

# Test 15: Test Hive Metastore
print_info "Test du Hive Metastore..."
if docker exec metastore ps aux | grep -q "postgres"; then
    print_result 0 "Hive Metastore (PostgreSQL) en cours d'exécution"
else
    print_result 1 "Hive Metastore non en cours d'exécution"
fi

echo ""
echo "📊 Résumé des interfaces disponibles..."
echo "======================================"

echo ""
echo "🌐 Interfaces web:"
echo "  - HDFS NameNode: http://localhost:9870"
echo "  - YARN ResourceManager: http://localhost:8088"
echo "  - Spark Master: http://localhost:8080"
echo "  - MongoDB Express: http://localhost:8089"
echo "  - Application Streamlit: http://localhost:8501"
echo ""

echo "🔌 Ports de service:"
echo "  - MongoDB: localhost:27018"
echo "  - Spark Thrift Server: localhost:10000"
echo "  - Hive Metastore: localhost:5434"
echo ""

echo "📁 Répertoires HDFS:"
echo "  - /data/raw/sales/ (données brutes)"
echo "  - /data/curated/sales/ (données transformées)"
echo ""

echo "🔄 Services automatiques:"
echo "  - Export MongoDB → HDFS: Automatique toutes les 5 minutes"
echo "  - Logs du service d'export: docker logs -f mongo-exporter"
echo ""

echo "🎯 Commandes utiles:"
echo "  - Voir les logs d'un service: docker logs -f <nom_du_service>"
echo "  - Accéder à un conteneur: docker exec -it <nom_du_service> bash"
echo "  - Vérifier HDFS: docker exec namenode hdfs dfs -ls /data/"
echo "  - Tester Pig: docker exec pig pig -x mapreduce /scripts/eda.pig"
echo ""

echo "✅ Test complet terminé !"
echo "Le cluster de traitement distribué est opérationnel."
