# -*- coding: utf-8 -*-
from datetime import datetime

from flask import (
    Blueprint, request, render_template, redirect, url_for,
    current_app, session, Response, jsonify)
from flask_login import login_required, login_user, logout_user
from rauth import OAuth2Service
from werkzeug.contrib.atom import AtomFeed

from app.forms import LoginForm
from app.models import Post
from app.models.blog import MC_KEY_FEED, MC_KEY_SEARCH
from app.models.mc import cache
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
        url = url_for('blog.post', ident=post_id)

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


@cache(MC_KEY_FEED)
def _feed():
    feed = AtomFeed(title=current_app.config.get('SITE_TITLE'),
                    updated=datetime.now(), feed_url=request.url,
                    url=request.host)
    posts = Post.get_all()
    for post in posts:
        body = post.html_content
        summary = post.excerpt

        feed.add(
            post.title, body, content_type='html', summary=summary,
            summary_type='html', author=current_app.config.get('AUTHOR'),
            url=post.url, id=post.id, updated=post.created_at,
            published=post.created_at
        )
    return feed.to_string()


@bp.route('/atom.xml')
def feed():
    return Response(_feed(), content_type='text/xml')


@bp.route('/search')
def search():
    return render_template('search.html')


@bp.route('/search.json')
def search_json():
    return jsonify(_search_json())


@cache(MC_KEY_SEARCH)
def _search_json():
    posts = Post.get_all()
    return [
        {
            'url': post.url,
            'tags': [tag.name for tag in post.tags],
            'title': post.title,
            'content': post.html_content
        } for post in posts]
