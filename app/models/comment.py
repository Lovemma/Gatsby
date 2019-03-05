# -*- coding: utf-8 -*-

import mistune

from app.extenions import db
from app.models.base import BaseModel
from .consts import K_COMMENT, ONE_HOUR
from .mc import clear_mc, cache
from .react import ReactMixin, ReactItem
from .signals import comment_reacted
from .user import GithubUser

markdown = mistune.Markdown()
MC_KEY_COMMENT_LIST = 'comment:%s:comment_list'
MC_KEY_N_COMMENTS = 'comment:%s:n_comments'
MC_KEY_COMMENT_IDS_LIKED_BY_USER = 'react:comment_ids_liked_by:%s:%s'


class Comment(ReactMixin, BaseModel):
    __tablename__ = 'comments'

    github_id = db.Column(db.Integer)
    post_id = db.Column(db.Integer)
    reaction_type = db.Column(db.Integer)
    ref_id = db.Column(db.Integer)
    kind = K_COMMENT

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
    def user(self):
        return GithubUser.query.filter_by(gid=self.github_id).first()

    @property
    def n_likes(self):
        return self.stats.love_count

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
        return obj

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

    @cache(MC_KEY_COMMENT_IDS_LIKED_BY_USER % (
            '{user_id}', '{self.id}'), ONE_HOUR)
    def comment_ids_liked_by(self, user_id):
        cids = [c.id for c in self.comments]
        if not cids:
            return []
        queryset = ReactItem.query.filter(
            ReactItem.user_id == user_id, ReactItem.target_id.in_(cids),
            ReactItem.target_kind == K_COMMENT).all()
        return [item.target_id for item in queryset]


@comment_reacted.connect
def update_comment_list_cache(_, user_id, comment_id):
    comment = Comment.cache(comment_id)
    if comment:
        clear_mc(MC_KEY_COMMENT_LIST % comment.post_id)
        clear_mc(MC_KEY_COMMENT_IDS_LIKED_BY_USER % (
            user_id, comment.post_id))
