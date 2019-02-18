# -*- coding: utf-8 -*-

from sqlalchemy import or_

from app import db
from app.models.base import BaseModel


class Post(BaseModel):
    __tablename__ = 'posts'

    title = db.Column(db.String(length=100), unique=True)
    author_id = db.Column(db.Integer)
    slug = db.Column(db.String(length=100))
    summary = db.Column(db.String(length=255))
    can_comment = db.Column(db.Boolean, default=True)
    published = db.Column(db.Boolean, default=False)

    @classmethod
    def create(cls, **kwargs):
        tags = kwargs.pop('tags', [])
        obj = super().create(**kwargs)
        if tags:
            PostTag.update_multi(obj.id, tags)
        return obj

    def update_tags(self, tagnames):
        if tagnames:
            PostTag.update_multi(self.id, tagnames)
        return True

    @property
    def tags(self):
        pts = PostTag.query.filter_by(post_id=self.id).all()
        if not pts:
            return []
        ids = [pt.tag_id for pt in pts]
        return Tag.query.filter(Tag.id.in_(ids)).all()

    @property
    def author(self):
        from app.models import User
        return User.query.get(self.author_id)

    def preview_url(self):
        return f'/{self.__class__.__name__.lower()}/{self.id}/preview'


class Tag(BaseModel):
    __tablename__ = 'tags'

    name = db.Column(db.String(length=100), unique=True)

    @classmethod
    def get_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def create(cls, **kwargs):
        name = kwargs.pop('name')
        kwargs['name'] = name.lower()
        return super().create(**kwargs)


class PostTag(BaseModel):
    __tablename__ = 'post_tags'

    post_id = db.Column(db.Integer)
    tag_id = db.Column(db.Integer)

    @classmethod
    def update_multi(cls, post_id, tags):
        tags = set(tags)
        origin_tags = set([t.name for t in Post.query.get(post_id).tags])

        need_add = tags - origin_tags
        need_del = origin_tags - tags
        need_add_tag_ids = set()
        need_del_tag_ids = set()
        for tag_name in need_add:
            tag, _ = Tag.get_or_create(name=tag_name)
            need_add_tag_ids.add(tag.id)
        for tag_name in need_del:
            tag, _ = Tag.get_or_create(name=tag_name)
            need_del_tag_ids.add(tag.id)

        if need_del_tag_ids:
            cls.query.filter(cls.post_id == post_id,
                             cls.tag_id.in_(need_del_tag_ids)).delete(synchronize_session=False)
            db.session.commit()
        for tag_id in need_add_tag_ids:
            PostTag.get_or_create(post_id=post_id, tag_id=tag_id)
