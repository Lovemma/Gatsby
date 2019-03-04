# -*- coding: utf-8 -*-

import json
import os
from pathlib import Path

from flask import current_app
from jsonschema import validate

from .utils import Null, AttrDict

schema = {
    'type': 'object',
    'properties': {
        'intro': {'type': 'string'},
        'github_url': {'type': 'string'},
        'avatar': {'type': 'string'}
    }
}
PROFILE_FILE = 'profile.json'


def get_profile():
    file = Path(current_app.config.get('HERE')) / PROFILE_FILE
    if not os.path.exists(file):
        return Null()

    with open(file) as f:
        return AttrDict(json.load(f))


def set_profile(**kwargs):
    validate(kwargs, schema)
    with open(Path(current_app.config.get('HERE')) / PROFILE_FILE, 'w') as f:
        json.dump(kwargs, f)
