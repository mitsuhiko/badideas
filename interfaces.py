# -*- coding: utf-8 -*-
"""
    interfaces
    ~~~~~~~~~~

    Implements a ``implements()`` function that does interfaces.  It's
    a very simple implementation and does not handle multiple calls
    to implements() properly.

    :copyright: (c) Copyright 2011 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""
import sys


class BaseType(type):
    pass


class Base(object):
    __metaclass__ = BaseType


class Interface(object):
    __slots__ = ()


def find_real_type(explicit, bases):
    if explicit is not None:
        return explicit
    for base in bases:
        if type(base) is not type:
            return type(base)
    return type


def iter_interface_methods(interface):
    for key, value in interface.__dict__.iteritems():
        if callable(value):
            yield key


def implemented(class_, interface, method):
    return getattr(class_, method).im_func \
        is not getattr(interface, method).im_func


def make_meta_factory(metacls, interfaces):
    def __metaclass__(name, bases, d):
        real_type = find_real_type(metacls, bases)
        bases += interfaces
        rv = real_type(name, bases, d)
        for interface in interfaces:
            for method in iter_interface_methods(interface):
                if not implemented(rv, interface, method):
                    raise NotImplementedError('Missing method %r on %r '
                        'from interface %r' % (method, rv.__name__,
                                               interface.__name__))
        return rv
    return __metaclass__


def implements(*interfaces):
    cls_scope = sys._getframe(1).f_locals
    metacls = cls_scope.get('__metaclass__')
    metafactory = make_meta_factory(metacls, interfaces)
    cls_scope['__metaclass__'] = metafactory


if __name__ == '__main__':
    class IRenderable(Interface):

        def render(self):
            raise NotImplementedError()


    class User(Base):
        implements(IRenderable)

        def render(self):
            return self.username

    print User.__bases__
