# -*- coding: utf-8 -*-

from collections import Counter
from itertools import groupby

from flask import Blueprint, render_template, session, abort, current_app

from app.models import Post, PostTag, Tag
from app.models.profile import get_profile
from app.models.utils import Pagination

bp = Blueprint('blog', __name__, url_prefix='/')


@bp.route('/')
def index():
    return _posts()


def _posts(page=1):
    PER_PAGE = current_app.config.get('PER_PAGE')
    start = (page - 1) * PER_PAGE
    posts = Post.get_all()
    total = len(posts)
    posts = posts[start: start + PER_PAGE]
    paginator = Pagination(page, PER_PAGE, total)
    profile = get_profile()

    return render_template('index.html', posts=posts, paginator=paginator,
                           profile=profile)


@bp.route('/post/<ident>/')
def post(ident):
    return _post(ident=ident)


@bp.route('/page/<ident>/')
def page(ident=1):
    if str(ident).isdigit():
        return _posts(page=int(ident))
    return _post(ident=ident)


def _post(ident, is_preview=False):
    post = Post.get_or_404(ident)
    if not is_preview and post.status != Post.STATUS_ONLINE:
        abort(404)
    github_user = session.get('user')
    stats = post.stats
    reaction_type = None
    liked_comment_ids = []
    if github_user:
        reaction_type = post.get_reaction_type(github_user['gid'])

        liked_comment_ids = post.comment_ids_liked_by(
            github_user['gid'])
    related_posts = post.get_related()
    return render_template('post.html', post=post, github_user=github_user,
                           stats=stats, reaction_type=reaction_type,
                           liked_comment_ids=liked_comment_ids,
                           related_posts=related_posts)


@bp.route('/archives')
def archives():
    rv = {
        year: list(items) for year, items in groupby(
        Post.query.filter_by(status=Post.STATUS_ONLINE).order_by(
            Post.id.desc()).all(),
        lambda item: item.created_at.year)
    }
    archives = sorted(rv.items(), key=lambda x: x[0],
                      reverse=True)
    return render_template('archives.html', archives=archives)


@bp.route('/archive/<year>')
def archive(year):
    posts = Post.query.filter(Post.status == Post.STATUS_ONLINE,
                              Post.created_at >= f'{year}-01-01').order_by(
        Post.id.desc()).all()
    archives = [(year, posts)]
    return render_template('archives.html', archives=archives)


@bp.route('/tags')
def tags():
    tag_ids = PostTag.query.with_entities(PostTag.tag_id).all()
    counter = Counter(tag_ids)
    tags_ = Tag.get_multi(counter.keys())
    tags = [(tags_[index], count)
            for index, count in enumerate(counter.values())]

    return render_template('tags.html', tags=tags)


@bp.route('/tag/<int:tag_id>/')
def tag(tag_id):
    tag = Tag.cache(tag_id)
    post_ids = PostTag.query.filter_by(tag_id=tag_id).order_by(
        PostTag.post_id.desc()).with_entities(PostTag.post_id).all()
    posts = Post.get_multi(post_ids)
    return render_template('tag.html', tag=tag, posts=posts)
