FROM hadoop-base:latest

# Copie du script de démarrage
COPY start-nn.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/start-nn.sh

# Exposition des ports
EXPOSE 9870 8088 7077 8080 10020 19888

# Commande de démarrage
CMD ["/usr/local/bin/start-nn.sh"]
