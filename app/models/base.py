# -*- coding: utf-8 -*-

from datetime import datetime

from app import db, context


class BaseModel(db.Model):
    __abstract__ = True

    _redis = None

    id = db.Column(db.Integer, primary_key=True)
    create_at = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance

    def save(self):
        db.session.add(self)
        db.session.commit()

    @property
    def url(self):
        return f'/{self.__class__.__name__.lower()}/{self.id}/'

    @classmethod
    def get_or_create(cls, **kwargs):
        instance = cls.query.filter_by(**kwargs).first()
        if instance:
            return instance, False
        return cls.create(**kwargs), True

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @property
    def redis(self):
        if self._redis is None:
            redis = context.get('redis')
            self._redis = redis
        return self._redis

    def get_db_key(self, key):
        return f'{self.__class__.__name__}/{self.id}/props/{key}'

    def set_props_by_key(self, key, value):
        key = self.get_db_key(key)
        return self.redis.set(key, value)

    def get_props_by_key(self, key):
        key = self.get_db_key(key)
        return self.redis.get(key) or b''
