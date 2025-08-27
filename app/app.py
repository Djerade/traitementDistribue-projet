import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pymongo
# from pyhive import hive  # Temporairement désactivé
import os
from datetime import datetime, timedelta

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
    ["📈 Vue d'ensemble", "🔍 Exploration des données", "👥 Top Utilisateurs", "📅 Statistiques temporelles"]
)

# Fonction pour charger les données depuis MongoDB
def load_mongo_data():
    """Charger les données depuis MongoDB"""
    client = get_mongo_connection()
    if client:
        # Utiliser les variables d'environnement si disponibles
        db_name = os.getenv('MONGO_DB', 'retail')
        collection_name = os.getenv('MONGO_COLLECTION', 'sales')
        db = client[db_name]
        collection = db[collection_name]
        data = list(collection.find({}, {'_id': 0}))
        return pd.DataFrame(data)
    return pd.DataFrame()

# Fonction pour charger les données depuis Hive
def load_hive_data(query):
    """Charger les données depuis Hive - Temporairement désactivé"""
    st.warning("Fonction Hive temporairement désactivée")
    return pd.DataFrame()

# Page Vue d'ensemble
if page == "📈 Vue d'ensemble":
    st.header("📈 Vue d'ensemble des ventes")
    
    # Charger les données
    df = load_mongo_data()
    
    if not df.empty:
        # Métriques principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total des ventes", f"{len(df):,}")
        
        with col2:
            total_revenue = df['total_amount'].sum()
            st.metric("Chiffre d'affaires", f"${total_revenue:,.2f}")
        
        with col3:
            avg_sale = df['total_amount'].mean()
            st.metric("Vente moyenne", f"${avg_sale:.2f}")
        
        with col4:
            unique_users = df['user_id'].nunique()
            st.metric("Clients uniques", f"{unique_users:,}")
        
        # Graphiques
        col1, col2 = st.columns(2)
        
        with col1:
            # Ventes par catégorie
            category_sales = df.groupby('category')['total_amount'].sum().reset_index()
            fig_category = px.pie(
                category_sales, 
                values='total_amount', 
                names='category',
                title="Répartition des ventes par catégorie"
            )
            st.plotly_chart(fig_category, use_container_width=True)
        
        with col2:
            # Top 5 produits
            product_sales = df.groupby('product_name')['total_amount'].sum().sort_values(ascending=False).head(5)
            fig_products = px.bar(
                x=product_sales.values,
                y=product_sales.index,
                orientation='h',
                title="Top 5 des produits par chiffre d'affaires"
            )
            fig_products.update_layout(xaxis_title="Chiffre d'affaires ($)")
            st.plotly_chart(fig_products, use_container_width=True)

# Page Exploration des données
elif page == "🔍 Exploration des données":
    st.header("🔍 Exploration des données")
    
    df = load_mongo_data()
    
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
        st.subheader(f"Données filtrées ({len(filtered_df)} ventes)")
        st.dataframe(filtered_df, use_container_width=True)
        
        # Statistiques descriptives
        st.subheader("Statistiques descriptives")
        st.dataframe(filtered_df.describe(), use_container_width=True)

# Page Top Utilisateurs
elif page == "👥 Top Utilisateurs":
    st.header("👥 Top Utilisateurs")
    
    df = load_mongo_data()
    
    if not df.empty:
        # Top utilisateurs par montant dépensé
        user_totals = df.groupby('user_id').agg({
            'total_amount': ['sum', 'count', 'mean']
        }).round(2)
        user_totals.columns = ['Total dépensé', 'Nombre d\'achats', 'Montant moyen']
        user_totals = user_totals.sort_values('Total dépensé', ascending=False)
        
        st.subheader("Top utilisateurs par montant total dépensé")
        st.dataframe(user_totals, use_container_width=True)
        
        # Graphique des top utilisateurs
        top_users = user_totals.head(10)
        fig_users = px.bar(
            x=top_users.index,
            y=top_users['Total dépensé'],
            title="Top 10 des utilisateurs par montant dépensé"
        )
        fig_users.update_layout(xaxis_title="Utilisateur", yaxis_title="Montant total ($)")
        st.plotly_chart(fig_users, use_container_width=True)

# Page Statistiques temporelles
elif page == "📅 Statistiques temporelles":
    st.header("📅 Statistiques temporelles")
    
    df = load_mongo_data()
    
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
        
        fig_temporal.update_layout(height=600, title_text="Évolution temporelle des ventes")
        st.plotly_chart(fig_temporal, use_container_width=True)

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
