# -*- coding: utf-8 -*-
"""
    rvused
    ~~~~~~

    Is my return value used?  This function will tell you.

    :copyright: (c) Copyright 2011 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""
import sys
import dis


def return_value_used():
    frame = sys._getframe(2)
    code = frame.f_code.co_code[frame.f_lasti:]
    try:
        has_arg = ord(code[0]) >= dis.HAVE_ARGUMENT
        next_code = code[3 if has_arg else 1]
    except IndexError:
        return True
    return ord(next_code) != dis.opmap['POP_TOP']


if __name__ == '__main__':
    def foo():
        if return_value_used():
            print 'My return value is used'
        else:
            print 'My return value is discarded'
    foo()
    a = foo()
