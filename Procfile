web: gunicorn config.wsgi --log-file -
worker: celery -A config worker --beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler