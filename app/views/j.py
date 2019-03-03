# -*- coding: utf-8 -*-

from functools import wraps

import mistune
from flask import Blueprint, session, jsonify, request, get_template_attribute

from app.models import Post, ReactItem, ReactStats, Comment
from app.models.consts import K_POST

bp = Blueprint('j', __name__, url_prefix='/j')


def login_required(f):
    @wraps(f)
    def wrapped(**kwargs):
        user = session.get('user')
        if not user:
            return jsonify({'r': 403, 'msg': 'Login required.'})
        post_id = kwargs.pop('post_id', None)
        if post_id is not None:
            post = Post.cache(post_id)
            if not post:
                return jsonify({'r': 1, 'msg': 'Post not exist.'})
            args = (user, post)
        else:
            args = (user,)
        return f(*args, **kwargs)

    return wrapped


@bp.route('/post/<post_id>/comment', methods=['POST'])
@login_required
def create_comment(user, post):
    content = request.form.get('content')
    if not content:
        return jsonify({'r': 1, 'msg': 'Comment content required.'})
    comment = post.add_comment(user['gid'], content)
    liked_comment_ids = post.comment_ids_liked_by(user['gid'])

    template = get_template_attribute('utils.html',
                                      'render_single_comment')
    return jsonify({
        'r': 0 if comment else 1,
        'html': template(comment, user),
        'liked_comment_ids': liked_comment_ids
    })


@bp.route('/post/<post_id>/comments')
def comments(post_id):
    post = Post.cache(post_id)
    if not post:
        return jsonify({'r': 1, 'msg': 'Post not exist.'})

    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))

    start = (page - 1) * per_page
    comments = post.comments[start:start + per_page]

    user = session.get('user')
    liked_comment_ids = post.comment_ids_liked_by(user['gid'])
    template = get_template_attribute('utils.html', 'render_comments')

    return jsonify({
        'r': 0,
        'html': template(comments, user),
        'liked_comment_ids': liked_comment_ids
    })


@bp.route('/markdown', methods=['POST'])
@login_required
def render_markdown(user):
    text = request.form.get('text')
    if not text:
        return jsonify({'r': 1, 'msg': 'Text required.'})
    return jsonify({'r': 0, 'text': mistune.markdown(text)})


@bp.route('/post/<post_id>/react', methods=['POST', 'DELETE'])
@login_required
def react(user, post):
    if request.method == 'POST':
        reaction_type = request.form.get('reaction_type', None)
        if reaction_type is None:
            return jsonify({'r': 1, 'msg': 'Reaction type error.'})
        rv = post.add_reaction(user['gid'], reaction_type)
    elif request.method == 'DELETE':
        rv = post.cancel_reaction(user['gid'])

    stat = ReactStats.get_by_target(post.id, K_POST)
    reaction_type = None
    if user:
        reaction_item = ReactItem.get_reaction_item(
            user['gid'], post.id, K_POST)
        if reaction_item:
            reaction_type = reaction_item.reaction_type
    template = get_template_attribute('utils.html', 'render_react_container')
    return jsonify({'r': int(not rv),
                    'html': template(stat=stat, reaction_type=reaction_type)
                    })


@bp.route('/comment/<comment_id>/like', methods=['POST', 'DELETE'])
def comment_like(comment_id):
    user = session.get('user')
    if not user:
        return jsonify({'r': 403, 'msg': 'Login required.'})
    comment = Comment.cache(comment_id)
    if not comment:
        return jsonify({'r': 1, 'msg': 'Comment not exist.'})
    if request.method == 'POST':
        rv = comment.add_reaction(user['gid'], ReactItem.K_LOVE)
    elif request.method == 'DELETE':
        rv = comment.cancel_reaction(user['gid'])

    return jsonify({'r': int(not rv), 'n_likes': comment.n_likes})
