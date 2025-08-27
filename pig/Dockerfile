FROM openjdk:11-jre-slim

# Variables d'environnement
ARG PIG_VER=0.17.0

# Installation des dépendances
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Téléchargement et installation de Pig
RUN curl -L https://archive.apache.org/dist/pig/pig-${PIG_VER}/pig-${PIG_VER}.tar.gz \
    | tar -xz -C /opt && mv /opt/pig-${PIG_VER} /opt/pig

# Configuration des variables d'environnement
ENV PIG_HOME=/opt/pig
ENV PATH=$PATH:/opt/pig/bin
ENV JAVA_HOME=/usr/local/openjdk-11

# Création de l'utilisateur hadoop
RUN groupadd -r hadoop && useradd -r -g hadoop hadoop

# Copie des configurations Hadoop
COPY hadoop/core-site.xml /opt/pig/conf/
COPY hadoop/hdfs-site.xml /opt/pig/conf/
COPY hadoop/yarn-site.xml /opt/pig/conf/
COPY hadoop/mapred-site.xml /opt/pig/conf/

# Configuration de Pig pour utiliser YARN
RUN echo "mapreduce.framework.name=yarn" >> /opt/pig/conf/pig.properties && \
    echo "fs.defaultFS=hdfs://namenode:9000" >> /opt/pig/conf/pig.properties

# Répertoire de travail
WORKDIR /scripts

# Utilisateur par défaut
USER hadoop
