# -*- coding: utf-8 -*-

from collections import Counter
from itertools import groupby

from flask import Blueprint, render_template, session

from app.models.consts import K_POST
from app.models import Post, PostTag, Tag, ReactItem, ReactStats

bp = Blueprint('blog', __name__, url_prefix='/')


@bp.route('/')
def index():
    posts = Post.query.all()

    return render_template('index.html', posts=posts)


@bp.route('/post/<post_id>/')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    github_user = session.get('user')
    stat = ReactStats.get_by_target(post_id, K_POST)
    reaction_type = None
    if github_user:
        reaction_item = ReactItem.get_reaction_item(
            github_user['id'], post_id, K_POST)
        if reaction_item:
            reaction_type = reaction_item.reaction_type
    return render_template('post.html', post=post, github_user=github_user,
                           stat=stat, reaction_type=reaction_type)


@bp.route('/archives')
def archives():
    rv = {
        year: list(items) for year, items in groupby(
        Post.query.filter_by(published=Post.STATUS_ONLINE).order_by(
            Post.id.desc()).all(),
        lambda item: item.created_at.year)
    }
    archives = sorted(rv.items(), key=lambda x: x[0],
                      reverse=True)
    return render_template('archives.html', archives=archives)


@bp.route('/archive/<year>')
def archive(year):
    posts = Post.query.filter(Post.published == Post.STATUS_ONLINE,
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


@bp.route('/search')
def search():
    return render_template('index.html')


@bp.route('/atom.xml')
def atom():
    return render_template('index.html')
