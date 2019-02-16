# -*- coding: utf-8 -*-

from flask import Blueprint, request, render_template
from flask_login import login_required

from app import db
from app.models import Post

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/')
@login_required
def index():
    title = request.args.get('title', 'World')
    post = Post(title=title)
    db.session.add(post)
    db.session.commit()

    return render_template('admin/index.html')


@bp.route('/posts')
@login_required
def list_posts():
    return render_template('admin/index.html')


@bp.route('/posts/new')
@login_required
def new_post():
    return render_template('admin/index.html')


@bp.route('/pages')
@login_required
def list_pages():
    return render_template('admin/index.html')


@bp.route('/pages/new')
@login_required
def new_page():
    return render_template('admin/index.html')


@bp.route('/users')
@login_required
def list_users():
    return render_template('admin/index.html')


@bp.route('/users/new')
@login_required
def new_user():
    return render_template('admin/user.html')


@bp.route('/users/<user_id>/edit')
@login_required
def edit_user(user_id):
    return render_template('admin/user.html', user_id=user_id)
