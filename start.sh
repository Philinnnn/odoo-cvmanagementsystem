#!/bin/sh
set -e

exec odoo \
  --db_host="$PGHOST" \
  --db_port="${PGPORT:-5432}" \
  --db_user="$ODOO_DB_USER" \
  --db_password="$ODOO_DB_PASSWORD" \
  --http-port="${PORT:-8069}" \
  --addons-path=/mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons \
  --proxy-mode \
  --without-demo=all