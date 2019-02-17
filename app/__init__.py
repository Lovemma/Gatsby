# -*- coding: utf-8 -*-

from flask import Flask, Request as _Request
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy

from config import config

db = SQLAlchemy()
auth = LoginManager()
auth.login_view = 'index.login'


class Request(_Request):
    @property
    def user(self):
        return current_user

    @property
    def user_id(self):
        return self.user.id if self.user else 0


def create_app(config_name='default'):
    app = Flask(__name__)
    app.request_class = Request
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
