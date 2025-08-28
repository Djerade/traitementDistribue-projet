import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pymongo
# from pyhive import hive  # Temporairement désactivé
import os
from datetime import datetime, timedelta

# Imports Spark (optionnels - seulement si PySpark est disponible)
try:
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import *
    SPARK_AVAILABLE = True
except ImportError:
    SPARK_AVAILABLE = False
    st.warning("⚠️ PySpark n'est pas installé. Certaines fonctionnalités Spark seront désactivées.")

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Ventes - Traitement Distribué",
    page_icon="📊",
    layout="wide"
)

# Titre principal
st.title("📊 Dashboard Ventes - Architecture Traitement Distribué")
st.markdown("---")

# Configuration des connexions
@st.cache_resource
def get_mongo_connection():
    """Connexion à MongoDB"""
    try:
        # Utiliser les variables d'environnement si disponibles
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://mongodb:27017/')
        client = pymongo.MongoClient(mongo_uri)
        return client
    except Exception as e:
        st.error(f"Erreur de connexion MongoDB: {e}")
        return None

@st.cache_resource
def get_hive_connection():
    """Connexion à Hive via Spark Thrift - Temporairement désactivé"""
    st.warning("Connexion Hive temporairement désactivée")
    return None

# Sidebar pour la navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox(
    "Choisir une page",
    ["📈 Vue d'ensemble", "🔍 Exploration des données", "👥 Top Utilisateurs", "📅 Statistiques temporelles", "⚡ Analyses Spark"]
)

