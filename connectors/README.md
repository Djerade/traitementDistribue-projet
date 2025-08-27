# Connecteurs pour l'Architecture Traitement Distribué

Ce répertoire contient les connecteurs nécessaires pour l'intégration entre les différents composants.

## Connecteurs requis

### 1. MongoDB Spark Connector
- **Fichier**: `mongo-spark-connector_2.12-10.1.1.jar`
- **URL de téléchargement**: https://search.maven.org/remotecontent?filepath=org/mongodb/spark/mongo-spark-connector_2.12/10.1.1/mongo-spark-connector_2.12-10.1.1.jar
- **Usage**: Permet à Spark de lire directement depuis MongoDB

### 2. PostgreSQL JDBC Driver (pour Hive Metastore)
- **Fichier**: `postgresql-42.7.1.jar`
- **URL de téléchargement**: https://jdbc.postgresql.org/download/postgresql-42.7.1.jar
- **Usage**: Connexion Hive Metastore vers PostgreSQL

## Installation

```bash
# Télécharger le MongoDB Spark Connector
wget https://search.maven.org/remotecontent?filepath=org/mongodb/spark/mongo-spark-connector_2.12/10.1.1/mongo-spark-connector_2.12-10.1.1.jar -O mongo-spark-connector_2.12-10.1.1.jar

# Télécharger le driver PostgreSQL
wget https://jdbc.postgresql.org/download/postgresql-42.7.1.jar -O postgresql-42.7.1.jar
```

## Configuration

Les connecteurs sont automatiquement ajoutés au classpath dans les Dockerfiles correspondants.

### Pour Spark
Le MongoDB Spark Connector est configuré dans les scripts Spark via les options :
- `spark.mongodb.read.connection.uri`
- `spark.mongodb.read.database`
- `spark.mongodb.read.collection`

### Pour Hive
Le driver PostgreSQL est configuré dans `hive-site.xml` pour la connexion au metastore.
