# -*- coding: utf-8 -*-

from flask import Flask, Request as _Request
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy

from config import config

_app = Flask(__name__)
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
    _app.request_class = Request
    _app.config.from_object(config[config_name])

    db.init_app(_app)
    auth.init_app(_app)
    config[config_name].init_app(_app)

    register_blueprint(_app)

    return _app


def register_blueprint(app):
    from app.views.admin import bp as admin_bp
    app.register_blueprint(admin_bp)
    from app.views.index import bp as index_bp
    app.register_blueprint(index_bp)


from .filters import has_attr
