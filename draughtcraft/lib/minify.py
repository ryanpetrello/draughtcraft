#
# Copyright (c) 2005-2009 Ben Bangert, James Gardner, Philip Jenvey,
#                         Mike Orr, Jon Rosenbaugh, Christoph Haas, 
#                         and other contributors.
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. The name of the author or contributors may not be used to endorse or
#    promote products derived from this software without specific prior
#    written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
# 
# 
# ------------------------------------------------------------------------------
# 
# 
# Portions of WebHelpers covered by the following license::
# 
# Copyright (c) 2005, the Lawrence Journal-World
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
# 
#     1. Redistributions of source code must retain the above copyright notice, 
#        this list of conditions and the following disclaimer.
#     
#     2. Redistributions in binary form must reproduce the above copyright 
#        notice, this list of conditions and the following disclaimer in the
#        documentation and/or other materials provided with the distribution.
# 
#     3. Neither the name of Django nor the names of its contributors may be used
#        to endorse or promote products derived from this software without
#        specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

"""Minification helpers.

This module provides enhanced versions of the ``javascript_link`` and
``stylesheet_link`` helpers in ``webhelpers.html.tags``.  These versions add
two additional arguments:

javascript_link(url, minified=False, combined=False)
stylesheet_link(url, combined=False)

* **minified**: If true, reduce the file size by squeezing out
  whitespace and other characters insignificant to the Javascript syntax.
* **combined**: If true, concatenate the specified files into one file to
  reduce page load time.

Adapted from code by Pedro Algarvio and Domen Kozar <ufs@ufsoft.org>.
URL: http://docs.fubar.si/minwebhelpers/
"""

import os
import logging
import mimetypes
import cStringIO as StringIO

from webhelpers.html.tags import javascript_link as native_javascript_link
from webhelpers.html.tags import stylesheet_link as native_stylesheet_link

from jsmin import JavascriptMinify


__all__ = ['javascript_link', 'stylesheet_link', 'ResourceLookupMiddleware']
log = logging.getLogger(__name__)

def redis_connector():
    from pecan import conf
    from redis import Redis
    return Redis(**conf.redis)


class ResourceLookupMiddleware(object):
    """
    Used to serve resource lookups for minified and compiled JS and CSS files.
    """

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        from pecan import conf
        path = environ.get('PATH_INFO', '')
        if conf.cache.get('data_backend') == RedisResourceCache and \
            (path.startswith('/javascript') or path.startswith('/css')):
                cached = redis_connector().get(path)
                if cached:
                    start_response('200 OK', [('Content-Type', mimetypes.guess_type(path)[0])])
                    return [cached]

        return self.app(environ, start_response)


class ResourceCache(object):

    @classmethod
    def base_link(cls, ext, *sources, **options):
        from pecan import conf, request
        from draughtcraft.templates.helpers import stamp

        combined = options.pop('combined', False)
        minified = options.pop('minified', False)

        fs_root = conf.app.static_root

        cache = request.environ['beaker.cache']
        @cache.cache(conf.cache['key'])
        def combine_sources(sources, ext, fs_root):
            if len(sources) < 2:
                return sources

            names = list()
            js_buffer = StringIO.StringIO()
            base = os.path.commonprefix([os.path.dirname(s) for s in sources])

            for source in sources:
                # get a list of all filenames without extensions
                js_file = os.path.basename(source)
                js_file_name = os.path.splitext(js_file)[0]
                names.append(js_file_name)

                # build a master file with all contents
                full_source = os.path.join(fs_root, source.lstrip('/'))
                f = cls.retrieve_readable(full_source)
                js_buffer.write(f.read())
                js_buffer.write('\n')
                f.close()

            # glue a new name and generate path to it
            fname = '.'.join(names + ['COMBINED', ext])
            fpath = os.path.join(fs_root, base.strip('/'), fname)

            # write the combined file
            cls.write_combine(js_buffer, fpath)

            return [os.path.join(base, fname)]

        @cache.cache(conf.cache['key'])
        def minify_sources(sources, ext, fs_root=''):

            minified_sources = []

            for source in sources:
                # generate full path to source
                no_ext_source = os.path.splitext(source)[0]
                full_source = os.path.join(fs_root, (no_ext_source + ext).lstrip('/'))

                # generate minified source path
                full_source = os.path.join(fs_root, (source).lstrip('/'))
                no_ext_full_source = os.path.splitext(full_source)[0]
                minified = no_ext_full_source + ext

                if 'js' in ext:
                    # minify js source (read stream is auto-closed inside)
                    cls.write_minify(
                        cls.retrieve_readable(full_source),
                        minified
                    )

                minified_sources.append(no_ext_source + ext)

            return minified_sources

        if combined:
            sources = combine_sources(list(sources), ext, fs_root)

        if minified:
            sources = minify_sources(list(sources), '.min.' + ext, fs_root)

        # append a version stamp
        sources = [stamp(s) for s in sources]

        if 'js' in ext:
            return native_javascript_link(*sources, **options)
        if 'css' in ext:
            return native_stylesheet_link(*sources, **options)

    @classmethod
    def write_combine(cls, buff, dest):
        raise NotImplementedError() # pragma: no cover

    @classmethod
    def write_minify(cls, source, dest):
        raise NotImplementedError() # pragma: no cover

    @classmethod
    def retrieve_readable(cls, filepath):
        raise NotImplementedError() # pragma: no cover

    @classmethod
    def javascript_link(cls, *sources, **options):
        return cls.base_link('js', *sources, **options)

    @classmethod
    def stylesheet_link(cls, *sources, **options):
        return cls.base_link('css', *sources, **options)


class FileSystemResourceCache(ResourceCache):
    """
    A resource cache implemented at the file system level.
    """

    @classmethod
    def write_combine(cls, buff, dest):
        dest = open(dest, 'w')
        dest.write(buff.getvalue())
        dest.close()

    @classmethod
    def write_minify(cls, source, dest):
        dest = open(dest, 'w')
        JavascriptMinify().minify(source, dest)
        dest.close()

    @classmethod
    def retrieve_readable(cls, filepath):
        return open(filepath, 'r')


class RedisResourceCache(ResourceCache):

    @classmethod
    def write_combine(cls, buff, dest):
        from pecan import conf
        redis = redis_connector()
        redis.set(dest.replace(conf.app.static_root, ''), buff.getvalue())

    @classmethod
    def write_minify(cls, source, dest):
        from pecan import conf
        redis = redis_connector()
        buff = StringIO.StringIO()
        JavascriptMinify().minify(source, buff)
        redis = redis_connector()
        redis.set(dest.replace(conf.app.static_root, ''), buff.getvalue())

    @classmethod
    def retrieve_readable(cls, filepath):
        #
        # If the file already exists on disk (meaning it's a source file),
        # just use it.
        # 
        if os.path.isfile(filepath):
            return FileSystemResourceCache.retrieve_readable(filepath)

        #
        # Otherwise, the file is likely a combined/minified file that has been
        # saved in Redis.
        #
        from pecan import conf
        redis = redis_connector()
        buff = StringIO.StringIO()
        buff.write(redis.get(filepath.replace(conf.app.static_root, '')))
        buff.seek(0)
        return buff


def javascript_link(*sources, **options):
    from pecan import conf
    impl = options.get(
        'data_backend',
        conf.cache.get('data_backend', FileSystemResourceCache)
    )
    return impl.javascript_link(*sources, **options)

def stylesheet_link(*sources, **options):
    from pecan import conf
    impl = options.get(
        'data_backend',
        conf.cache.get('data_backend', FileSystemResourceCache)
    )
    return impl.stylesheet_link(*sources, **options)
