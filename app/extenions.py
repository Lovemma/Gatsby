# -*- coding: utf-8 -*-

from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from .config import SENTRY_DSN

db = SQLAlchemy()
auth = LoginManager()
auth.login_view = 'index.login'

if SENTRY_DSN:
    from raven.contrib.flask import Sentry

    sentry = Sentry()
else:
    sentry = None
