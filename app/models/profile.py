# -*- coding: utf-8 -*-

import json
import os
from pathlib import Path

from flask import current_app
from jsonschema import validate

from .mc import cache
from .utils import empty, AttrDict

schema = {
    'type': 'object',
    'properties': {
        'intro': {'type': 'string'},
        'github_url': {'type': 'string'},
        'avatar': {'type': 'string'},
        'linkedin_url': {'type': 'string'}
    }
}
PROFILE_FILE = 'profile.json'
MC_KEY_PROFILE = 'profile'


@cache(MC_KEY_PROFILE)
def get_profile():
    file = Path(current_app.config.get('HERE')) / PROFILE_FILE
    if not os.path.exists(file):
        return empty

    with open(file) as f:
        return AttrDict(json.load(f))


def set_profile(**kwargs):
    validate(kwargs, schema)
    with open(Path(current_app.config.get('HERE')) / PROFILE_FILE, 'w') as f:
        json.dump(kwargs, f)
