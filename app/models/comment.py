# -*- coding: utf-8 -*-

import mistune

from app import db
from app.models.base import BaseModel
from .mc import clear_mc, cache

markdown = mistune.Markdown()
MC_KEY_COMMENT_LIST = 'comment:%s:comment_list'
MC_KEY_N_COMMENTS = 'comment:%s:n_comments'


class Comment(BaseModel):
    __tablename__ = 'comments'

    github_id = db.Column(db.Integer)
    post_id = db.Column(db.Integer)
    reaction_type = db.Column(db.Integer)
    ref_id = db.Column(db.Integer)

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

    def set_content(self, content):
        return self.set_props_by_key('content', content)

    def save(self, *args, **kwargs):
        content = kwargs.pop('content', None)
        if content is not None:
            self.set_content(content)
        return super().save()

    def clear_mc(self):
        for key in (MC_KEY_N_COMMENTS, MC_KEY_COMMENT_LIST):
            clear_mc(key % self.post_id)


class CommentMixin:
    def add_comment(self, user_id, content, ref_id=0):
        obj = Comment.create(github_id=user_id, post_id=self.id,
                             ref_id=ref_id)
        obj.set_content(content)
        return True

    def del_comment(self, user_id, comment_id):
        c = Comment.query.get(comment_id)
        if c and c.github_id == user_id and c.post_id == self.id:
            c.delete()
            return True
        return False

    @property
    @cache(MC_KEY_COMMENT_LIST % ('{self.id}'))
    def comments(self):
        return Comment.query.filter_by(post_id=self.id).order_by(
            Comment.id.desc()).all()

    @property
    @cache(MC_KEY_N_COMMENTS % ('{self.id}'))
    def n_comments(self):
        return Comment.query.filter_by(post_id=self.id).count()
