#!/usr/bin/env bash

# setup the django project
# create a virtual environment
python3 -m venv .venv
# activate the virtual environment
source .venv/bin/activate
# install the requirements
pip install -r requirements.txt
# create the database and run migrations
python manage.py makemigrations
python manage.py migrate
# create a superuser
python manage.py createsuperuser
# run the server
python manage.py runserver

# reset the database
python manage.py flush

uvicorn mainproject.asgi:application --host 0.0.0.0 --port 8000
