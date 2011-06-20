# -*- coding: utf-8 -*-
"""
    assname
    ~~~~~~~

    Figures out the assigned name for an expression.

    :copyright: (c) Copyright 2011 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""
import sys
import dis


def assigned_name():
    frame = sys._getframe(2)
    code = frame.f_code.co_code[frame.f_lasti:]
    try:
        has_arg = ord(code[0]) >= dis.HAVE_ARGUMENT
        skip = 3 if has_arg else 1
        next_code = ord(code[skip])
        name_index = ord(code[skip + 1])
    except IndexError:
        return True
    if next_code in (dis.opmap['STORE_FAST'],
                     dis.opmap['STORE_GLOBAL'],
                     dis.opmap['STORE_NAME'],
                     dis.opmap['STORE_DEREF']):
        namelist = frame.f_code.co_names
        if next_code == dis.opmap['STORE_GLOBAL']:
            namelist = frame.f_code.co_names
        elif next_code == dis.opmap['STORE_DEREF']:
            namelist = frame.f_code.co_freevars
        return namelist[name_index]


if __name__ == '__main__':
    import collections
    def namedtuple(*names):
        rv = collections.namedtuple(assigned_name(), names)
        rv.__module__ = sys._getframe(1).f_globals['__name__']
        return rv

    Token = namedtuple('type', 'value', 'lineno')
    print Token, Token('int', 42, 1)
