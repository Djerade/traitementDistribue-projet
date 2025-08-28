#!/usr/bin/env python3
"""
Exemple simple de travail Spark qui fonctionne
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
import pymongo
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Fonction principale"""
    logger.info("🚀 Démarrage du traitement Spark simple")
    
    try:
        # Créer la session Spark
        spark = SparkSession.builder \
            .appName("ExempleSimpleSpark") \
            .master("local[*]") \
            .getOrCreate()
        
        logger.info("✅ Session Spark créée")
        
        # Créer des données d'exemple
        data = [
            {"user_id": "user1", "product": "laptop", "amount": 1200.0, "category": "electronics"},
            {"user_id": "user2", "product": "phone", "amount": 800.0, "category": "electronics"},
            {"user_id": "user1", "product": "book", "amount": 25.0, "category": "books"},
            {"user_id": "user3", "product": "shirt", "amount": 50.0, "category": "clothing"},
            {"user_id": "user2", "product": "laptop", "amount": 1200.0, "category": "electronics"},
            {"user_id": "user3", "product": "book", "amount": 30.0, "category": "books"},
            {"user_id": "user1", "product": "phone", "amount": 800.0, "category": "electronics"},
            {"user_id": "user2", "product": "shirt", "amount": 45.0, "category": "clothing"},
        ]
        
        # Créer le DataFrame Spark
        df = spark.createDataFrame(data)
        logger.info(f"✅ {df.count()} lignes créées dans Spark")
        
        print("\n" + "="*50)
        print("📊 DONNÉES D'EXEMPLE")
        print("="*50)
        df.show()
        
        # Analyse par catégorie
        print("\n📈 ANALYSE PAR CATÉGORIE")
        print("-" * 30)
        resultat_categories = df.groupBy("category") \
            .agg(
                count("*").alias("nombre_ventes"),
                sum("amount").alias("revenu_total"),
                avg("amount").alias("montant_moyen")
            ) \
            .orderBy(col("revenu_total").desc())
        
        resultat_categories.show()
        
        # Analyse par utilisateur
        print("\n📈 ANALYSE PAR UTILISATEUR")
        print("-" * 30)
        resultat_utilisateurs = df.groupBy("user_id") \
            .agg(
                count("*").alias("nombre_achats"),
                sum("amount").alias("montant_total"),
                avg("amount").alias("panier_moyen")
            ) \
            .orderBy(col("montant_total").desc())
        
        resultat_utilisateurs.show()
        
        # Top produits
        print("\n📈 TOP PRODUITS")
        print("-" * 30)
        resultat_produits = df.groupBy("product") \
            .agg(
                count("*").alias("nombre_ventes"),
                sum("amount").alias("revenu_total")
            ) \
            .orderBy(col("revenu_total").desc())
        
        resultat_produits.show()
        
        # Statistiques générales
        print("\n📊 STATISTIQUES GÉNÉRALES")
        print("-" * 30)
        stats = df.select(
            count("*").alias("total_ventes"),
            sum("amount").alias("revenu_total"),
            avg("amount").alias("panier_moyen"),
            countDistinct("user_id").alias("utilisateurs_uniques"),
            countDistinct("product").alias("produits_uniques"),
            countDistinct("category").alias("categories_uniques")
        ).collect()[0]
        
        print(f"Total des ventes: {stats['total_ventes']}")
        print(f"Revenu total: {stats['revenu_total']:.2f} €")
        print(f"Panier moyen: {stats['panier_moyen']:.2f} €")
        print(f"Utilisateurs uniques: {stats['utilisateurs_uniques']}")
        print(f"Produits uniques: {stats['produits_uniques']}")
        print(f"Catégories uniques: {stats['categories_uniques']}")
        
        logger.info("🎉 Traitement Spark simple terminé avec succès!")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du traitement: {e}")
        raise
    finally:
        if 'spark' in locals():
            spark.stop()
            logger.info("🛑 Session Spark fermée")

if __name__ == "__main__":
    main()
