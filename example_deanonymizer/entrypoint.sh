#!/bin/bash

# Argument validation check
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <module_name>"
    exit 1
fi

MODULE_NAME=${1}

# run gunicorn in the background but still keep its stdout/stderr visible
gunicorn --bind=127.0.0.1:8000 ${MODULE_NAME} 2>&1 &

# Remove interfering default configuration
rm -f /etc/nginx/sites-enabled/default
# forward logs to docker log collector (see https://serverfault.com/a/634296)
ln -sf /dev/stdout /var/log/nginx/access.log
ln -sf /dev/stderr /var/log/nginx/error.log

nginx -g 'daemon off;'
