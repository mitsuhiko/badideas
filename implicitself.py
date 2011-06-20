# -*- coding: utf-8 -*-
"""
    implicitself
    ~~~~~~~~~~~~

    Implements a bytecode hack and metaclass to make the self
    implicit in functions.

    :copyright: (c) Copyright 2011 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""
import opcode
from types import FunctionType, CodeType


HAVE_ARGUMENT = opcode.HAVE_ARGUMENT
LOAD_FAST = opcode.opmap['LOAD_FAST']
STORE_FAST = opcode.opmap['STORE_FAST']
LOAD_GLOBAL = opcode.opmap['LOAD_GLOBAL']
STORE_GLOBAL = opcode.opmap['STORE_GLOBAL']
LOAD_ATTR = opcode.opmap['LOAD_ATTR']
STORE_ATTR = opcode.opmap['STORE_ATTR']
LOAD_NAME = opcode.opmap['LOAD_NAME']
STORE_NAME = opcode.opmap['STORE_NAME']


def disassemble(code):
    code = map(ord, code)
    i = 0
    n = len(code)
    while i < n:
        op = code[i]
        i += 1
        if op >= HAVE_ARGUMENT:
            oparg = code[i] | code[i + 1] << 8
            i += 2
        else:
            oparg = None
        yield op, oparg


def implicit_self(function):
    code = function.func_code
    bytecode, varnames, names = inject_self(code)
    function.func_code = CodeType(code.co_argcount + 1, code.co_nlocals + 1,
        code.co_stacksize, code.co_flags, bytecode, code.co_consts, names,
        varnames, code.co_filename, code.co_name, code.co_firstlineno,
        code.co_lnotab, code.co_freevars, code.co_cellvars)


def inject_self(code):
    varnames = ('self',) + tuple(n for i, n in enumerate(code.co_varnames))
    names = tuple(n for i, n in enumerate(code.co_names))
    bytecode = []

    for op, arg in disassemble(code.co_code):
        if op in (LOAD_FAST, STORE_FAST):
            arg = varnames.index(code.co_varnames[arg])
        elif op in (LOAD_GLOBAL, STORE_GLOBAL, LOAD_NAME, STORE_NAME):
            if code.co_names[arg] == 'self':
                op = LOAD_FAST if op in (LOAD_GLOBAL, LOAD_NAME) \
                               else STORE_FAST
                arg = 0
            else:
                arg = names.index(code.co_names[arg])
        elif op in (LOAD_ATTR, STORE_ATTR):
            arg = names.index(code.co_names[arg])
        bytecode.append(chr(op))
        if op >= opcode.HAVE_ARGUMENT:
            bytecode.append(chr(arg & 0xff))
            bytecode.append(chr(arg >> 8))

    return ''.join(bytecode), varnames, names


class ImplicitSelfType(type):

    def __new__(cls, name, bases, d):
        for key, value in d.iteritems():
            if isinstance(value, FunctionType):
                implicit_self(value)
        return type.__new__(cls, name, bases, d)


class ImplicitSelf(object):
    __metaclass__ = ImplicitSelfType


if __name__ == '__main__':
    import hashlib

    class User(ImplicitSelf):

        def __init__(username, password):
            self.username = username
            self.set_password(password)

        def set_password(password):
            self.hash = hashlib.sha1(password).hexdigest()

        def check_password(password):
            return hashlib.sha1(password).hexdigest() == self.hash

    u = User('mitsuhiko', 'default')
    print u.__dict__
