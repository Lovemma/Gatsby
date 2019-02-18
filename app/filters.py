# -*- coding: utf-8 -*-

from . import _app as app


@app.template_filter('hasattr')
def has_attr(obj, name):
    return hasattr(obj, name)
