sleep 3
python manage.py makemigrations
python manage.py migrate
python manage.py seed_db

python -m gunicorn --workers=4 --timeout 0 --preload --bind 0.0.0.0:8000 WEBWEBWEB.wsgi:application
