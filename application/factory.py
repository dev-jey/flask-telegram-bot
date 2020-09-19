from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from celery import Celery
from config import Config
from .celery_config import init_celery

db = SQLAlchemy()



def create_app(app_name = __name__, **kwargs):
    """Construct the core application."""
    app = Flask(app_name, instance_relative_config=False)
    if kwargs.get("celery"):
        init_celery(kwargs.get("celery"),app)
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config.from_object('config.Config')
    db.init_app(app)

    with app.app_context():
        from . import routes  # Import routes
        db.create_all()  # Create sql tables for our data models

        return app


