-- Script d'initialisation pour Hive Metastore
-- Ce script sera exécuté automatiquement lors du premier démarrage

-- Création de la base de données metastore (déjà créée par les variables d'environnement)
-- Les tables seront créées automatiquement par Hive lors de la première connexion

-- Vérification que la base existe
SELECT current_database();
