# -*- coding: utf-8 -*-

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
auth = LoginManager()
auth.login_view = 'index.login'
