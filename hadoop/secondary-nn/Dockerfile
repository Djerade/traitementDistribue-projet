FROM hadoop-base:latest

# Copie du script de démarrage
COPY start-secondary-nn.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/start-secondary-nn.sh

# Exposition des ports
EXPOSE 9868

# Commande de démarrage
CMD ["/usr/local/bin/start-secondary-nn.sh"]
