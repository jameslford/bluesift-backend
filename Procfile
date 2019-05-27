web: gunicorn config.wsgi --log-file -
worker: python manage.py celery -A config worker --beat -l info