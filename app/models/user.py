# -*- coding: utf-8 -*-

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, auth
from .base import BaseModel


class User(BaseModel, UserMixin):
    __tablename__ = 'users'

    intro = db.Column(db.String(length=100), default='')
    email = db.Column(db.String(length=100))
    name = db.Column(db.String(length=100), unique=True)
    password = db.Column(db.Text)
    github_url = db.Column(db.String(length=100), default='')
    active = db.Column(db.Boolean, default=True)


def generate_password(password):
    return generate_password_hash(
        password, method='pbkdf2:sha256')


def create_user(**data):
    if 'name' not in data or 'password' not in data:
        raise ValueError('Username or password are required.')
    data['password'] = generate_password_hash(
        password=data.pop('password'),
        method='pbkdf2:sha256'
    )
    user = User(**data)
    db.session.add(user)
    db.session.commit()
    return user


def validate_login(name, password):
    user = User.query.filter_by(name=name).first()
    if not user:
        return False, None
    if check_password_hash(user.password, password):
        return True, user
    return False, user


@auth.user_loader
def load_user(user_id):
    return User.query.get(user_id)