FROM hadoop-base:latest

# Copie du script de démarrage
COPY start-dn.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/start-dn.sh

# Exposition des ports
EXPOSE 9864 8042 8081

# Commande de démarrage
CMD ["/usr/local/bin/start-dn.sh"]
