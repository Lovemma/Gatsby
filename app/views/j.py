# -*- coding: utf-8 -*-

from functools import wraps

import mistune
from flask import Blueprint, session, jsonify, request, get_template_attribute

from app.models import Post, ReactItem, ReactStats
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
            post = Post.query.get(post_id)
            if not post:
                return jsonify({'r': 1, 'msg': 'Post not exist.'})
            args = (user, post)
        else:
            args = (user,)
        return f(*args, **kwargs)

    return wrapped


@bp.route('/comment/<post_id>', methods=['POST'])
@login_required
def create_comment(user, post):
    content = request.form.get('content')
    if not content:
        return jsonify({'r': 1, 'msg': 'Comment content required.'})
    comment = post.add_comment(user['gid'], content)

    template = get_template_attribute('utils.html',
                                      'render_single_comment')
    return jsonify({
        'r': 0 if comment else 1,
        'html': template(comment, user)
    })


@bp.route('/comment/<post_id>/comments')
def comments(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'r': 1, 'msg': 'Post not exist.'})

    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))

    start = (page - 1) * per_page
    comments = post.comments[start:start + per_page]

    user = session.get('user')
    template = get_template_attribute('utils.html', 'render_comments')

    return jsonify({
        'r': 0,
        'html': template(comments, user)
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
        rv = post.add_reaction(user['id'], reaction_type)
    elif request.method == 'DELETE':
        rv = post.cancel_reaction(user['id'])

    stat = ReactStats.get_by_target(post.id, K_POST)
    reaction_type = None
    if user:
        reaction_item = ReactItem.get_reaction_item(
            user['id'], post.id, K_POST)
        if reaction_item:
            reaction_type = reaction_item.reaction_type
    template = get_template_attribute('utils.html', 'render_react_container')
    return jsonify({'r': int(not rv),
                    'html': template(stat=stat, reaction_type=reaction_type)
                    })
