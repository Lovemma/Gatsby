# -*- coding: utf-8 -*-

from flask import Blueprint, json
from flask_login import login_required

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/publish/<post_id>', methods=['POST', 'DELETE'])
@login_required
def publish(post_id):
    return json.dumps({'r': 0})
