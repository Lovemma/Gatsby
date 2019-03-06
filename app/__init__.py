# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from pathlib import Path

import redis
from flask import Flask, Request as _Request, Response, render_template
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
    app.jinja_env.globals['SHOW_PROFILE'] = app.config.get('SHOW_PROFILE')


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


from app.models import Post, Tag


def _sitemap():
    ten_days_ago = (datetime.now() - timedelta(days=10)).date().isoformat()
    posts = Post.query.filter_by(status=Post.STATUS_ONLINE).order_by(
        Post.id.desc()).all()
    tags = Tag.query.order_by(Tag.id.desc()).all()
    items = []

    for rv in [posts, tags]:
        items.extend([(item.url, item.created_at) for item in rv])

    for route in app.url_map.iter_rules():
        if any(endpoint in route.rule for endpoint in ('/admin', '/j', '/api')):
            continue
        if 'GET' in route.methods and not route.arguments:
            items.append([route.rule, ten_days_ago])

    return render_template('sitemap.xml', items=items)


@app.route('/sitemap.xml')
def sitemap():
    return Response(_sitemap(), content_type='text/xml')


from .filters import has_attr, get_attr