# Fonction pour charger les données depuis MongoDB
def load_mongo_data(limit=None):
    """Charger les données depuis MongoDB"""
    client = get_mongo_connection()
    if client:
        try:
            # Utiliser les variables d'environnement si disponibles
            db_name = os.getenv('MONGO_DB', 'retail')
            collection_name = os.getenv('MONGO_COLLECTION', 'sales')
            db = client[db_name]
            collection = db[collection_name]
            
            # Utiliser un curseur avec timeout et limite pour éviter les problèmes de mémoire
            cursor = collection.find({}, {'_id': 0})
            
            # Appliquer une limite si spécifiée, sinon utiliser une limite par défaut
            if limit:
                cursor = cursor.limit(limit)
            else:
                # Limite par défaut pour éviter les problèmes de mémoire
                cursor = cursor.limit(10000)
            
            # Convertir le curseur en liste avec gestion d'erreur
            data = list(cursor)
            return pd.DataFrame(data)
        except Exception as e:
            st.error(f"Erreur lors du chargement des données MongoDB: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

# Fonction pour charger les données depuis Hive
def load_hive_data(query):
    """Charger les données depuis Hive - Temporairement désactivé"""
    st.warning("Fonction Hive temporairement désactivée")
    return pd.DataFrame()

# Fonction pour exécuter des analyses Spark
def run_spark_analysis(analysis_type="category", limit=10000):
    """Exécute des analyses Spark et retourne les résultats"""
    if not SPARK_AVAILABLE:
        st.error("❌ PySpark n'est pas disponible. Impossible d'exécuter l'analyse Spark.")
        return None
        
    try:
        # Créer une session Spark en mode local
        spark = SparkSession.builder \
            .appName("StreamlitSparkAnalysis") \
            .config("spark.master", "local[*]") \
            .config("spark.driver.memory", "1g") \
            .config("spark.sql.adaptive.enabled", "true") \
            .getOrCreate()
        
        # Charger les données MongoDB
        client = get_mongo_connection()
        if not client:
            return None
            
        db_name = os.getenv('MONGO_DB', 'retail')
        collection_name = os.getenv('MONGO_COLLECTION', 'sales')
        db = client[db_name]
        collection = db[collection_name]
        
        # Charger avec limite
        cursor = collection.find({}, {'_id': 0}).limit(limit)
        data = list(cursor)
        
        if not data:
            return None
            
        # Créer DataFrame Spark
        df = spark.createDataFrame(data)
        
        # Exécuter l'analyse demandée
        if analysis_type == "category":
            result = df.groupBy("category") \
                .agg(
                    count("*").alias("nombre_ventes"),
                    sum("total_amount").alias("chiffre_affaires"),
                    avg("total_amount").alias("montant_moyen")
                ) \
                .orderBy(col("chiffre_affaires").desc())
                
        elif analysis_type == "products":
            result = df.groupBy("product_name", "category") \
                .agg(
                    count("*").alias("nombre_ventes"),
                    sum("total_amount").alias("chiffre_affaires")
                ) \
                .orderBy(col("chiffre_affaires").desc()) \
                .limit(10)
                
        elif analysis_type == "users":
            result = df.groupBy("user_id") \
                .agg(
                    count("*").alias("nombre_achats"),
                    sum("total_amount").alias("montant_total"),
                    avg("total_amount").alias("montant_moyen")
                ) \
                .orderBy(col("montant_total").desc()) \
                .limit(10)
        
        # Convertir en Pandas DataFrame
        pandas_df = result.toPandas()
        
        # Arrêter Spark
        spark.stop()
        
        return pandas_df
        
    except Exception as e:
        st.error(f"Erreur lors de l'analyse Spark: {e}")
        return None

# Fonction pour obtenir les statistiques MongoDB sans charger toutes les données
def get_mongo_stats():
    """Obtenir les statistiques de la base MongoDB"""
    client = get_mongo_connection()
    if client:
        try:
            db_name = os.getenv('MONGO_DB', 'retail')
            collection_name = os.getenv('MONGO_COLLECTION', 'sales')
            db = client[db_name]
            collection = db[collection_name]
            
            # Obtenir le nombre total de documents
            total_docs = collection.count_documents({})
            
            # Obtenir les statistiques d'agrégation
            pipeline = [
                {
                    '$group': {
                        '_id': None,
                        'total_revenue': {'$sum': '$total_amount'},
                        'avg_sale': {'$avg': '$total_amount'},
                        'unique_users': {'$addToSet': '$user_id'}
                    }
                }
            ]
            
            result = list(collection.aggregate(pipeline))
            if result:
                stats = result[0]
                return {
                    'total_docs': total_docs,
                    'total_revenue': stats['total_revenue'],
                    'avg_sale': stats['avg_sale'],
                    'unique_users': len(stats['unique_users'])
                }
        except Exception as e:
            st.error(f"Erreur lors de l'obtention des statistiques: {e}")
    
    return {
        'total_docs': 0,
        'total_revenue': 0,
        'avg_sale': 0,
        'unique_users': 0
    }

# Page Vue d'ensemble
if page == "📈 Vue d'ensemble":
    st.header("📈 Vue d'ensemble des ventes")
    
    # Obtenir les statistiques globales
    stats = get_mongo_stats()
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total des ventes", f"{stats['total_docs']:,}")
    
    with col2:
        st.metric("Chiffre d'affaires", f"${stats['total_revenue']:,.2f}")
    
    with col3:
        st.metric("Vente moyenne", f"${stats['avg_sale']:.2f}")
    
    with col4:
        st.metric("Clients uniques", f"{stats['unique_users']:,}")
    
    # Charger un échantillon de données pour les graphiques
    df = load_mongo_data(limit=1000)
    
    if not df.empty:
        # Graphiques
        col1, col2 = st.columns(2)
        
        with col1:
            # Ventes par catégorie
            category_sales = df.groupby('category')['total_amount'].sum().reset_index()
            fig_category = px.pie(
                category_sales, 
                values='total_amount', 
                names='category',
                title="Répartition des ventes par catégorie (échantillon)"
            )
            st.plotly_chart(fig_category, use_container_width=True)
        
        with col2:
            # Top 5 produits
            product_sales = df.groupby('product_name')['total_amount'].sum().sort_values(ascending=False).head(5)
            fig_products = px.bar(
                x=product_sales.values,
                y=product_sales.index,
                orientation='h',
                title="Top 5 des produits par chiffre d'affaires (échantillon)"
            )
            fig_products.update_layout(xaxis_title="Chiffre d'affaires ($)")
            st.plotly_chart(fig_products, use_container_width=True)
    else:
        st.warning("Impossible de charger les données pour les graphiques")

# Page Exploration des données
elif page == "🔍 Exploration des données":
    st.header("🔍 Exploration des données")
    
    # Sélectionner la taille de l'échantillon
    sample_size = st.slider("Taille de l'échantillon", min_value=100, max_value=10000, value=1000, step=100)
    
    df = load_mongo_data(limit=sample_size)
    
    if not df.empty:
        # Filtres
        st.subheader("Filtres")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            categories = ['Toutes'] + list(df['category'].unique())
            selected_category = st.selectbox("Catégorie", categories)
        
        with col2:
            min_amount = st.number_input("Montant minimum ($)", min_value=0.0, value=0.0)
        
        with col3:
            max_amount = st.number_input("Montant maximum ($)", min_value=0.0, value=float(df['total_amount'].max()))
        
        # Appliquer les filtres
        filtered_df = df.copy()
        if selected_category != 'Toutes':
            filtered_df = filtered_df[filtered_df['category'] == selected_category]
        filtered_df = filtered_df[
            (filtered_df['total_amount'] >= min_amount) & 
            (filtered_df['total_amount'] <= max_amount)
        ]
        
        # Afficher les données filtrées
        st.subheader(f"Données filtrées ({len(filtered_df)} ventes sur {len(df)} échantillon)")
        st.dataframe(filtered_df, use_container_width=True)
        
        # Statistiques descriptives
        st.subheader("Statistiques descriptives")
        st.dataframe(filtered_df.describe(), use_container_width=True)
    else:
        st.warning("Impossible de charger les données")

# Page Top Utilisateurs
elif page == "👥 Top Utilisateurs":
    st.header("👥 Top Utilisateurs")
    
    # Sélectionner la taille de l'échantillon
    sample_size = st.slider("Taille de l'échantillon", min_value=100, max_value=10000, value=1000, step=100)
    
    df = load_mongo_data(limit=sample_size)
    
    if not df.empty:
        # Top utilisateurs par montant dépensé
        user_totals = df.groupby('user_id').agg({
            'total_amount': ['sum', 'count', 'mean']
        }).round(2)
        user_totals.columns = ['Total dépensé', 'Nombre d\'achats', 'Montant moyen']
        user_totals = user_totals.sort_values('Total dépensé', ascending=False)
        
        st.subheader(f"Top utilisateurs par montant total dépensé (échantillon de {len(df)} ventes)")
        st.dataframe(user_totals, use_container_width=True)
        
        # Graphique des top utilisateurs
        top_users = user_totals.head(10)
        fig_users = px.bar(
            x=top_users.index,
            y=top_users['Total dépensé'],
            title="Top 10 des utilisateurs par montant dépensé (échantillon)"
        )
        fig_users.update_layout(xaxis_title="Utilisateur", yaxis_title="Montant total ($)")
        st.plotly_chart(fig_users, use_container_width=True)
    else:
        st.warning("Impossible de charger les données")

# Page Statistiques temporelles
elif page == "📅 Statistiques temporelles":
    st.header("📅 Statistiques temporelles")
    
    # Sélectionner la taille de l'échantillon
    sample_size = st.slider("Taille de l'échantillon", min_value=100, max_value=10000, value=1000, step=100)
    
    df = load_mongo_data(limit=sample_size)
    
    if not df.empty:
        # Convertir la colonne date
        df['sale_date'] = pd.to_datetime(df['sale_date'])
        
        # Ventes par jour
        daily_sales = df.groupby('sale_date').agg({
            'total_amount': ['sum', 'count']
        }).round(2)
        daily_sales.columns = ['Chiffre d\'affaires', 'Nombre de ventes']
        
        # Graphique temporel
        fig_temporal = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Chiffre d\'affaires quotidien', 'Nombre de ventes quotidien'),
            vertical_spacing=0.1
        )
        
        fig_temporal.add_trace(
            go.Scatter(x=daily_sales.index, y=daily_sales['Chiffre d\'affaires'], 
                      mode='lines+markers', name='CA quotidien'),
            row=1, col=1
        )
        
        fig_temporal.add_trace(
            go.Scatter(x=daily_sales.index, y=daily_sales['Nombre de ventes'], 
                      mode='lines+markers', name='Ventes quotidiennes'),
            row=2, col=1
        )
        
        fig_temporal.update_layout(height=600, title_text=f"Évolution temporelle des ventes (échantillon de {len(df)} ventes)")
        st.plotly_chart(fig_temporal, use_container_width=True)
    else:
        st.warning("Impossible de charger les données")

