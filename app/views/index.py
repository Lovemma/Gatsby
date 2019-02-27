# -*- coding: utf-8 -*-

from flask import (
    Blueprint, request, render_template, redirect, url_for,
    current_app, session
)
from flask_login import login_required, login_user, logout_user
from rauth import OAuth2Service

from app.forms import LoginForm
from app.models.user import validate_login, create_github_user

bp = Blueprint('index', __name__, url_prefix='/')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    error = ''

    if form.validate_on_submit():
        name = form.name.data
        password = form.password.data
        is_validated, user = validate_login(name, password)
        if is_validated:
            login_user(user)
            return redirect(url_for('admin.index'))
        error = 'Validation failed. Please try again'
    return render_template('admin/login_user.html', request=request,
                           form=form, error=error)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')


@bp.route('/oauth')
@bp.route('/oauth/post/<post_id>')
def oauth(post_id=None):
    if post_id is None:
        url = '/'
    else:
        url = url_for('blog.post', post_id=post_id)

    user = session.get('user')
    if user:
        return redirect(url)

    github = OAuth2Service(
        client_id=current_app.config.get('GITHUB_CLIENT_ID'),
        client_secret=current_app.config.get('GITHUB_CLIENT_SECRET'),
        name='github',
        authorize_url='https://github.com/login/oauth/authorize',
        access_token_url='https://github.com/login/oauth/access_token',
        base_url='https://api.github.com/'
    )
    if 'error' in request.args:
        return request.args.get('error')

    redirect_url = current_app.config.get('REDIRECT_URL')
    if post_id is not None:
        redirect_url += f'/post/{post_id}'

    if 'code' not in request.args:
        return redirect(github.get_authorize_url(
            scope='email profile', redirect_uri=redirect_url))

    code = request.args.get('code')
    auth_session = github.get_auth_session(data={'code': code})

    user_info = auth_session.get('/user').json()

    user = create_github_user(user_info)

    session['user'] = user.to_dict()

    return redirect(url)
