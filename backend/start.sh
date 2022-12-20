#!/bin/bash
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py collectstatic --no-input
python3 manage.py import_data
gunicorn foodgram.wsgi:application --bind 0:8000
