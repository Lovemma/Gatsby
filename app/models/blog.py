# -*- coding: utf-8 -*-

from app import db
from app.models.base import BaseModel


class Post(BaseModel):
    __tablename__ = 'posts'

    title = db.Column(db.Text)


class Tag(BaseModel):
    __tablename__ = 'tags'

    name = db.Column(db.Text)


class PostTag(BaseModel):
    __tablename__ = 'post_tags'

    post_id = db.Column(db.Integer)
    tag_id = db.Column(db.Integer)
