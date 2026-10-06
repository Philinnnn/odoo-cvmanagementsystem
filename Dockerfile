FROM odoo:17

USER root

# Кастомные модули
COPY ./addons /mnt/extra-addons

# Свой стартовый скрипт
COPY ./start.sh /start.sh
RUN chmod +x /start.sh \
    && chown -R odoo:odoo /mnt/extra-addons

USER odoo

EXPOSE 8069

ENTRYPOINT ["/start.sh"]