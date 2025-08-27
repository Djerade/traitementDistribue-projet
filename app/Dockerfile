FROM python:3.11-slim

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libsasl2-dev \
    libkrb5-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Répertoire de travail
WORKDIR /app

# Copie des fichiers de dépendances
COPY requirements.txt .


# Copie du code de l'application
COPY . .

# Exposition du port
EXPOSE 8501

# Commande de démarrage
ENTRYPOINT ["/bin/sh", "-c", "pip install --default-timeout=100 --no-cache-dir -r requirements.txt && exec streamlit run app.py --server.port 8501 --server.address 0.0.0.0"]
