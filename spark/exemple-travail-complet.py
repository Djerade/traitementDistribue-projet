#!/usr/bin/env python3
"""
Exemple de travail Spark complet pour démontrer le traitement distribué
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
import pymongo
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def creer_session_spark():
    """Créer une session Spark connectée au cluster"""
    return SparkSession.builder \
        .appName("TraitementDistribueVentes") \
        .config("spark.master", "spark://namenode:7077") \
        .config("spark.driver.memory", "1g") \
        .config("spark.executor.memory", "2g") \
        .config("spark.executor.cores", "2") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
        .enableHiveSupport() \
        .getOrCreate()

def charger_donnees_mongodb(spark, limite=50000):
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

def analyser_tendances_temporelles(df):
    """Analyser les tendances temporelles"""
    logger.info("Analyse des tendances temporelles...")
    
    from pyspark.sql.functions import to_date, year, month, dayofweek
    
    resultat = df.withColumn("date_vente", to_date("timestamp")) \
        .groupBy(
            year("date_vente").alias("annee"),
            month("date_vente").alias("mois"),
            dayofweek("date_vente").alias("jour_semaine")
        ) \
        .agg(
            count("*").alias("nombre_ventes"),
            sum("total_amount").alias("revenu_total"),
            avg("total_amount").alias("panier_moyen")
        ) \
        .orderBy("annee", "mois", "jour_semaine")
    
    logger.info("✅ Analyse temporelle terminée")
    return resultat

def sauvegarder_resultats_hdfs(resultats, nom_analyse):
    """Sauvegarder les résultats sur HDFS"""
    logger.info(f"Sauvegarde des résultats {nom_analyse} sur HDFS...")
    
    chemin_hdfs = f"hdfs://namenode:9000/spark-results/{nom_analyse}"
    
    resultats.write \
        .mode("overwrite") \
        .parquet(chemin_hdfs)
    
    logger.info(f"✅ Résultats sauvegardés: {chemin_hdfs}")

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
    logger.info("🚀 Démarrage du traitement distribué Spark")
    
    try:
        # Créer la session Spark
        spark = creer_session_spark()
        logger.info("✅ Session Spark créée")
        
        # Charger les données
        df = charger_donnees_mongodb(spark, limite=100000)
        if df is None:
            logger.error("❌ Impossible de charger les données")
            return
        
        # Afficher les statistiques générales
        afficher_statistiques(df)
        
        # Effectuer les analyses
        analyses = {
            "ventes-par-categorie": analyser_ventes_par_categorie(df),
            "top-produits": analyser_top_produits(df, 15),
            "utilisateurs-actifs": analyser_utilisateurs_actifs(df, 25),
            "tendances-temporelles": analyser_tendances_temporelles(df)
        }
        
        # Afficher et sauvegarder les résultats
        for nom, resultat in analyses.items():
            print(f"\n📈 RÉSULTATS: {nom.upper()}")
            print("-" * 40)
            resultat.show(truncate=False)
            
            # Sauvegarder sur HDFS
            sauvegarder_resultats_hdfs(resultat, nom)
        
        logger.info("🎉 Traitement distribué terminé avec succès!")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du traitement: {e}")
        raise
    finally:
        if 'spark' in locals():
            spark.stop()
            logger.info("🛑 Session Spark fermée")

if __name__ == "__main__":
    main()
