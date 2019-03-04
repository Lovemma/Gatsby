# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm as _FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import (
    StringField, PasswordField, SubmitField, BooleanField, SelectField,
    SelectMultipleField, TextAreaField
)
from wtforms.compat import iteritems
from wtforms.validators import DataRequired


class SwitchField(SelectField):
    ...


class FlaskForm(_FlaskForm):
    def validate(self, extra_validators=None):
        """
        Validates the form by calling `validate` on each field.

        :param extra_validators:
            If provided, is a dict mapping field names to a sequence of
            callables which will be passed as extra validators to the field's
            `validate` method.

        Returns `True` if no errors occur.
        """
        self._errors = None
        success = True
        for name, field in iteritems(self._fields):
            if field.type in ('SelectField', 'SelectMultipleField'):
                continue

            if extra_validators is not None and name in extra_validators:
                extra = extra_validators[name]
            else:
                extra = tuple()
            if not field.validate(self, extra):
                success = False
        return success


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
    content = TextAreaField('Content', default='')
    can_comment = BooleanField('CanComment', default=True)
    tags = SelectMultipleField('Tags', default=[])
    author_id = SelectField('AuthorId', default='',
                            validators=[DataRequired()])
    published = SwitchField('Published', choices=[('on', 1), ('off', 0)],
                            default='on')
    submit = SubmitField('Submit')


class ProfileForm(FlaskForm):
    avatar = FileField('Avatar', validators=[
        FileRequired(), FileAllowed('bmp gif jpg jpeg png'.split())])
    avatar_path = StringField('AvatarPath', default='')
    intro = StringField('Intro', default='')
    github_url = StringField('Github URL', default='')
    linkedin_url = StringField('Linkedin URL', default='')
    submit = SubmitField('Submit')
