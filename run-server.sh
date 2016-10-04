#!/bin/bash
PORT=$1
gunicorn kpm.api.wsgi:app -b :$PORT --timeout 120 -w 4 --reload
