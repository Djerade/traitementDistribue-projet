FROM hadoop-base:latest

# Copie des configurations Hadoop
COPY core-site.xml /opt/hadoop/etc/hadoop/
COPY hdfs-site.xml /opt/hadoop/etc/hadoop/
COPY yarn-site.xml /opt/hadoop/etc/hadoop/
COPY mapred-site.xml /opt/hadoop/etc/hadoop/

# Copie du script de démarrage
COPY datanode/start-dn.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/start-dn.sh

# Exposition des ports
EXPOSE 9864 8042 8081

# Commande de démarrage
CMD ["/usr/local/bin/start-dn.sh"]
