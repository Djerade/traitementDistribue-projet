# Architecture Technique – Traitement Distribué (Docker)

> **Cible** : Cluster Hadoop/Spark (1 master, 1 secondary-master, 3 slaves) + Pig pour EDA + lecture MongoDB→Hadoop + application dynamique + workflow et livrables.

## 🏗️ Vue d'ensemble

Cette architecture implémente un système de traitement distribué complet avec les composants suivants :

```
                   ┌──────────────────────────────┐
                   │        Poste Dev/Client      │
                   │  (navigateur + VSCode)       │
                   └──────────────┬───────────────┘
                                  │
                                  ▼
                     Docker Network: bigdata_net (bridge)
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                     Cluster Hadoop + Spark + Pig + MongoDB + App                        │
│                                                                                         │
│  ┌──────────────┐   ┌────────────────┐     ┌────────────────┐     ┌────────────────┐   │
│  │ namenode     │   │ secondary-nn   │     │ datanode-1     │     │ datanode-2     │   │
│  │ + resourcemgr│   │ + journalnode  │     │ + nodemanager   │     │ + nodemanager   │   │
│  │ + spark-master │ │                │     │ + spark-worker  │     │ + spark-worker  │   │
│  └──────┬───────┘   └────────┬───────┘     └────────┬───────┘     └────────┬───────┘   │
│         │                    │                      │                      │           │
│         └─────── HDFS HA (JournalNodes/ZKFC) ───────┴───────────────┬───────┘           │
│                                                                     │                   │
│                                        ┌─────────────────────────────▼──────────────┐   │
│                                        │ datanode-3 + nodemanager + spark-worker    │   │
│                                        └────────────────────────────────────────────┘   │
│
│  ┌──────────────────────┐     ┌─────────────────────┐     ┌──────────────────────────┐  │
│  │ Pig (client)         │<--->│ Spark Thrift Server │<--->│ Hive Metastore (option)  │  │
│  │ (mapreduce mode)     │     │ (JDBC/SQL)          │     │ + Derby/Postgres         │  │
│  └──────────────────────┘     └─────────────────────┘     └──────────────────────────┘  │
│
│  ┌───────────────────────────────┐
│  │ MongoDB (replica set 1-node)  │  ← volumes
│  │ + mongo-express (option)      │
│  └───────────────────────────────┘
│
│  ┌───────────────────────────────┐
│  │ App dynamique (Streamlit/Flask│ → lit via Spark Thrift JDBC ou WebHDFS / parquet
│  │  + API)                        │ → écrit résultats vers HDFS/MinIO(option)
│  └───────────────────────────────┘
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## 🚀 Démarrage rapide

### Prérequis
- Docker et Docker Compose installés
- Au moins 8 Go de RAM disponible
- 20 Go d'espace disque libre

### Installation et démarrage

1. **Cloner le projet**
```bash
git clone <repository-url>
cd traitementDistribue-projet
```

2. **Lancer l'architecture complète**
```bash
chmod +x start-cluster.sh
./start-cluster.sh
```

3. **Accéder aux interfaces**
- **Dashboard principal** : http://localhost:8501
- **HDFS NameNode** : http://localhost:9870
- **YARN ResourceManager** : http://localhost:8088
- **Spark Master** : http://localhost:8080
- **MongoDB Express** : http://localhost:8089

## 📁 Structure du projet

```
/bigdata-project
├── docker-compose.yml          # Orchestration des services
├── start-cluster.sh            # Script de démarrage automatique
├── env.example                 # Variables d'environnement
├── hadoop/
│   ├── base/Dockerfile         # Image de base Hadoop/Spark
│   ├── namenode/               # NameNode + ResourceManager + Spark Master
│   ├── datanode/               # DataNode + NodeManager + Spark Worker
│   ├── secondary-nn/           # Secondary NameNode
│   └── *.xml                   # Configurations Hadoop
├── spark/
│   ├── thrift/Dockerfile       # Spark Thrift Server
│   └── scripts/                # Scripts Spark (ingestion MongoDB→HDFS)
├── pig/
│   ├── Dockerfile              # Client Pig
│   └── scripts/                # Scripts Pig EDA
├── hive/
│   ├── metastore/Dockerfile    # Hive Metastore (PostgreSQL)
│   └── hive-site.xml           # Configuration Hive
├── mongo/
│   └── init.js                 # Données d'exemple MongoDB
├── app/
│   ├── Dockerfile              # Application Streamlit
│   ├── requirements.txt        # Dépendances Python
│   └── app.py                  # Dashboard principal
└── connectors/                 # Connecteurs JAR
```

## 🔧 Services déployés

| Service | Port | Description |
|---------|------|-------------|
| **namenode** | 9870, 8088, 7077, 8080 | HDFS NameNode + YARN ResourceManager + Spark Master |
| **secondary-nn** | 9868 | Secondary NameNode |
| **datanode-1/2/3** | 9864, 8042, 8081+ | HDFS DataNode + YARN NodeManager + Spark Worker |
| **spark-thrift** | 10000 | Spark Thrift Server (JDBC/SQL) |
| **metastore** | 5432 | Hive Metastore (PostgreSQL) |
| **mongodb** | 27017 | Base de données source |
| **mongo-express** | 8089 | Interface web MongoDB |
| **app** | 8501 | Dashboard Streamlit |

## 📊 Flux de données

### 1. **Ingestion** (MongoDB → HDFS)
```python
# Script: spark/scripts/mongo_to_hdfs.py
spark.read.format("mongodb").load()  # Lecture MongoDB
  .write.parquet("hdfs:///data/raw/")  # Écriture HDFS Parquet
