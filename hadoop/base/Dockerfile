FROM openjdk:11-jre-slim

# Variables d'environnement
ARG HADOOP_VER=3.3.6
ARG SPARK_VER=3.5.1

# Installation des dépendances
RUN apt-get update && apt-get install -y \
    curl \
    python3 \
    procps \
    wget \
    ssh \
    pdsh \
    && rm -rf /var/lib/apt/lists/*

# Téléchargement et installation de Hadoop
RUN curl -L https://archive.apache.org/dist/hadoop/common/hadoop-${HADOOP_VER}/hadoop-${HADOOP_VER}.tar.gz \
    | tar -xz -C /opt && mv /opt/hadoop-${HADOOP_VER} /opt/hadoop

# Téléchargement et installation de Spark
RUN curl -L https://archive.apache.org/dist/spark/spark-${SPARK_VER}/spark-${SPARK_VER}-bin-hadoop3.tgz \
    | tar -xz -C /opt && mv /opt/spark-${SPARK_VER}-bin-hadoop3 /opt/spark

# Configuration des variables d'environnement
ENV HADOOP_HOME=/opt/hadoop
ENV SPARK_HOME=/opt/spark
ENV PATH=$PATH:/opt/hadoop/bin:/opt/hadoop/sbin:/opt/spark/bin
ENV JAVA_HOME=/usr/local/openjdk-11

# Création des utilisateurs
RUN groupadd -r hadoop && useradd -r -g hadoop hadoop
RUN groupadd -r spark && useradd -r -g spark spark

# Configuration SSH pour Hadoop
RUN mkdir -p /home/hadoop/.ssh && \
    ssh-keygen -t rsa -P '' -f /home/hadoop/.ssh/id_rsa && \
    cat /home/hadoop/.ssh/id_rsa.pub >> /home/hadoop/.ssh/authorized_keys && \
    chmod 0600 /home/hadoop/.ssh/authorized_keys && \
    chown -R hadoop:hadoop /home/hadoop/.ssh

# Création des répertoires pour les configurations
RUN mkdir -p /opt/connectors

# Création des répertoires nécessaires
RUN mkdir -p /hadoop/dfs/name /hadoop/dfs/data /tmp/hadoop-yarn /tmp/hadoop-yarn/staging && \
    chown -R hadoop:hadoop /hadoop /tmp/hadoop-yarn

# Configuration des permissions
RUN chown -R hadoop:hadoop /opt/hadoop && \
    chown -R spark:spark /opt/spark

WORKDIR /opt/hadoop
