# -*- coding: utf-8 -*-

from datetime import datetime

from app import context
from app.extenions import db
from .mc import cache, clear_mc

MC_KEY_ITEM_BY_ID = '%s:%s'


class BaseModel(db.Model):
    __abstract__ = True

    _redis = None

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def url(self):
        return f'/{self.__class__.__name__.lower()}/{self.id}/'

    @property
    def redis(self):
        if self._redis is None:
            redis = context.get('redis')
            self._redis = redis
        return self._redis

    @classmethod
    def get_or_create(cls, **kwargs):
        instance = cls.query.filter_by(**kwargs).first()
        if instance:
            return instance, False
        return cls.create(**kwargs), True

    def get_db_key(self, key):
        return f'{self.__class__.__name__}/{self.id}/props/{key}'

    def set_props_by_key(self, key, value):
        key = self.get_db_key(key)
        return self.redis.set(key, value)

    def get_props_by_key(self, key):
        key = self.get_db_key(key)
        return self.redis.get(key) or b''

    @classmethod
    @cache(MC_KEY_ITEM_BY_ID % ('{cls.__name__}', '{id}'))
    def cache(cls, id):
        return cls.query.get(id)

    @classmethod
    def get_multi(cls, ids):
        return [cls.cache(id) for id in ids]

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        db.session.add(instance)
        db.session.commit()
        cls.__flush__(instance)
        return instance

    def save(self):
        db.session.add(self)
        db.session.commit()
        self.__flush__(self)

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        self.__flush__(self)

    @classmethod
    def __flush__(cls, target):
        clear_mc(MC_KEY_ITEM_BY_ID % (target.__class__.__name__, target.id))
        target.clear_mc()

    def clear_mc(self):
        ...
