# -*- coding: utf-8 -*-

from app import db
from datetime import datetime


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    create_at = db.Column(db.DateTime, default=datetime.utcnow)
