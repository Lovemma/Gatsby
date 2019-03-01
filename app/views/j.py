# -*- coding: utf-8 -*-

from functools import wraps

import mistune
from flask import Blueprint, session, jsonify, request, get_template_attribute

from app.models import Post

bp = Blueprint('j', __name__, url_prefix='/j')


def login_required(f):
    @wraps(f)
    def wrapped(**kwargs):
        user = session.get('user')
        if not user:
            raise jsonify({'r': 403, 'msg': 'Login required.'})
        return f(user, **kwargs)

    return wrapped


@bp.route('/comment/<post_id>', methods=['POST'])
@login_required
def create_comment(user, post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'r': 1, 'msg': 'Post not exist.'})

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
