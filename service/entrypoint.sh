#!/bin/sh
cd /service/

# List all environment variables
echo "----------LISTING ALL ENVIRONMENT VARIABLES----------"
env

# Wait for the MySQL server to start
while ! mysqladmin ping -h"$MYSQL_HOST" -P"$MYSQL_PORT" --silent; do
    sleep 1
done

# Wait for the MySQL server to be ready
until mysql -h"$MYSQL_HOST" -P"$MYSQL_PORT" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e 'SELECT 1'; do
    sleep 1
done
echo "----------DATABASE CONNECTION SUCCESSFUL----------"

# create database if it does not exist
until mysql -h"$MYSQL_HOST" -P"$MYSQL_PORT" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "CREATE DATABASE IF NOT EXISTS ${MYSQL_DATABASE};"; do
    sleep 1
done
echo "----------DATABASE CREATED------------------------"

echo "----------APPYING DATABASE MIGRATIONS-------------"
python -m alembic upgrade head

echo "----------INITIALIZE DATABASE------------------"
python init.py

echo "------STARTING GUNICORN AT 0.0.0.0:${SERVICE_PORT}--"
uvicorn main:app --host 0.0.0.0 --port "$SERVICE_PORT" --workers 4 --reload