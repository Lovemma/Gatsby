# -*- coding: utf-8 -*-

from werkzeug.utils import find_modules, import_string


def register_blueprint(root, app):
    for name in find_modules(root, recursive=True):
        mod = import_string(name)
        if hasattr(mod, 'bp'):
            app.register_blueprint(mod.bp)
