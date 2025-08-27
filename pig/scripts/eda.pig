-- Script Pig pour l'analyse exploratoire des données de ventes MongoDB enrichies
-- Chargement des données depuis HDFS

-- Charger les données de ventes depuis HDFS
-- Note: Les données MongoDB exportées contiennent des champs enrichis
raw_sales = LOAD 'hdfs://namenode:9000/data/raw/sales/' USING PigStorage(',') AS (
    sale_id:chararray,
    user_id:chararray,
    product_id:chararray,
    product_name:chararray,
    quantity:int,
    unit_price:double,
    total_amount:double,
    sale_date:chararray,
    category:chararray,
    store_id:chararray,
    payment_method:chararray,
    region:chararray,
    customer_age:int,
    customer_gender:chararray,
    discount_applied:boolean,
    discount_amount:double,
    shipping_cost:double,
    tax_amount:double,
    created_at:chararray,
    updated_at:chararray
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
    AVG(valid_sales.total_amount) AS avg_sale_amount,
    SUM(valid_sales.quantity) AS total_quantity_sold,
    AVG(valid_sales.quantity) AS avg_quantity_per_sale;

-- Afficher les statistiques par catégorie
DUMP category_stats;

-- Top 10 des utilisateurs par montant dépensé
by_user = GROUP valid_sales BY user_id;
user_totals = FOREACH by_user GENERATE 
    group AS user_id,
    SUM(valid_sales.total_amount) AS total_spent,
    COUNT(valid_sales) AS nb_purchases,
    AVG(valid_sales.total_amount) AS avg_purchase_amount,
    SUM(valid_sales.quantity) AS total_items_purchased;
top_users = ORDER user_totals BY total_spent DESC;

-- Afficher le top 10 des utilisateurs
DUMP top_users LIMIT 10;

-- Statistiques par région
by_region = GROUP valid_sales BY region;
region_stats = FOREACH by_region GENERATE 
    group AS region,
    COUNT(valid_sales) AS nb_sales,
    SUM(valid_sales.total_amount) AS total_revenue,
    AVG(valid_sales.total_amount) AS avg_sale_amount,
    COUNT(DISTINCT valid_sales.user_id) AS unique_customers;

-- Afficher les statistiques par région
DUMP region_stats;

-- Statistiques par méthode de paiement
by_payment = GROUP valid_sales BY payment_method;
payment_stats = FOREACH by_payment GENERATE 
    group AS payment_method,
    COUNT(valid_sales) AS nb_transactions,
    SUM(valid_sales.total_amount) AS total_amount,
    AVG(valid_sales.total_amount) AS avg_transaction_amount;

-- Afficher les statistiques par méthode de paiement
DUMP payment_stats;

-- Analyse démographique par âge
by_age_group = FOREACH valid_sales GENERATE 
    CASE 
        WHEN customer_age < 25 THEN '18-24'
        WHEN customer_age < 35 THEN '25-34'
        WHEN customer_age < 45 THEN '35-44'
        WHEN customer_age < 55 THEN '45-54'
        WHEN customer_age < 65 THEN '55-64'
        ELSE '65+'
    END AS age_group,
    total_amount,
    quantity,
    user_id;

age_group_stats = GROUP by_age_group BY age_group;
age_analysis = FOREACH age_group_stats GENERATE 
    group AS age_group,
    COUNT(by_age_group) AS nb_sales,
    SUM(by_age_group.total_amount) AS total_revenue,
    AVG(by_age_group.total_amount) AS avg_sale_amount,
    COUNT(DISTINCT by_age_group.user_id) AS unique_customers;

-- Afficher l'analyse par groupe d'âge
DUMP age_analysis;

-- Analyse par genre
by_gender = GROUP valid_sales BY customer_gender;
gender_stats = FOREACH by_gender GENERATE 
    group AS gender,
    COUNT(valid_sales) AS nb_sales,
    SUM(valid_sales.total_amount) AS total_revenue,
    AVG(valid_sales.total_amount) AS avg_sale_amount,
    COUNT(DISTINCT valid_sales.user_id) AS unique_customers;

-- Afficher les statistiques par genre
DUMP gender_stats;

-- Top 10 des magasins par performance
by_store = GROUP valid_sales BY store_id;
store_stats = FOREACH by_store GENERATE 
    group AS store_id,
    COUNT(valid_sales) AS nb_sales,
    SUM(valid_sales.total_amount) AS total_revenue,
    AVG(valid_sales.total_amount) AS avg_sale_amount,
    COUNT(DISTINCT valid_sales.user_id) AS unique_customers;
top_stores = ORDER store_stats BY total_revenue DESC;

-- Afficher le top 10 des magasins
DUMP top_stores LIMIT 10;

-- Analyse des remises
discount_analysis = GROUP valid_sales BY discount_applied;
discount_stats = FOREACH discount_analysis GENERATE 
    group AS discount_applied,
    COUNT(valid_sales) AS nb_sales,
    SUM(valid_sales.total_amount) AS total_revenue,
    SUM(valid_sales.discount_amount) AS total_discounts_given,
    AVG(valid_sales.discount_amount) AS avg_discount_amount;

-- Afficher l'analyse des remises
DUMP discount_stats;

-- Statistiques par jour
by_date = GROUP valid_sales BY sale_date;
daily_stats = FOREACH by_date GENERATE 
    group AS sale_date,
    COUNT(valid_sales) AS nb_sales,
    SUM(valid_sales.total_amount) AS daily_revenue,
    AVG(valid_sales.total_amount) AS avg_sale_amount,
    COUNT(DISTINCT valid_sales.user_id) AS unique_customers;

-- Sauvegarder les résultats dans HDFS
STORE category_stats INTO 'hdfs://namenode:9000/data/curated/sales/category_stats' USING PigStorage('\t');
STORE top_users INTO 'hdfs://namenode:9000/data/curated/sales/top_users' USING PigStorage('\t');
STORE region_stats INTO 'hdfs://namenode:9000/data/curated/sales/region_stats' USING PigStorage('\t');
STORE payment_stats INTO 'hdfs://namenode:9000/data/curated/sales/payment_stats' USING PigStorage('\t');
STORE age_analysis INTO 'hdfs://namenode:9000/data/curated/sales/age_analysis' USING PigStorage('\t');
STORE gender_stats INTO 'hdfs://namenode:9000/data/curated/sales/gender_stats' USING PigStorage('\t');
STORE top_stores INTO 'hdfs://namenode:9000/data/curated/sales/top_stores' USING PigStorage('\t');
STORE discount_stats INTO 'hdfs://namenode:9000/data/curated/sales/discount_stats' USING PigStorage('\t');
STORE daily_stats INTO 'hdfs://namenode:9000/data/curated/sales/daily_stats' USING PigStorage('\t');
