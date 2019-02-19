# -*- coding: utf-8 -*-


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



class ProductionConfig(Config):
    pass


class TestingConfig(Config):
    pass


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
