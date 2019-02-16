# -*- coding: utf-8 -*-

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from config import config

db = SQLAlchemy()
auth = LoginManager()
auth.login_view = 'index.login'

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    auth.init_app(app)
    config[config_name].init_app(app)

    register_blueprint(app)

    return app


def register_blueprint(app):
    from app.views.admin import bp as admin_bp
    app.register_blueprint(admin_bp)
    from app.views.index import bp as index_bp
    app.register_blueprint(index_bp)
