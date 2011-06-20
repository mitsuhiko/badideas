# -*- coding: utf-8 -*-
"""
    caseinsensitive
    ~~~~~~~~~~~~~~~

    An implementation of a case insensitive namespace.

    :copyright: (c) Copyright 2011 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""
from collections import MutableMapping


class Namespace(MutableMapping):

    def __init__(self):
        self.ns = {}

    def __getitem__(self, key):
        return self.ns[key.lower()]

    def __delitem__(self, key):
        del self.ns[key.lower()]

    def __setitem__(self, key, value):
        self.ns[key.lower()] = value

    def __len__(self):
        return len(self.ns)

    def __iter__(self):
        return iter(self.ns)


if __name__ == '__main__':
    ns = Namespace()
    exec '''if 1:
        foo = 42
        Bar = 23
        print (Foo, BAR)
    ''' in {}, ns
