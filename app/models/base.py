# -*- coding: utf-8 -*-

from app import db
from datetime import datetime


class BaseModel(db.Model):
    __abstract__ = True

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

    def url(self):
        return f'/{self.__class__.__name__.lower()}/{self.id}/'
