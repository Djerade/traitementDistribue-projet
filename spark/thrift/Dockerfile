FROM hadoop-base:latest

# Copie du script de démarrage
COPY start-thrift.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/start-thrift.sh

# Exposition des ports
EXPOSE 10000

# Commande de démarrage
CMD ["/usr/local/bin/start-thrift.sh"]