```

### 2. **EDA avec Pig**
```pig
-- Script: pig/scripts/eda.pig
raw = LOAD 'hdfs:///data/raw/sales/' USING PigStorage(',');
by_category = GROUP raw BY category;
stats = FOREACH by_category GENERATE group, COUNT(raw), SUM(raw.total_amount);
STORE stats INTO 'hdfs:///data/curated/category_stats';
```

### 3. **Visualisation** (Streamlit)
```python
# App: app/app.py
# Connexion JDBC: jdbc:hive2://spark-thrift:10000/default
# Connexion MongoDB: mongodb://mongodb:27017
```

## 🛠️ Commandes utiles

### Monitoring
```bash
# Voir l'état des services
docker-compose ps

# Logs en temps réel
docker-compose logs -f namenode
docker-compose logs -f spark-thrift

# Vérifier HDFS
docker exec namenode hdfs dfsadmin -report
```

### Exécution de jobs
```bash
# Lancer un job Spark
docker exec spark-thrift spark-submit /opt/spark/scripts/mongo_to_hdfs.py

# Exécuter un script Pig
docker exec pig pig -x mapreduce /scripts/eda.pig

# Requête SQL via Spark Thrift
docker exec spark-thrift beeline -u jdbc:hive2://localhost:10000
```

### Gestion des données
```bash
# Lister les fichiers HDFS
docker exec namenode hdfs dfs -ls /data/

# Copier des fichiers
docker exec namenode hdfs dfs -put localfile /data/raw/

# Voir le contenu
docker exec namenode hdfs dfs -cat /data/curated/category_stats/part-r-00000
```

## 📈 Exemples d'utilisation

### 1. **Analyse des ventes par catégorie**
```sql
-- Via Spark Thrift Server
SELECT category, 
       COUNT(*) as nb_sales,
       SUM(total_amount) as revenue
FROM raw_sales 
GROUP BY category 
ORDER BY revenue DESC;
```

### 2. **Top utilisateurs**
```pig
-- Via Pig
users = LOAD 'hdfs:///data/raw/sales/' USING PigStorage(',');
by_user = GROUP users BY user_id;
user_totals = FOREACH by_user GENERATE group, SUM(users.total_amount);
top_users = ORDER user_totals BY $1 DESC;
STORE top_users INTO 'hdfs:///data/curated/top_users';
```

### 3. **Dashboard temps réel**
- Ouvrir http://localhost:8501
- Naviguer entre les différentes vues
- Filtrer et explorer les données

## 🔍 Tests et validation

### Tests techniques
1. **MongoDB → Spark** : Vérifier la lecture des documents
2. **HDFS write** : Confirmer l'écriture en Parquet
3. **Pig EDA** : Valider les agrégations
4. **Thrift JDBC** : Tester les requêtes SQL
5. **App Streamlit** : Vérifier les visualisations

### Validation des données
```bash
# Compter les documents MongoDB
docker exec mongodb mongo retail --eval "db.sales.count()"

# Vérifier les fichiers HDFS
docker exec namenode hdfs dfs -ls /data/raw/sales/

# Tester une requête SQL
docker exec spark-thrift beeline -u jdbc:hive2://localhost:10000 -e "SELECT COUNT(*) FROM raw_sales;"
```

## 🚨 Dépannage

### Problèmes courants

**1. Services ne démarrent pas**
```bash
# Vérifier les logs
docker-compose logs [service-name]

# Redémarrer un service
docker-compose restart [service-name]
```

**2. HDFS non accessible**
```bash
# Vérifier l'état du NameNode
docker exec namenode hdfs dfsadmin -safemode get

# Formater le NameNode (si nécessaire)
docker exec namenode hdfs namenode -format
```

**3. Spark Workers non connectés**
```bash
# Vérifier la connectivité réseau
docker exec datanode-1 ping namenode

# Redémarrer les workers
docker-compose restart datanode-1 datanode-2 datanode-3
```

**4. MongoDB non accessible**
```bash
# Vérifier les logs MongoDB
docker-compose logs mongodb

# Tester la connexion
docker exec mongodb mongo --eval "db.adminCommand('ping')"
```

## 📚 Ressources additionnelles

### Documentation
- [Hadoop 3.3.6](https://hadoop.apache.org/docs/r3.3.6/)
- [Spark 3.5.1](https://spark.apache.org/docs/3.5.1/)
- [Pig 0.17.0](https://pig.apache.org/docs/r0.17.0/)
- [MongoDB Spark Connector](https://docs.mongodb.com/spark-connector/)

### Extensions possibles
- **Zookeeper + JournalNodes** pour HA complet
- **MinIO/S3** pour le stockage objet
- **Airflow** pour l'orchestration
- **Grafana + Prometheus** pour le monitoring

## 📄 Licence

Ce projet est fourni à des fins éducatives et de démonstration.

---

**Architecture développée pour le cours de Traitement Distribué**  
*Hadoop + Spark + Pig + MongoDB + Streamlit*

