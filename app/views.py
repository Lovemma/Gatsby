# -*- coding: utf-8 -*-

from flask import Blueprint, request, render_template

from . import db
from .models import Post

bp = Blueprint('views', __name__)


@bp.route('/')
def index():
    title = request.args.get('title', 'World')
    post = Post(title=title)
    db.session.add(post)
    db.session.commit()

    return render_template('index.html', post=post)
