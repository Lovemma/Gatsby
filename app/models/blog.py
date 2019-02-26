# -*- coding: utf-8 -*-

from html.parser import HTMLParser

import mistune

from app import db
from app.models.base import BaseModel
from .comment import CommentMixin
from .mc import cache, clear_mc
from .utils import trunc_utf8

MC_KEY_TAGS_BY_POST_ID = 'post:%s:tags'
markdown = mistune.Markdown()


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


class Post(BaseModel, CommentMixin):
    __tablename__ = 'posts'

    STATUSES = (
        STATUS_UNPUBLISHED,
        STATUS_ONLINE
    ) = [False, True]

    title = db.Column(db.String(length=100), unique=True)
    author_id = db.Column(db.Integer)
    slug = db.Column(db.String(length=100))
    summary = db.Column(db.String(length=255))
    can_comment = db.Column(db.Boolean, default=True)
    published = db.Column(db.Boolean, default=STATUSES)

    @classmethod
    def create(cls, **kwargs):
        tags = kwargs.pop('tags', [])
        content = kwargs.pop('content')
        obj = super().create(**kwargs)
        if tags:
            PostTag.update_multi(obj.id, tags)
        obj.set_content(content)
        return obj

    def update_tags(self, tagnames):
        if tagnames:
            PostTag.update_multi(self.id, tagnames)
        return True

    @property
    @cache(MC_KEY_TAGS_BY_POST_ID % ('{self.id}'))
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

    def set_content(self, content):
        return self.set_props_by_key('content', content)

    def save(self, **kwargs):
        content = kwargs.pop('content', None)
        if content is not None:
            self.set_content(content)
        return super().save()

    @property
    def content(self):
        rv = self.get_props_by_key('content')
        if rv:
            return rv.decode('utf-8')

    @property
    def html_content(self):
        content = self.content
        if not content:
            return ''
        return markdown(content)

    @property
    def excerpt(self):
        if self.summary:
            return self.summary
        s = MLStripper()
        s.feed(self.html_content)
        return trunc_utf8(s.get_data(), 100)


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
                             cls.tag_id.in_(need_del_tag_ids)).delete(
                synchronize_session=False)
            db.session.commit()
        for tag_id in need_add_tag_ids:
            PostTag.get_or_create(post_id=post_id, tag_id=tag_id)

        clear_mc(MC_KEY_TAGS_BY_POST_ID % post_id)
