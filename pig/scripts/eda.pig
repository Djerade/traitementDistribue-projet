-- Script Pig pour l'analyse exploratoire des données de ventes
-- Chargement des données depuis HDFS

-- Charger les données de ventes depuis HDFS
-- Note: Si les données sont en Parquet, utiliser ParquetLoader
-- Si en CSV, utiliser PigStorage
raw_sales = LOAD 'hdfs://namenode:9000/data/raw/sales/' USING PigStorage(',') AS (
    sale_id:chararray,
    user_id:chararray,
    product_id:chararray,
    quantity:int,
    unit_price:double,
    total_amount:double,
    sale_date:chararray,
    category:chararray
);

-- Filtrer les ventes valides (montant > 0)
valid_sales = FILTER raw_sales BY total_amount > 0;

-- Afficher un échantillon des données
DUMP valid_sales LIMIT 10;

-- Statistiques par catégorie
by_category = GROUP valid_sales BY category;
category_stats = FOREACH by_category GENERATE 
    group AS category,
    COUNT(valid_sales) AS nb_sales,
    SUM(valid_sales.total_amount) AS total_revenue,
    AVG(valid_sales.total_amount) AS avg_sale_amount;

-- Afficher les statistiques par catégorie
DUMP category_stats;

-- Top 10 des utilisateurs par montant dépensé
by_user = GROUP valid_sales BY user_id;
user_totals = FOREACH by_user GENERATE 
    group AS user_id,
    SUM(valid_sales.total_amount) AS total_spent,
    COUNT(valid_sales) AS nb_purchases;
top_users = ORDER user_totals BY total_spent DESC;

-- Afficher le top 10 des utilisateurs
DUMP top_users LIMIT 10;

-- Statistiques par jour
by_date = GROUP valid_sales BY sale_date;
daily_stats = FOREACH by_date GENERATE 
    group AS sale_date,
    COUNT(valid_sales) AS nb_sales,
    SUM(valid_sales.total_amount) AS daily_revenue;

-- Sauvegarder les résultats dans HDFS
STORE category_stats INTO 'hdfs://namenode:9000/data/curated/sales/category_stats' USING PigStorage('\t');
STORE top_users INTO 'hdfs://namenode:9000/data/curated/sales/top_users' USING PigStorage('\t');
STORE daily_stats INTO 'hdfs://namenode:9000/data/curated/sales/daily_stats' USING PigStorage('\t');
