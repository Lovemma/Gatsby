# -*- coding: utf-8 -*-

from app import db
from app.models.base import BaseModel


class ReactItem(BaseModel):
    __tablename__ = 'react_items'

    post_id = db.Column(db.Integer)
    reaction_type = db.Column(db.Integer)
