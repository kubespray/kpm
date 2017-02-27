#!/bin/sh
PORT=${PORT:-5000}
storage="${STORAGE:-filesystem}"
echo $storage
db_class=cnr.models.kv.$storage.db:CnrDB
blob_class=cnr.models.kv.$storage.blob:Blob
echo $db_class
DATABASE_URL="$HOME/.kpm/packages" CNR_DB_CLASS=$db_class CNR_BLOB_CLASS=$blob_class gunicorn kpm.api.wsgi:app -b :$PORT --timeout 120 -w 4 --reload
