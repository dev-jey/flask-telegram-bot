web: gunicorn run:app
worker: celery -A -E  application.celery_worker.celery worker -l info --pool=gevent --concurrency=1000