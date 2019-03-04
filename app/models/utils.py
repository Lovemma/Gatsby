# -*- coding: utf-8 -*-

class Empty:

    def __call__(self, *a, **kw):
        return empty

    def __nonzero__(self):
        return False

    def __contains__(self, item):
        return False

    def __repr__(self):
        return '<Empty Object>'

    def __str__(self):
        return ''

    def __eq__(self, v):
        return isinstance(v, Empty)

    def __getattr__(self, name):
        if not name.startswith('__'):
            return empty
        raise AttributeError(name)

    def __len__(self):
        return 0

    def __getitem__(self, key):
        return empty

    def __setitem__(self, key, value):
        pass

    def __delitem__(self, key):
        pass

    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration

    def next(self):
        raise StopIteration


empty = Empty()


def trunc_utf8(string, num, etc='...'):
    if num >= len(string):
        return string

    if etc:
        trunc_idx = num - len(etc)
    else:
        trunc_idx = num
    ret = string[:trunc_idx]
    if etc:
        ret += etc
    return ret


class Null:
    def __call__(self, *args, **kwargs):
        return self

    def __getattr__(self, item):
        return ''

    def __setattr__(self, key, value):
        return self

    def __delattr__(self, item):
        return self

    def __repr__(self):
        return '<Null>'

    def __str__(self):
        return 'Null'


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self
