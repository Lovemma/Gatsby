# -*- coding: utf-8 -*-

import redis
from flask import Flask, Request as _Request
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.contrib.cache import MemcachedCache
from werkzeug.local import LocalProxy, LocalStack

from config import config

_app = Flask(__name__)
db = SQLAlchemy()
auth = LoginManager()
auth.login_view = 'index.login'

_context_stack = LocalStack()


def get_context():
    top = _context_stack.top
    if top is None:
        raise RuntimeError()
    return top


context = LocalProxy(get_context)
client = None


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
    from app.views.api import bp as api_bp
    app.register_blueprint(api_bp)
    from app.views.blog import bp as blog_bp
    app.register_blueprint(blog_bp)


@_app.before_first_request
def setup():
    global client
    client = MemcachedCache(servers=_app.config.get('MEMCACHED_URL'))


@_app.before_request
def setup_context():
    host = _app.config.get('REDIS_HOST', 'localhost')
    port = _app.config.get('REDIS_PORT', 6379)
    pool = redis.ConnectionPool(host=host, port=port,
                                max_connections=10)
    _redis = redis.Redis(connection_pool=pool)
    context = {
        'redis': _redis,
        'memcached': client
    }
    _context_stack.push(context)


@_app.after_request
def teardown(response):
    _context_stack.pop()
    return response


from .filters import has_attr
