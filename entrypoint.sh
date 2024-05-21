#!/bin/bash

# Collect static files
#echo "Collecting static files"
#python manage.py collectstatic --noinput

# Apply database migrations
echo "Applying database migrations"
python manage.py makemigrations
python manage.py migrate

# Start Gunicorn or Daphne based on the command passed in
exec "$@"
