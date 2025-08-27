// Script d'initialisation MongoDB avec des données de ventes d'exemple

// Créer la base de données retail
db = db.getSiblingDB('retail');

// Créer la collection sales
db.createCollection('sales');

// Insérer des données de ventes d'exemple
db.sales.insertMany([
    {
        sale_id: "S001",
        user_id: "U001",
        product_id: "P001",
        product_name: "Laptop Dell XPS",
        quantity: 1,
        unit_price: 1299.99,
        total_amount: 1299.99,
        sale_date: "2024-01-15",
        category: "Electronics"
    },
    {
        sale_id: "S002",
        user_id: "U002",
        product_id: "P002",
        product_name: "iPhone 15 Pro",
        quantity: 1,
        unit_price: 999.99,
        total_amount: 999.99,
        sale_date: "2024-01-16",
        category: "Electronics"
    },
    {
        sale_id: "S003",
        user_id: "U001",
        product_id: "P003",
        product_name: "Nike Air Max",
        quantity: 2,
        unit_price: 129.99,
        total_amount: 259.98,
        sale_date: "2024-01-17",
        category: "Sports"
    },
    {
        sale_id: "S004",
        user_id: "U003",
        product_id: "P004",
        product_name: "Samsung TV 55\"",
        quantity: 1,
        unit_price: 799.99,
        total_amount: 799.99,
        sale_date: "2024-01-18",
        category: "Electronics"
    },
    {
        sale_id: "S005",
        user_id: "U002",
        product_id: "P005",
        product_name: "Adidas T-Shirt",
        quantity: 3,
        unit_price: 29.99,
        total_amount: 89.97,
        sale_date: "2024-01-19",
        category: "Clothing"
    },
    {
        sale_id: "S006",
        user_id: "U004",
        product_id: "P006",
        product_name: "MacBook Pro M3",
        quantity: 1,
        unit_price: 1999.99,
        total_amount: 1999.99,
        sale_date: "2024-01-20",
        category: "Electronics"
    },
    {
        sale_id: "S007",
        user_id: "U001",
        product_id: "P007",
        product_name: "Basketball",
        quantity: 1,
        unit_price: 49.99,
        total_amount: 49.99,
        sale_date: "2024-01-21",
        category: "Sports"
    },
    {
        sale_id: "S008",
        user_id: "U003",
        product_id: "P008",
        product_name: "Levi's Jeans",
        quantity: 2,
        unit_price: 79.99,
        total_amount: 159.98,
        sale_date: "2024-01-22",
        category: "Clothing"
    },
    {
        sale_id: "S009",
        user_id: "U005",
        product_id: "P009",
        product_name: "Sony Headphones",
        quantity: 1,
        unit_price: 299.99,
        total_amount: 299.99,
        sale_date: "2024-01-23",
        category: "Electronics"
    },
    {
        sale_id: "S010",
        user_id: "U002",
        product_id: "P010",
        product_name: "Running Shoes",
        quantity: 1,
        unit_price: 89.99,
        total_amount: 89.99,
        sale_date: "2024-01-24",
        category: "Sports"
    }
]);

// Créer des index pour améliorer les performances
db.sales.createIndex({ "user_id": 1 });
db.sales.createIndex({ "category": 1 });
db.sales.createIndex({ "sale_date": 1 });

print("Base de données retail créée avec succès !");
print("Collection sales créée avec " + db.sales.countDocuments() + " documents.");
