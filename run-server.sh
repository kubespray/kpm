#!/bin/sh
PORT=${PORT:-5000}
storage="${STORAGE:-filesystem}"
echo $storage
DATABASE_URL="$HOME/.kpm/packages" APPR_DB_CLASS=$storage gunicorn kpm.api.wsgi:app -b :$PORT --timeout 120 -w 4 --reload
