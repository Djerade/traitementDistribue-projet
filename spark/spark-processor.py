#!/usr/bin/env python3
"""
Service Spark pour le traitement distribué des données
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
import pymongo
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SparkDataProcessor:
    def __init__(self):
        self.spark = SparkSession.builder \
            .appName("RetailDataProcessor") \
            .config("spark.master", "spark://namenode:7077") \
            .config("spark.driver.memory", "1g") \
            .config("spark.executor.memory", "2g") \
            .config("spark.executor.cores", "2") \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
            .enableHiveSupport() \
            .getOrCreate()
        
        logger.info("Session Spark initialisée")
        
    def load_mongo_data_to_spark(self, limit=None):
        """Charge les données MongoDB dans Spark DataFrame"""
        try:
            mongo_client = pymongo.MongoClient("mongodb://mongodb:27017")
            db = mongo_client['retail']
            collection = db['sales']
            
            if limit:
                cursor = collection.find({}, {'_id': 0}).limit(limit)
            else:
                cursor = collection.find({}, {'_id': 0})
            
            data = list(cursor)
            if data:
                df = self.spark.createDataFrame(data)
                logger.info(f"Données MongoDB chargées: {df.count()} lignes")
                return df
            return None
                
        except Exception as e:
            logger.error(f"Erreur MongoDB: {e}")
            return None
    
    def analyze_sales_by_category(self, df):
        """Analyse les ventes par catégorie"""
        if df is None:
            return None
            
        try:
            result = df.groupBy("category") \
                .agg(
                    count("*").alias("nombre_ventes"),
                    sum("total_amount").alias("chiffre_affaires"),
                    avg("total_amount").alias("montant_moyen")
                ) \
                .orderBy(col("chiffre_affaires").desc())
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur analyse catégorie: {e}")
            return None
    
    def analyze_top_products(self, df, top_n=10):
        """Analyse les produits les plus vendus"""
        if df is None:
            return None
            
        try:
            result = df.groupBy("product_name", "category") \
                .agg(
                    count("*").alias("nombre_ventes"),
                    sum("total_amount").alias("chiffre_affaires")
                ) \
                .orderBy(col("chiffre_affaires").desc()) \
                .limit(top_n)
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur analyse produits: {e}")
            return None
    
    def save_to_hdfs(self, df, path, format="parquet"):
        """Sauvegarde le DataFrame dans HDFS"""
        if df is None:
            return False
            
        try:
            df.write \
                .mode("overwrite") \
                .format(format) \
                .save(f"hdfs://namenode:9000{path}")
            
            logger.info(f"Données sauvegardées HDFS: {path}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde HDFS: {e}")
            return False
    
    def run_analysis(self, limit=None):
        """Exécute l'analyse complète"""
        logger.info("Début analyse Spark")
        
        df = self.load_mongo_data_to_spark(limit)
        if df is None:
            return None
        
        results = {}
        results['category_analysis'] = self.analyze_sales_by_category(df)
        results['top_products'] = self.analyze_top_products(df)
        
        # Sauvegarder dans HDFS
        if results['category_analysis']:
            self.save_to_hdfs(results['category_analysis'], "/user/spark/analyses/category_analysis")
        
        logger.info("Analyse Spark terminée")
        return results
    
    def stop(self):
        if self.spark:
            self.spark.stop()

def main():
    processor = SparkDataProcessor()
    
    try:
        results = processor.run_analysis(limit=10000)
        
        if results:
            print("=== RÉSULTATS SPARK ===")
            
            if results['category_analysis']:
                print("\n--- Analyse par catégorie ---")
                results['category_analysis'].show()
            
            if results['top_products']:
                print("\n--- Top produits ---")
                results['top_products'].show()
        
    except Exception as e:
        logger.error(f"Erreur: {e}")
    
    finally:
        processor.stop()

if __name__ == "__main__":
    main()
