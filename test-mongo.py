#!/usr/bin/env python3
"""
Script de test pour valider la connexion MongoDB
"""

import pymongo
import pandas as pd
import sys
import time

def test_mongodb_connection():
    """Tester la connexion MongoDB et afficher les statistiques"""
    try:
        # Connexion à MongoDB
        client = pymongo.MongoClient("mongodb://mongodb_new:27017/")
        
        # Vérifier la connexion
        client.admin.command('ping')
        print("✅ MongoDB connecté avec succès!")
        
        # Accéder à la base de données
        db = client["retail"]
        collection = db["sales"]
        
        # Récupérer les données
        data = list(collection.find({}, {'_id': 0}))
        df = pd.DataFrame(data)
        
        # Afficher les statistiques
        print(f"📊 {len(df)} documents trouvés")
        print(f"📈 Chiffre d'affaires total: ${df['total_amount'].sum():,.2f}")
        print(f"👥 Utilisateurs uniques: {df['user_id'].nunique()}")
        print(f"🏷️  Catégories: {df['category'].nunique()}")
        
        # Afficher un échantillon
        print("\n📋 Échantillon des données:")
        print(df.head(3).to_string(index=False))
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur de connexion MongoDB: {e}")
        return False

if __name__ == "__main__":
    # Attendre un peu que MongoDB soit prêt
    time.sleep(5)
    
    success = test_mongodb_connection()
    sys.exit(0 if success else 1)
