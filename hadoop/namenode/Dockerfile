FROM hadoop-base:latest

# Copie des configurations Hadoop
COPY core-site.xml /opt/hadoop/etc/hadoop/
COPY hdfs-site.xml /opt/hadoop/etc/hadoop/
COPY yarn-site.xml /opt/hadoop/etc/hadoop/
COPY mapred-site.xml /opt/hadoop/etc/hadoop/

# Copie du script de démarrage
COPY namenode/start-nn.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/start-nn.sh

# Exposition des ports
EXPOSE 9870 8088 7077 8080 10020 19888

# Commande de démarrage
CMD ["/usr/local/bin/start-nn.sh"]
