FROM postgres:13

# Variables d'environnement pour PostgreSQL
ENV POSTGRES_DB=metastore
ENV POSTGRES_USER=hive
ENV POSTGRES_PASSWORD=hive

# Copie du script d'initialisation
COPY init-metastore.sql /docker-entrypoint-initdb.d/

# Exposition du port
EXPOSE 5432
