#!/usr/bin/env python3
"""
Script Spark pour ingérer les données MongoDB vers HDFS
Utilise le MongoDB Spark Connector pour lire depuis MongoDB et écrire en Parquet sur HDFS
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
import sys
import os

def create_spark_session():
    """Créer une session Spark avec configuration MongoDB"""
    spark = (SparkSession.builder
        .appName("MongoDB to HDFS Ingestion")
        .config("spark.mongodb.read.connection.uri", "mongodb://mongodb:27017")
        .config("spark.mongodb.read.database", "retail")
        .config("spark.mongodb.read.collection", "sales")
        .config("spark.sql.warehouse.dir", "hdfs://namenode:9000/user/hive/warehouse")
        .config("spark.sql.catalogImplementation", "hive")
        .enableHiveSupport()
        .getOrCreate())
    
    return spark

def ingest_sales_data(spark):
    """Ingérer les données de ventes depuis MongoDB vers HDFS"""
    
    print("Début de l'ingestion des données de ventes...")
    
    # Lire les données depuis MongoDB
    print("Lecture des données depuis MongoDB...")
    sales_df = spark.read.format("mongodb").load()
    
    print(f"Nombre de documents lus: {sales_df.count()}")
    print("Schéma des données:")
    sales_df.printSchema()
    
    # Afficher un échantillon des données
    print("Échantillon des données:")
    sales_df.show(5)
    
    # Nettoyage et transformation des données
    print("Nettoyage et transformation des données...")
    
    # Convertir les types de données
    cleaned_df = sales_df.withColumn(
        "sale_date", 
        to_date(col("sale_date"), "yyyy-MM-dd")
    ).withColumn(
        "total_amount", 
        col("total_amount").cast("double")
    ).withColumn(
        "quantity", 
        col("quantity").cast("int")
    ).withColumn(
        "unit_price", 
        col("unit_price").cast("double")
    )
    
    # Ajouter une colonne de partition par date
    partitioned_df = cleaned_df.withColumn(
        "dt", 
        date_format(col("sale_date"), "yyyy-MM-dd")
    )
    
    # Écrire en Parquet sur HDFS
    print("Écriture des données en Parquet sur HDFS...")
    
    # Écrire dans la zone raw
    raw_path = "hdfs://namenode:9000/data/raw/sales"
    partitioned_df.write.mode("overwrite").partitionBy("dt").parquet(raw_path)
    
    print(f"Données écrites dans: {raw_path}")
    
    # Créer une table Hive externe
    print("Création de la table Hive externe...")
    
    spark.sql(f"""
    CREATE TABLE IF NOT EXISTS raw_sales (
        sale_id STRING,
        user_id STRING,
        product_id STRING,
        product_name STRING,
        quantity INT,
        unit_price DOUBLE,
        total_amount DOUBLE,
        sale_date DATE,
        category STRING
    )
    PARTITIONED BY (dt STRING)
    STORED AS PARQUET
    LOCATION '{raw_path}'
    """)
    
    # Récupérer les partitions
    spark.sql("MSCK REPAIR TABLE raw_sales")
    
    print("Table Hive 'raw_sales' créée avec succès!")
    
    # Afficher les statistiques de la table
    print("Statistiques de la table raw_sales:")
    spark.sql("SELECT COUNT(*) as total_records FROM raw_sales").show()
    spark.sql("SELECT dt, COUNT(*) as records FROM raw_sales GROUP BY dt ORDER BY dt").show()
    
    return cleaned_df

def create_curated_tables(spark, sales_df):
    """Créer des tables curated pour l'analyse"""
    
    print("Création des tables curated...")
    
    # Table des statistiques par catégorie
    category_stats = sales_df.groupBy("category").agg(
        count("*").alias("nb_sales"),
        sum("total_amount").alias("total_revenue"),
        avg("total_amount").alias("avg_sale_amount"),
        min("total_amount").alias("min_sale_amount"),
        max("total_amount").alias("max_sale_amount")
    )
    
    curated_path = "hdfs://namenode:9000/data/curated/sales"
    category_stats.write.mode("overwrite").parquet(f"{curated_path}/category_stats")
    
    # Table des top utilisateurs
    user_stats = sales_df.groupBy("user_id").agg(
        sum("total_amount").alias("total_spent"),
        count("*").alias("nb_purchases"),
        avg("total_amount").alias("avg_purchase_amount")
    ).orderBy(col("total_spent").desc())
    
    user_stats.write.mode("overwrite").parquet(f"{curated_path}/user_stats")
    
    # Table des statistiques quotidiennes
    daily_stats = sales_df.groupBy("sale_date").agg(
        count("*").alias("nb_sales"),
        sum("total_amount").alias("daily_revenue"),
        avg("total_amount").alias("avg_sale_amount")
    ).orderBy("sale_date")
    
    daily_stats.write.mode("overwrite").parquet(f"{curated_path}/daily_stats")
    
    # Créer les tables Hive
    spark.sql(f"""
    CREATE TABLE IF NOT EXISTS category_stats (
        category STRING,
        nb_sales BIGINT,
        total_revenue DOUBLE,
        avg_sale_amount DOUBLE,
        min_sale_amount DOUBLE,
        max_sale_amount DOUBLE
    )
    STORED AS PARQUET
    LOCATION '{curated_path}/category_stats'
    """)
    
    spark.sql(f"""
    CREATE TABLE IF NOT EXISTS user_stats (
        user_id STRING,
        total_spent DOUBLE,
        nb_purchases BIGINT,
        avg_purchase_amount DOUBLE
    )
    STORED AS PARQUET
    LOCATION '{curated_path}/user_stats'
    """)
    
    spark.sql(f"""
    CREATE TABLE IF NOT EXISTS daily_stats (
        sale_date DATE,
        nb_sales BIGINT,
        daily_revenue DOUBLE,
        avg_sale_amount DOUBLE
    )
    STORED AS PARQUET
    LOCATION '{curated_path}/daily_stats'
    """)
    
    print("Tables curated créées avec succès!")

def main():
    """Fonction principale"""
    
    print("=== Début du processus d'ingestion MongoDB vers HDFS ===")
    
    try:
        # Créer la session Spark
        spark = create_spark_session()
        
        # Ingest des données de ventes
        sales_df = ingest_sales_data(spark)
        
        # Créer les tables curated
        create_curated_tables(spark, sales_df)
        
        print("=== Processus d'ingestion terminé avec succès! ===")
        
        # Afficher un résumé
        print("\nRésumé de l'ingestion:")
        print(f"- Documents traités: {sales_df.count()}")
        print(f"- Catégories: {sales_df.select('category').distinct().count()}")
        print(f"- Utilisateurs uniques: {sales_df.select('user_id').distinct().count()}")
        print(f"- Période: {sales_df.agg(min('sale_date'), max('sale_date')).collect()[0]}")
        
    except Exception as e:
        print(f"Erreur lors de l'ingestion: {e}")
        sys.exit(1)
    finally:
        if 'spark' in locals():
            spark.stop()

if __name__ == "__main__":
    main()
