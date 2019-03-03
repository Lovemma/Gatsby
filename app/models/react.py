# -*- coding: utf-8 -*-

from app import db
from app.models.base import BaseModel
from .consts import K_COMMENT
from .mc import cache, clear_mc
from .signals import comment_reacted

MC_KEY_USER_REACT_STAT = 'react:stats:%s:%s'
MC_KEY_REACTION_ITEM_BY_USER_TARGET = 'react:reaction_item:%s:%s:%s'


class ReactItem(BaseModel):
    __tablename__ = 'react_items'

    target_id = db.Column(db.Integer)
    target_kind = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    reaction_type = db.Column(db.Integer)

    REACTION_KINDS = (
        K_UPVOTE,
        K_FUNNY,
        K_LOVE,
        K_SURPRISED,
        K_SAD
    ) = range(5)

    REACTION_MAP = {
        'upvote': K_UPVOTE,
        'funny': K_FUNNY,
        'love': K_LOVE,
        'surprised': K_SURPRISED,
        'sad': K_SAD
    }

    @classmethod
    def create(cls, **kwargs):
        obj = super().create(**kwargs)
        react_name = next((name for name, type in cls.REACTION_MAP.items()
                           if type == obj.reaction_type), None)
        stat = ReactStats.get_by_target(obj.target_id, obj.target_kind)
        field = f'{react_name}_count'
        setattr(stat, field, getattr(stat, field) + 1)
        stat.save()
        return obj

    @classmethod
    @cache(MC_KEY_REACTION_ITEM_BY_USER_TARGET % ('{user_id}', '{target_id}',
                                                  '{target_kind}'))
    def get_reaction_item(cls, user_id, target_id, target_kind):
        rv = cls.query.filter_by(user_id=user_id, target_id=target_id,
                                 target_kind=target_kind).first()
        return rv

    def delete(self):
        super().delete()
        stat = ReactStats.get_by_target(self.target_id, self.target_kind)
        react_name = next((name for name, type in self.REACTION_MAP.items()
                           if type == self.reaction_type), None)
        field = f'{react_name}_count'
        setattr(stat, field, getattr(stat, field) - 1)
        stat.save()

    def clear_mc(self):
        clear_mc(MC_KEY_REACTION_ITEM_BY_USER_TARGET % (
            self.user_id, self.target_id, self.target_kind))

        if self.target_kind == K_COMMENT:
            comment_reacted.send(user_id=self.user_id,
                                 comment_id=self.target_id)


class ReactStats(BaseModel):
    target_id = db.Column(db.Integer)
    target_kind = db.Column(db.Integer)
    upvote_count = db.Column(db.Integer, default=0)
    funny_count = db.Column(db.Integer, default=0)
    love_count = db.Column(db.Integer, default=0)
    surprised_count = db.Column(db.Integer, default=0)
    sad_count = db.Column(db.Integer, default=0)

    @classmethod
    @cache(MC_KEY_USER_REACT_STAT % ('{target_id}', '{target_kind}'))
    def get_by_target(cls, target_id, target_kind):
        rv = cls.query.filter_by(target_id=target_id,
                                 target_kind=target_kind).first()
        if not rv:
            rv = cls.create(target_id=target_id,
                            target_kind=target_kind)
        return rv

    def clear_mc(self):
        clear_mc(MC_KEY_USER_REACT_STAT % (
            self.target_id, self.target_kind))


class ReactMixin:
    def add_reaction(self, user_id, reaction_type):
        item = ReactItem.get_reaction_item(user_id, self.id, self.kind)
        if item and reaction_type == item.reaction_type:
            item.save()
            return True
        if not item:
            item = ReactItem.create(
                target_id=self.id, target_kind=self.kind,
                user_id=user_id, reaction_type=reaction_type)
        else:
            item.reaction_type = reaction_type
            item.save()

        return bool(item)

    def cancel_reaction(self, user_id):
        item = ReactItem.get_reaction_item(user_id, self.id, self.kind)
        if item:
            item.delete()
        return True

    @property
    def stats(self):
        return ReactStats.get_by_target(self.id, self.kind)

    def get_reaction_type(self, user_id):
        item = ReactItem.get_reaction_item(user_id, self.id, self.kind)
        return item.reaction_type if item else None
