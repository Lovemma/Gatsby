# -*- coding: utf-8 -*-

from flask import Blueprint, render_template

from app.models import Post

bp = Blueprint('blog', __name__, url_prefix='/')


@bp.route('/')
def index():
    posts = Post.query.all()

    return render_template('index.html', posts=posts)


@bp.route('/post/<post_id>')
def post(post_id):
    post = Post.query.get(post_id).first_or_404()
    return render_template('index.html', post=post)
