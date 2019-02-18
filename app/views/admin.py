# -*- coding: utf-8 -*-

from flask import Blueprint, request, render_template
from flask_login import login_required

from app import db
from app.forms import UserForm, PostForm
from app.models import Post, User
from app.models.user import generate_password

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/')
@login_required
def index():
    title = request.args.get('title', 'World')
    # post = Post(title=title)
    # db.session.add(post)
    # db.session.commit()

    return render_template('admin/index.html')


@bp.route('/posts')
@login_required
def list_posts():
    posts = Post.query.all()
    total = len(posts)
    return render_template('admin/list_posts.html',
                           posts=posts, total=total, msg='')


@bp.route('/posts/new', methods=['GET', 'POST'])
@login_required
def new_post():
    return _post()


def _post(post_id=None):
    form = PostForm(request.form)
    msg = ''

    if post_id is not None:
        post = Post.query.filter_by(id=post_id).first_or_404()

    if form.validate_on_submit():
        title = form.title.data
        post = Post.query.filter_by(title=title).first()
        if post:
            post.save()
            msg = 'Post was successfully updated.'
        else:
            post = Post()
            msg = 'Post was successfully created.'
        form.populate_obj(post)
        post.save()
        posts = Post.query.all()
        total = len(posts)
        context = {'posts': posts, 'total': total, 'msg': msg}
        return render_template('admin/list_posts.html', **context)
    elif post_id is not None:
        form = PostForm(obj=post)
        form.submit.label.text = 'Update'
    return render_template('admin/post.html',
                           form=form, msg=msg, post_id=post_id)


@bp.route('/post/<post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id=None):
    return _post(post_id=post_id)


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
    users = User.query.all()
    total = len(users)
    return render_template('admin/list_users.html',
                           users=users, total=total, msg='')


@bp.route('/users/new', methods=['GET', 'POST'])
@login_required
def new_user():
    return _user()


def _user(user_id=None):
    form = UserForm(request.form)
    msg = ''

    if user_id is not None:
        user = User.query.filter_by(id=user_id).first_or_404()

    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        active = form.active.data
        user = User.query.filter_by(name=name).first()
        if user:
            user.email = email
            user.password = generate_password(password)
            user.active = active
            user.save()
            msg = 'User was successfully updated.'
        else:
            user = User(name=name, email=email,
                        password=generate_password(password), active=active)
            user.save()
            msg = 'User was successfully created.'
        users = User.query.all()
        total = len(users)
        context = {'users': users, 'total': total, 'msg': msg}
        return render_template('admin/list_users.html', **context)

    elif user_id is not None:
        form.name.data = user.name
        form.email.data = user.email
        form.active.data = 'on' if user.active else 'off'
        form.submit.label.text = 'Update'
        form.password.data = ''
    return render_template('admin/user.html', form=form, msg=msg,
                           user_id=user_id)


@bp.route('/users/<user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    return _user(user_id)
