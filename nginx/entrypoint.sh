#!/bin/sh
echo "Preparing Rapt Server..."

export API_URL="http://${SERVICE_NAME}:${SERVICE_PORT}"
# env

cp /app/nginx.conf.template /app/nginx.conf
# cat /app/nginx.conf

sed -i "s|SERVICEURL|${API_URL}|g" /app/nginx.conf
# cat /app/nginx.conf

cp /app/nginx.conf /etc/nginx/nginx.conf
# cat /etc/nginx/nginx.conf

nginx -s reload
nginx -g "daemon off;"