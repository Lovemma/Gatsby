# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, BooleanField, IntegerField,
    SelectField
)
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password')
    active = BooleanField('Active')
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    slug = StringField('Slug')
    summary = StringField('Summary')
    can_comment = BooleanField('CanComment', default=True)
    author_id = IntegerField('AuthorId', default='',
                             validators=[DataRequired()])
    published = SelectField('Published', choices=[('on', 1), ('off', 0)],
                            default='on')
    submit = SubmitField('Submit')
