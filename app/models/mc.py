# -*- coding: utf-8 -*-

import inspect
import re
from functools import wraps
from pickle import dumps, loads

from app import context
from app.models.utils import Empty

_memcached = None
__formaters = {}
percent_pattern = re.compile(r'%\w')
brace_pattern = re.compile(r'\{[\w\d\.\[\]_]+\}')


def get_memcached():
    global _memcached
    if _memcached is not None:
        return _memcached

    _memcached = context.get('memcached')
    return _memcached


def formater(text):
    """
    >>> format('%s %s', 3, 2, 7, a=7, id=8)
    '3 2'
    >>> format('%(a)d %(id)s', 3, 2, 7, a=7, id=8)
    '7 8'
    >>> format('{1} {id}', 3, 2, a=7, id=8)
    '2 8'
    >>> class Obj: id = 3
    >>> format('{obj.id} {0.id}', Obj(), obj=Obj())
    '3 3'
    >>> class Obj: id = 3
    >>> format('{obj.id.__class__} {obj.id.__class__.__class__} {0.id} {1}', \
    >>> Obj(), 6, obj=Obj())
    "<type 'int'> <type 'type'> 3 6"
    """
    percent = percent_pattern.findall(text)
    brace = brace_pattern.search(text)
    if percent and brace:
        raise Exception('mixed format is not allowed')

    if percent:
        n = len(percent)
        return lambda *a, **kw: text % tuple(a[:n])
    elif '%(' in text:
        return lambda *a, **kw: text % kw
    else:
        return text.format


def format(text, *a, **kw):
    f = __formaters.get(text)
    if f is None:
        f = formater(text)
        __formaters[text] = f
    return f(*a, **kw)


def gen_key_factory(key_pattern, arg_names, defaults):
    args = dict(zip(arg_names[-len(defaults):], defaults)) if defaults else {}
    if callable(key_pattern):
        names = inspect.getfullargspec(key_pattern)[0]

    def gen_key(*a, **kw):
        aa = args.copy()
        aa.update(zip(arg_names, a))
        aa.update(kw)
        if callable(key_pattern):
            key = key_pattern(*[aa[n] for n in names])
        else:
            key = format(key_pattern, *[aa[n] for n in arg_names], **aa)
        return key and key.replace(' ', '_'), aa

    return gen_key


def cache(key_pattern, expire=0):
    def decorator(f):
        args, varargs, varkw, defaults, *_ = inspect.getfullargspec(f)
        if varargs or varkw:
            raise Exception('Do not support varargs.')
        gen_key = gen_key_factory(key_pattern, args, defaults)

        @wraps(f)
        def _(*a, **kw):
            memcached = get_memcached()
            key, args = gen_key(*a, **kw)
            if not key:
                return f(*a, **kw)
            force = kw.pop('force', False)
            r = memcached.get(key.encode('utf-8')) if not force else None

            if r is None:
                r = f(*a, **kw)
                if r is not None:
                    r = dumps(r)
                    memcached.set(key.encode('utf-8'), r, expire)

            try:
                r = loads(r)
            except TypeError:
                pass
            if isinstance(r, Empty):
                r = None
            return r

        _.original_function = f
        return _

    return decorator


def clear_mc(*key):
    memcached = get_memcached()
    assert memcached is not None
    for k in key:
        memcached.delete(k.encode('utf-8'))
