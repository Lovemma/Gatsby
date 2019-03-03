# -*- coding: utf-8 -*-

from flask.signals import _signals

comment_reacted = _signals.signal('comment_reacted')
