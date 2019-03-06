# -*- coding: utf-8 -*-

import os


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost:3306/gatsby?charset=utf8'
    WTF_CSRF_SECRET_KEY = 'a random string'
    SECRET_KEY = 'a random string'
    REDIS_HOST = 'localhost'
    REDIS_PORT = 6379

    MEMCACHED_URL = ['127.0.0.1:11211']

    GITHUB_CLIENT_ID = ''
    GITHUB_CLIENT_SECRET = ''

    REDIRECT_URL = 'http://127.0.0.1:8000/oauth'

    REACT_PROMPT = '喜欢这篇文章吗? 记得给我留言或订阅哦'

    HERE = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(HERE, 'app/static/upload')

    SHOW_PROFILE = False
    SITE_NAV_MENUS = [('blog.index', '首页'), ('blog.archives', '归档'),
                      ('blog.tags', '标签'), ('blog.search', '搜索'),
                      ('index.feed', '订阅'), ('/page/aboutme', '关于我')]

    AUTHOR = 'COldish'
    SITE_TITLE = 'My Blog'


class ProductionConfig(Config):
    pass


class TestingConfig(Config):
    pass


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
