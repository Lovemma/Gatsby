# -*- coding: utf-8 -*-

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import config

db = SQLAlchemy()


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    db.init_app(app)
    config[config_name].init_app(app)

    register_blueprint(app)

    return app


def register_blueprint(app):
    from .views import bp
    app.register_blueprint(bp)
