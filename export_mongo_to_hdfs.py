#!/usr/bin/env python3
"""
Script d'export automatique MongoDB vers HDFS
Exporte les données de MongoDB vers HDFS toutes les 5 minutes
"""

import os
import sys
import time
import logging
import tempfile
import subprocess
from datetime import datetime
import pymongo
from pymongo import MongoClient

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MongoToHDFSExporter:
    def __init__(self):
        self.client = None
        self.collection = None
        self.last_export_count = 0
        self.running = True
        
        # Configuration depuis les variables d'environnement
        self.mongo_uri = os.getenv('MONGO_URI', 'mongodb://mongodb:27017/')
        self.export_interval = int(os.getenv('EXPORT_INTERVAL', '300'))  # 5 minutes
        self.batch_size = int(os.getenv('BATCH_SIZE', '100000'))
        
    def connect_mongodb(self):
        """Connexion à MongoDB avec retry"""
        max_retries = 5
        retry_delay = 10
        
        for attempt in range(max_retries):
            try:
                logger.info(f"🔄 Tentative de connexion MongoDB (tentative {attempt + 1}/{max_retries})")
                self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
                self.client.admin.command('ping')
                self.collection = self.client.retail.sales
                logger.info("✅ Connexion MongoDB réussie")
                return True
            except Exception as e:
                logger.warning(f"⚠️ Échec de connexion MongoDB: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"⏳ Nouvelle tentative dans {retry_delay} secondes...")
                    time.sleep(retry_delay)
                else:
                    logger.error("❌ Impossible de se connecter à MongoDB")
                    return False
        return False
    
    def check_hdfs_connection(self):
        """Vérification de la connexion HDFS"""
        try:
            result = subprocess.run(
                ['docker', 'exec', 'namenode', 'hdfs', 'dfs', '-ls', '/'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                logger.info("✅ Connexion HDFS réussie")
                return True
            else:
                logger.warning(f"⚠️ Problème de connexion HDFS: {result.stderr}")
                return False
        except Exception as e:
            logger.warning(f"⚠️ Erreur lors de la vérification HDFS: {e}")
            return False
    
    def get_total_documents(self):
        """Récupération du nombre total de documents"""
        try:
            return self.collection.count_documents({})
        except Exception as e:
            logger.error(f"❌ Erreur lors du comptage des documents: {e}")
            return 0
    
    def export_to_csv(self, output_file, limit=None):
        """Export des données vers un fichier CSV"""
        try:
            # Champs à exporter (tous les champs de la collection enrichie)
            fields = [
                'sale_id', 'user_id', 'product_id', 'product_name', 'quantity',
                'unit_price', 'total_amount', 'sale_date', 'category', 'store_id',
                'payment_method', 'region', 'customer_age', 'customer_gender',
                'discount_applied', 'discount_amount', 'shipping_cost', 'tax_amount',
                'created_at', 'updated_at'
            ]
            
            with open(output_file, 'w', encoding='utf-8') as f:
                # Écriture de l'en-tête
                f.write(','.join(fields) + '\n')
                
                # Export par lots pour éviter les problèmes de curseur
                batch_size = min(limit or 10000, 10000)  # Limite à 10k par lot
                processed = 0
                
                while True:
                    # Pipeline d'agrégation pour formater les données
                    pipeline = [
                        {'$skip': processed},
                        {'$limit': batch_size}
                    ]
                    
                    # Ajout des champs manquants avec des valeurs par défaut
                    pipeline.append({
                        '$addFields': {
                            'sale_id': {'$toString': '$_id'},
                            'user_id': {'$ifNull': ['$user_id', 'unknown']},
                            'product_id': {'$ifNull': ['$product_id', 'unknown']},
                            'product_name': {'$ifNull': ['$product_name', 'Unknown Product']},
                            'quantity': {'$ifNull': ['$quantity', 1]},
                            'unit_price': {'$ifNull': ['$unit_price', 0.0]},
                            'total_amount': {'$ifNull': ['$total_amount', 0.0]},
                            'sale_date': {'$ifNull': ['$sale_date', '2024-01-01']},
                            'category': {'$ifNull': ['$category', 'Unknown']},
                            'store_id': {'$ifNull': ['$store_id', 'unknown']},
                            'payment_method': {'$ifNull': ['$payment_method', 'Unknown']},
                            'region': {'$ifNull': ['$region', 'Unknown']},
                            'customer_age': {'$ifNull': ['$customer_age', 25]},
                            'customer_gender': {'$ifNull': ['$customer_gender', 'Unknown']},
                            'discount_applied': {'$ifNull': ['$discount_applied', False]},
                            'discount_amount': {'$ifNull': ['$discount_amount', 0.0]},
                            'shipping_cost': {'$ifNull': ['$shipping_cost', 0.0]},
                            'tax_amount': {'$ifNull': ['$tax_amount', 0.0]},
                            'created_at': {'$ifNull': ['$created_at', '2024-01-01T00:00:00Z']},
                            'updated_at': {'$ifNull': ['$updated_at', '2024-01-01T00:00:00Z']}
                        }
                    })
                    
                    # Projection pour sélectionner les champs dans l'ordre
                    pipeline.append({'$project': {field: 1 for field in fields}})
                    
                    # Export des données du lot
                    cursor = self.collection.aggregate(pipeline, allowDiskUse=True, batchSize=1000)
                    batch_count = 0
                    
                    for doc in cursor:
                        row = []
                        for field in fields:
                            value = doc.get(field, '')
                            # Conversion des valeurs pour CSV
                            if isinstance(value, bool):
                                value = str(value).lower()
                            elif value is None:
                                value = ''
                            else:
                                value = str(value).replace(',', ';')
                            row.append(value)
                        f.write(','.join(row) + '\n')
                        batch_count += 1
                    
                    processed += batch_count
                    logger.info(f"📦 Lot traité: {batch_count} documents (total: {processed:,})")
                    
                    # Vérification si on a terminé
                    if limit and processed >= limit:
                        break
                    if batch_count < batch_size:
                        break
                    
                    # Pause entre les lots pour éviter la surcharge
                    time.sleep(1)
            
            logger.info(f"✅ Export CSV terminé: {output_file} ({processed:,} documents)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'export CSV: {e}")
            return False
    
    def upload_to_hdfs(self, local_file, hdfs_path):
        """Upload du fichier local vers HDFS"""
        try:
            # Copie du fichier vers le conteneur namenode
            copy_cmd = [
                'docker', 'cp', local_file, f'namenode:/tmp/{os.path.basename(local_file)}'
            ]
            result = subprocess.run(copy_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"❌ Erreur lors de la copie vers namenode: {result.stderr}")
                return False
            
            # Upload vers HDFS
            upload_cmd = [
                'docker', 'exec', 'namenode', 'hdfs', 'dfs', '-put',
                f'/tmp/{os.path.basename(local_file)}', hdfs_path
            ]
            result = subprocess.run(upload_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"❌ Erreur lors de l'upload HDFS: {result.stderr}")
                return False
            
            # Nettoyage du fichier temporaire
            cleanup_cmd = [
                'docker', 'exec', 'namenode', 'rm', f'/tmp/{os.path.basename(local_file)}'
            ]
            subprocess.run(cleanup_cmd, capture_output=True)
            
            logger.info(f"✅ Upload HDFS réussi: {hdfs_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'upload HDFS: {e}")
            return False
    
    def perform_export(self):
        """Exécution de l'export complet"""
        try:
            # Vérification des connexions
            if not self.connect_mongodb():
                return False
            
            if not self.check_hdfs_connection():
                return False
            
            # Comptage des documents
            total_docs = self.get_total_documents()
            logger.info(f"📊 Nombre total de documents MongoDB: {total_docs:,}")
            
            # Vérification s'il y a de nouveaux documents
            if total_docs <= self.last_export_count:
                logger.info("ℹ️ Aucun nouveau document à exporter")
                return True
            
            new_docs = total_docs - self.last_export_count
            logger.info(f"🔄 Export de {new_docs:,} nouveaux documents...")
            
            # Création du fichier temporaire
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
                temp_file_path = tmp_file.name
            
            try:
                # Export vers CSV
                if not self.export_to_csv(temp_file_path, limit=new_docs):
                    return False
                
                # Upload vers HDFS
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                hdfs_path = f'/data/raw/sales/sales_export_{timestamp}.csv'
                
                if not self.upload_to_hdfs(temp_file_path, hdfs_path):
                    return False
                
                # Mise à jour du compteur
                self.last_export_count = total_docs
                logger.info(f"✅ Export terminé avec succès: {hdfs_path}")
                return True
                
            finally:
                # Nettoyage du fichier temporaire
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'export: {e}")
            return False
    
    def signal_handler(self, signum, frame):
        """Gestionnaire de signal pour arrêt gracieux"""
        logger.info("🛑 Signal d'arrêt reçu, arrêt gracieux...")
        self.running = False
    
    def run_continuous(self):
        """Boucle principale d'exécution continue"""
        logger.info("🚀 Démarrage du service d'export automatique MongoDB vers HDFS")
        logger.info(f"⏰ Intervalle d'export: {self.export_interval} secondes")
        logger.info(f"📦 Taille de lot: {self.batch_size:,} documents")
        
        while self.running:
            try:
                logger.info("=" * 60)
                logger.info(f"🔄 Cycle d'export - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                if self.perform_export():
                    logger.info("✅ Cycle d'export réussi")
                else:
                    logger.warning("⚠️ Cycle d'export échoué, nouvelle tentative au prochain cycle")
                
                if self.running:
                    logger.info(f"⏳ Attente du prochain cycle ({self.export_interval} secondes)...")
                    time.sleep(self.export_interval)
                    
            except KeyboardInterrupt:
                logger.info("🛑 Interruption clavier détectée")
                break
            except Exception as e:
                logger.error(f"❌ Erreur inattendue: {e}")
                if self.running:
                    logger.info("⏳ Attente avant nouvelle tentative...")
                    time.sleep(30)
        
        logger.info("👋 Arrêt du service d'export automatique")

def main():
    logger.info("🎯 Service d'export MongoDB vers HDFS")
    logger.info("=" * 60)
    
    exporter = MongoToHDFSExporter()
    
    try:
        exporter.run_continuous()
    except Exception as e:
        logger.error(f"❌ Erreur fatale: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
