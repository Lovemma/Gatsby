# -*- coding: utf-8 -*-

from pathlib import Path

import redis
from flask import Flask, Request as _Request
from flask_login import current_user
from werkzeug.contrib.cache import MemcachedCache
from werkzeug.local import LocalProxy, LocalStack

from config import config
from .extenions import db, auth
from .views.utils import register_blueprint

_context_stack = LocalStack()


def get_context():
    top = _context_stack.top
    if top is None:
        raise RuntimeError()
    return top


context = LocalProxy(get_context)
client = None
_redis = None


class Request(_Request):
    @property
    def user(self):
        return current_user

    @property
    def user_id(self):
        return self.user.id if self.user else 0


def setup_jinja2_environment(app):
    app.jinja_env.globals['REACT_PROMPT'] = app.config.get('REACT_PROMPT')
    from .models import ReactItem
    app.jinja_env.globals['ReactItem'] = ReactItem
    from .models.consts import K_POST
    app.jinja_env.globals['K_POST'] = K_POST
    app.jinja_env.globals['SITE_NAV_MENUS'] = app.config.get('SITE_NAV_MENUS')


def create_app(config_name='default'):
    app = Flask(__name__)
    app.request_class = Request
    app.config.from_object(config[config_name])

    db.init_app(app)
    auth.init_app(app)
    config[config_name].init_app(app)

    register_blueprint('app.views', app)
    setup_jinja2_environment(app)

    return app


app = create_app()


@app.before_first_request
def setup():
    global client
    client = MemcachedCache(servers=app.config.get('MEMCACHED_URL'))
    Path(app.config.get('UPLOAD_FOLDER')).mkdir(parents=True, exist_ok=True)


@app.before_request
def setup_context():
    host = app.config.get('REDIS_HOST', 'localhost')
    port = app.config.get('REDIS_PORT', 6379)
    global _redis
    if _redis is None:
        pool = redis.ConnectionPool(host=host, port=port,
                                    max_connections=10)
        _redis = redis.Redis(connection_pool=pool)
    context = {
        'redis': _redis,
        'memcached': client
    }
    _context_stack.push(context)


@app.after_request
def teardown(response):
    _context_stack.pop()
    return response


from .filters import has_attr, get_attr
