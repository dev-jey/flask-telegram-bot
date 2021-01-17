"""Flask configuration variables."""
from os import environ, path
from dotenv import load_dotenv
from celery.utils.log import get_task_logger

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))


class Config:
    """Set Flask configuration from .env file."""

    # General Config
    SECRET_KEY = environ.get('SECRET_KEY')
    FLASK_APP = environ.get('FLASK_APP')
    FLASK_ENV = environ.get('FLASK_ENV')

    # Database
    SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL")
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email configurations
    MAIL_SERVER=environ.get('MAIL_SERVER')
    MAIL_PORT = environ.get('MAIL_PORT')
    MAIL_USERNAME = environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = environ.get('MAIL_PASSWORD')
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True

    #Background tasks
    CELERY_RESULT_BACKEND = environ.get('REDIS_URL')
    CELERY_BROKER_URL = environ.get('REDIS_URL')
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

    # CELERYBEAT_SCHEDULE = {
    # # Execute every x minutes.
    # 'run-start-task': {
    #     'task': 'send_messages',
    #     'schedule': crontab(minute=environ.get('TIME_MEASURE_SECONDS', '')),
    #     }
    # }
