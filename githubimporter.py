# -*- coding: utf-8 -*-
"""
    githubimporter
    ~~~~~~~~~~~~~~

    Imports code directly from github.

    :copyright: (c) Copyright 2011 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""
import sys
import imp
import urllib
import urlparse


class GithubImporter(object):
    url_template = 'https://raw.github.com/%(user)s/%(project)s/master/%(file)s'

    def __init__(self, path):
        url = urlparse.urlparse(path)
        if url.scheme != 'github':
            raise ImportError()
        self.user = url.netloc
        self.project = url.path.strip('/')
        if '/' in self.project:
            self.project, self.path = self.project.split('/', 1)
        else:
            self.path = ''
        self._cache = {}

    def get_source_and_filename(self, name):
        rv = self._cache.get(name)
        if rv is not None:
            return rv
        url_name = name.replace('.', '/')
        for filename in url_name + '.py', url_name + '/__init__.py':
            try:
                url = self.url_template % dict(
                    user=self.user,
                    project=self.project,
                    file=urlparse.urljoin(self.path, filename)
                )
                resp = urllib.urlopen(url)
                if resp.code == 404:
                    continue
                rv = resp.read(), 'github://%s/%s' % (
                    self.user,
                    filename
                )
                self._cache[name] = rv
                return rv
            except IOError:
                continue
        raise ImportError(name)

    def get_source(self, name):
        return self.get_source_and_filename(name)[0]

    def get_filename(self, name):
        return self.get_source_and_filename(name)[1]

    def find_module(self, name, path=None):
        try:
            self.get_source_and_filename(name)
        except ImportError:
            return None
        return self

    def load_module(self, name):
        source, filename = self.get_source_and_filename(name)
        sys.modules[name] = mod = imp.new_module(name)
        mod.__loader__ = self
        mod.__file__ = filename
        if filename.endswith('/__init__.py'):
            mod.__path__ = [filename.rsplit('/', 1)[0]]
        exec source in mod.__dict__
        return mod


def install_hook():
    sys.path_hooks.append(GithubImporter)


if __name__ == '__main__':
    install_hook()
    sys.path.append('github://mitsuhiko/markupsafe')

    import markupsafe
    print markupsafe.__file__
    print markupsafe.Markup.escape('<foo>')