# Page Analyses Spark
elif page == "⚡ Analyses Spark":
    st.header("⚡ Analyses Spark - Traitement Distribué")
    
    if not SPARK_AVAILABLE:
        st.error("""
        ❌ **PySpark n'est pas disponible**
        
        Pour utiliser les fonctionnalités Spark, assurez-vous que :
        1. PySpark est installé dans l'environnement
        2. Le service Spark est démarré
        3. Les dépendances sont correctement configurées
        """)
        
        st.info("""
        **Solution :**
        - Vérifiez que le service `spark-processor` est en cours d'exécution
        - Redémarrez l'application avec `docker-compose restart app`
        - Consultez les logs pour plus d'informations
        """)
        
        # Afficher le statut des services
        st.subheader("🔍 Statut des Services")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("PySpark Disponible", "❌ Non")
        
        with col2:
            st.metric("Spark Master", "http://localhost:8085")
        
        st.stop()
    
    st.info("""
    Cette page utilise Apache Spark pour effectuer des analyses distribuées sur vos données.
    Spark permet de traiter de grandes quantités de données en parallèle sur plusieurs nœuds.
    """)
    
    # Sélection du type d'analyse
    analysis_type = st.selectbox(
        "Type d'analyse Spark",
        ["category", "products", "users"],
        format_func=lambda x: {
            "category": "📊 Analyse par catégorie",
            "products": "🏷️ Top produits",
            "users": "👥 Top utilisateurs"
        }[x]
    )
    
    # Taille de l'échantillon
    sample_size = st.slider("Taille de l'échantillon Spark", min_value=1000, max_value=50000, value=10000, step=1000)
    
    # Bouton pour exécuter l'analyse
    if st.button("🚀 Exécuter l'analyse Spark", type="primary"):
        with st.spinner("Exécution de l'analyse Spark en cours..."):
            result = run_spark_analysis(analysis_type, sample_size)
            
            if result is not None:
                st.success(f"✅ Analyse Spark terminée ! {len(result)} résultats obtenus.")
                
                # Afficher les résultats
                st.subheader("📊 Résultats de l'analyse Spark")
                st.dataframe(result, use_container_width=True)
                
                # Graphiques selon le type d'analyse
                if analysis_type == "category":
                    fig = px.bar(
                        result, 
                        x='category', 
                        y='chiffre_affaires',
                        title="Chiffre d'affaires par catégorie (Spark)",
                        color='nombre_ventes'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                elif analysis_type == "products":
                    fig = px.bar(
                        result, 
                        x='product_name', 
                        y='chiffre_affaires',
                        title="Top produits par chiffre d'affaires (Spark)",
                        color='category'
                    )
                    fig.update_xaxes(tickangle=45)
                    st.plotly_chart(fig, use_container_width=True)
                    
                elif analysis_type == "users":
                    fig = px.bar(
                        result, 
                        x='user_id', 
                        y='montant_total',
                        title="Top utilisateurs par montant total (Spark)",
                        color='nombre_achats'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Métriques de performance
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Nombre de résultats", len(result))
                with col2:
                    if 'chiffre_affaires' in result.columns:
                        total_revenue = result['chiffre_affaires'].sum()
                        st.metric("Chiffre d'affaires total", f"${total_revenue:,.2f}")
                with col3:
                    if 'montant_total' in result.columns:
                        total_amount = result['montant_total'].sum()
                        st.metric("Montant total", f"${total_amount:,.2f}")
            else:
                st.error("❌ Erreur lors de l'exécution de l'analyse Spark")
    
    # Informations sur Spark
    st.subheader("ℹ️ À propos d'Apache Spark")
    st.markdown("""
    **Apache Spark** est un moteur de traitement distribué pour le big data :
    
    - ⚡ **Performance** : Traitement en mémoire jusqu'à 100x plus rapide que MapReduce
    - 🔄 **Polyvalence** : Supporte SQL, streaming, machine learning, et graph processing
    - 📊 **DataFrames** : API de haut niveau pour la manipulation de données
    - 🎯 **Fault tolerance** : Gestion automatique des pannes
    - 🚀 **Scalabilité** : Traitement distribué sur plusieurs nœuds
    
    **Architecture actuelle :**
    - Master : namenode (Spark Master)
    - Workers : 4 nœuds avec 5G RAM total
    - Stockage : HDFS + MongoDB
    """)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        Architecture Traitement Distribué - Hadoop + Spark + Pig + MongoDB + Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
