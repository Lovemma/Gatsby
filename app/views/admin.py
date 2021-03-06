# -*- coding: utf-8 -*-
from pathlib import Path

from flask import Blueprint, request, render_template, current_app
from flask_login import login_required
from werkzeug.datastructures import CombinedMultiDict
from werkzeug.utils import secure_filename

from app.config import PER_PAGE
from app.forms import UserForm, PostForm, ProfileForm
from app.models import Post, User, Tag
from app.models.profile import get_profile, set_profile
from app.models.user import generate_password
from app.models.utils import Pagination

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/')
@login_required
def index():
    return render_template('admin/index.html')


@bp.route('/posts/<page>')
@bp.route('/posts')
@login_required
def list_posts(page=1):
    return _get_post_context(page)


def _get_post_context(page=1):
    page = int(page)
    start = (page - 1) * PER_PAGE
    posts = Post.query.all()
    total = len(posts)
    posts = posts[start:start + PER_PAGE]
    paginator = Pagination(page, PER_PAGE, total)
    return render_template('admin/list_posts.html', posts=posts, total=total,
                           msg='', paginator=paginator, page=page)


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
        assert str(form.author_id.data).isdigit()
        post = Post.query.filter_by(title=title).first()
        if post:
            post.save()
            msg = 'Post was successfully updated.'
        else:
            post = Post()
            msg = 'Post was successfully created.'
        form.status.data = form.status.data == 'on'
        tags = form.tags.data
        content = form.content.data
        is_page = form.is_page.data
        del form.tags
        del form.content
        del form.is_page
        form.populate_obj(post)
        if is_page:
            post.type = Post.TYPE_PAGE
        post.save()
        post.update_tags(tags)
        post.set_content(content)
        return _get_post_context()
    elif post_id is not None:
        form = PostForm(obj=post)
        form.tags.data = [tag.name for tag in post.tags]
        form.can_comment.data = post.can_comment
        form.is_page.data = post.is_page
        form.status.data = 'on' if post.status else 'off'
        form.submit.label.text = 'Update'
    tags = Tag.query.all()
    authors = User.query.all()
    return render_template('admin/post.html',
                           form=form, msg=msg, post_id=post_id, tags=tags,
                           authors=authors)


@bp.route('/post/<post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id=None):
    return _post(post_id=post_id)


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
        form = UserForm(obj=user)
        form.password.data = ''
        form.active.data = user.active
        form.submit.label.text = 'Update'
    return render_template('admin/user.html', form=form, msg=msg,
                           user_id=user_id)


@bp.route('/users/<user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    return _user(user_id)


@bp.route('/profile', methods=['GET', 'POST'])
def profile():
    form = ProfileForm(CombinedMultiDict((request.files, request.form)))
    if request.method == 'POST':
        avatar_path = ''
        if form.validate():
            image = form.avatar.data
            intro = form.intro.data
            github_url = form.github_url.data
            linkedin_url = form.linkedin_url.data
            avatar_path = secure_filename(image.filename)
            uploaded_file = Path(
                current_app.config.get('UPLOAD_FOLDER')) / avatar_path
            image.save(str(uploaded_file))
            form.avatar_path.data = avatar_path
            kw = {'intro': intro, 'github_url': github_url,
                  'linkedin_url': linkedin_url}
            if avatar_path:
                kw.update(avatar=avatar_path)
            set_profile(**kw)
        if not avatar_path:
            form.avatar_path.data = get_profile().avatar

    elif request.method == 'GET':
        profile = get_profile()
        form.intro.data = profile.intro
        form.github_url.data = profile.github_url
        form.avatar_path.data = profile.avatar

    return render_template('admin/profile.html', form=form)
