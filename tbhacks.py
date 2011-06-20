# -*- coding: utf-8 -*-
"""
    tbhacks
    ~~~~~~~

    Provides a function to rechain tracebacks.

    :copyright: (c) Copyright 2011 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""
import sys
import ctypes
from types import TracebackType


if hasattr(ctypes.pythonapi, 'Py_InitModule4_64'):
    _Py_ssize_t = ctypes.c_int64
else:
    _Py_ssize_t = ctypes.c_int


if hasattr(sys, 'getobjects'):
    class _PyObject(ctypes.Structure):
        pass
    _PyObject._fields_ = [
        ('_ob_next', ctypes.POINTER(_PyObject)),
        ('_ob_prev', ctypes.POINTER(_PyObject)),
        ('ob_refcnt', _Py_ssize_t),
        ('ob_type', ctypes.POINTER(_PyObject))
    ]
else:
    class _PyObject(ctypes.Structure):
        pass
    _PyObject._fields_ = [
        ('ob_refcnt', _Py_ssize_t),
        ('ob_type', ctypes.POINTER(_PyObject))
    ]


class _Traceback(_PyObject):
    pass
_Traceback._fields_ = [
    ('tb_next', ctypes.POINTER(_Traceback)),
    ('tb_frame', ctypes.POINTER(_PyObject)),
    ('tb_lasti', ctypes.c_int),
    ('tb_lineno', ctypes.c_int)
]


def tb_set_next(tb, next):
    if not (isinstance(tb, TracebackType) and
            (next is None or isinstance(next, TracebackType))):
        raise TypeError('tb_set_next arguments must be traceback objects')
    obj = _Traceback.from_address(id(tb))
    if tb.tb_next is not None:
        old = _Traceback.from_address(id(tb.tb_next))
        old.ob_refcnt -= 1
    if next is None:
        obj.tb_next = ctypes.POINTER(_Traceback)()
    else:
        next = _Traceback.from_address(id(next))
        next.ob_refcnt += 1
        obj.tb_next = ctypes.pointer(next)
