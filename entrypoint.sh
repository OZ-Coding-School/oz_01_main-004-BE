#!/bin/bash

# Collect static files
#echo "Collect static files"
#python manage.py collectstatic

# Apply database migrations
#echo "Apply database migrations"
#python manage.py makemigrations
#python manage.py migrate

# Start Gunicorn
echo "Starting Gunicorn"
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
