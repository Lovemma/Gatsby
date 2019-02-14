# -*- coding: utf-8 -*-

from app import db

from app.models.base import BaseModel


class Comment(BaseModel):
    __tablename__ = 'comments'

    github_id = db.Column(db.Integer)
    post_id = db.Column(db.Integer)
    reaction_type = db.Column(db.Integer)
    ref_id = db.Column(db.Integer)
