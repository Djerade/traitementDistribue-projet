#!/usr/bin/env python3
"""
Exemple de travail Spark en mode local pour démontrer le traitement distribué
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
import pymongo
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def creer_session_spark_local():
    """Créer une session Spark en mode local"""
    return SparkSession.builder \
        .appName("TraitementLocalVentes") \
        .config("spark.driver.memory", "1g") \
        .config("spark.executor.memory", "1g") \
        .config("spark.sql.adaptive.enabled", "true") \
        .master("local[*]") \
        .getOrCreate()

def charger_donnees_mongodb(spark, limite=1000):
    """Charger les données depuis MongoDB vers Spark"""
    logger.info(f"Chargement de {limite} documents depuis MongoDB...")
    
    client = pymongo.MongoClient("mongodb://mongodb:27017")
    db = client.retail
    collection = db.sales
    
    # Charger les données
    cursor = collection.find({}, {'_id': 0}).limit(limite)
    data = list(cursor)
    
    if not data:
        logger.error("Aucune donnée trouvée dans MongoDB")
        return None
    
    # Créer le DataFrame Spark
    df = spark.createDataFrame(data)
    logger.info(f"✅ {df.count()} lignes chargées dans Spark")
    
    return df

def analyser_ventes_par_categorie(df):
    """Analyser les ventes par catégorie de produits"""
    logger.info("Analyse des ventes par catégorie...")
    
    resultat = df.groupBy("category") \
        .agg(
            count("*").alias("nombre_ventes"),
            sum("total_amount").alias("revenu_total"),
            avg("total_amount").alias("montant_moyen"),
            max("total_amount").alias("vente_max"),
            sum("quantity").alias("quantite_totale")
        ) \
        .orderBy(col("revenu_total").desc())
    
    logger.info("✅ Analyse par catégorie terminée")
    return resultat

def analyser_top_produits(df, top_n=10):
    """Analyser les produits les plus vendus"""
    logger.info(f"Analyse des top {top_n} produits...")
    
    resultat = df.groupBy("product_name") \
        .agg(
            count("*").alias("nombre_ventes"),
            sum("quantity").alias("quantite_totale"),
            sum("total_amount").alias("revenu_total"),
            avg("total_amount").alias("prix_moyen")
        ) \
        .orderBy(col("revenu_total").desc()) \
        .limit(top_n)
    
    logger.info("✅ Analyse des top produits terminée")
    return resultat

def analyser_utilisateurs_actifs(df, top_n=20):
    """Analyser les utilisateurs les plus actifs"""
    logger.info(f"Analyse des {top_n} utilisateurs les plus actifs...")
    
    resultat = df.groupBy("user_id") \
        .agg(
            count("*").alias("nombre_achats"),
            sum("total_amount").alias("montant_total"),
            avg("total_amount").alias("panier_moyen"),
            countDistinct("category").alias("categories_differentes")
        ) \
        .orderBy(col("montant_total").desc()) \
        .limit(top_n)
    
    logger.info("✅ Analyse des utilisateurs terminée")
    return resultat

def afficher_statistiques(df):
    """Afficher des statistiques générales"""
    logger.info("Calcul des statistiques générales...")
    
    stats = df.select(
        count("*").alias("total_ventes"),
        sum("total_amount").alias("revenu_total"),
        avg("total_amount").alias("panier_moyen"),
        countDistinct("user_id").alias("utilisateurs_uniques"),
        countDistinct("product_name").alias("produits_uniques"),
        countDistinct("category").alias("categories_uniques")
    ).collect()[0]
    
    print("\n" + "="*50)
    print("📊 STATISTIQUES GÉNÉRALES")
    print("="*50)
    print(f"Total des ventes: {stats['total_ventes']:,}")
    print(f"Revenu total: {stats['revenu_total']:,.2f} €")
    print(f"Panier moyen: {stats['panier_moyen']:.2f} €")
    print(f"Utilisateurs uniques: {stats['utilisateurs_uniques']:,}")
    print(f"Produits uniques: {stats['produits_uniques']:,}")
    print(f"Catégories uniques: {stats['categories_uniques']:,}")
    print("="*50)

def main():
    """Fonction principale"""
    logger.info("🚀 Démarrage du traitement Spark local")
    
    try:
        # Créer la session Spark
        spark = creer_session_spark_local()
        logger.info("✅ Session Spark locale créée")
        
        # Charger les données
        df = charger_donnees_mongodb(spark, limite=1000)
        if df is None:
            logger.error("❌ Impossible de charger les données")
            return
        
        # Afficher les statistiques générales
        afficher_statistiques(df)
        
        # Effectuer les analyses
        print("\n📈 RÉSULTATS: VENTES PAR CATÉGORIE")
        print("-" * 40)
        resultat_categories = analyser_ventes_par_categorie(df)
        resultat_categories.show(truncate=False)
        
        print("\n📈 RÉSULTATS: TOP PRODUITS")
        print("-" * 40)
        resultat_produits = analyser_top_produits(df, 10)
        resultat_produits.show(truncate=False)
        
        print("\n📈 RÉSULTATS: UTILISATEURS ACTIFS")
        print("-" * 40)
        resultat_utilisateurs = analyser_utilisateurs_actifs(df, 15)
        resultat_utilisateurs.show(truncate=False)
        
        logger.info("🎉 Traitement Spark local terminé avec succès!")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du traitement: {e}")
        raise
    finally:
        if 'spark' in locals():
            spark.stop()
            logger.info("🛑 Session Spark fermée")

if __name__ == "__main__":
    main()
