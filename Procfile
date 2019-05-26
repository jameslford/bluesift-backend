web: gunicorn config.wsgi --log-file -
worker: python manage.py celery worker --beat