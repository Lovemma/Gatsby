# -*- coding: utf-8 -*-

from flask import Blueprint, json, abort, request
from flask_login import login_required

from app.models import Post

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/publish/<post_id>', methods=['POST', 'DELETE'])
@login_required
def publish(post_id):
    if not post_id:
        abort(404)
    post = Post.query.get(post_id)
    if not post:
        return json.dumps({'r': 1, 'msg': 'Post not exist'})
    if request.method == 'POST':
        post.published = True
    elif request.method == 'DELETE':
        post.published = False
    post.save()
    return json.dumps({'r': 0})


@bp.route('/delete/<post_id>', methods=['DELETE'])
@login_required
def delete(post_id):
    if not post_id:
        abort(404)
    post = Post.query.get(post_id)
    if not post:
        return json.dumps({'r': 1, 'msg': 'Post not exist'})
    post.delete()
    return json.dumps({'r': 0})
