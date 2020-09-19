from application import celery
from application.factory import create_app
from application.celery_config import init_celery

app=create_app()
init_celery(celery, app)