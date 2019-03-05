# -*- coding: utf-8 -*-

from . import app


@app.template_filter('hasattr')
def has_attr(obj, name):
    return hasattr(obj, name)


@app.template_filter('getattr')
def get_attr(obj, name):
    return getattr(obj, name)
