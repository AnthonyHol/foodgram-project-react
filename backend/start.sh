#!/bin/bash
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --no-input
python manage.py import_data
gunicorn foodgram.wsgi:application --bind 0:8000
