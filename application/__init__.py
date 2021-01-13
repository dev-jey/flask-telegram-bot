from celery import Celery
from config import Config

def make_celery(app=__name__):
    redis_uri = Config.CELERY_BROKER_URL
    celery = Celery(
        app,
        backend=redis_uri,
        broker=redis_uri
    )
    return celery

celery = make_celery()