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

import os
from tempfile                   import mkdtemp
from shutil                     import rmtree

from draughtcraft.tests         import TestModel
from draughtcraft.lib.minify    import (javascript_link, stylesheet_link, 
                                    RedisResourceCache, ResourceLookupMiddleware)
from beaker.cache               import CacheManager
from webob                      import Request

import pecan
import fudge


class MinificationTestCase(TestModel):

    def setUp(self):
        super(MinificationTestCase, self).setUp()
        self.fixture_path = mkdtemp()

        self.touch_file('b.js')
        self.touch_file('b.css')
        self.touch_file('c.css')
        self.touch_file('c.js')
        os.mkdir(os.path.join(self.fixture_path, 'deep'))
        self.touch_file('deep/a.css')
        self.touch_file('deep/a.js')
        self.touch_file('deep/d.css')
        self.touch_file('deep/d.js')

        # set up a fake request with a beaker session
        pecan.core.state.request = Request.blank('/')
        self.cache = CacheManager(
            key = pecan.conf.cache['key']
        )
        pecan.core.state.request.environ['beaker.cache'] = self.cache
        pecan.conf.app.static_root = self.fixture_path

    def tearDown(self):
        rmtree(self.fixture_path)
        super(MinificationTestCase, self).tearDown()

    def touch_file(self, path):
        open(os.path.join(self.fixture_path, path), 'w').close()

    def write_file(self, path, contents):
        f = open(os.path.join(self.fixture_path, path), 'w')
        f.write(contents)
        f.close()

    def in_cache(self, filename):
        import beaker
        for c in beaker.cache.cache_managers.values():
            for (timestamp, _, values) in c.namespace.dictionary.values():
                if filename in values: return True
        return False

    def test_paths(self):
        """Testing if paths are constructed correctly"""
        # minify and combine
        js_source = javascript_link('/deep/a.js', '/b.js', combined=True, minified=True)
        css_source = stylesheet_link('/deep/a.css', '/b.css', combined=True)
        assert '"/a.b.COMBINED.css?XYZ"' in css_source
        assert '"/a.b.COMBINED.min.js?XYZ"' in js_source
        assert os.path.isfile(os.path.join(self.fixture_path, 'a.b.COMBINED.css'))
        assert os.path.isfile(os.path.join(self.fixture_path, 'a.b.COMBINED.min.js'))
        assert self.in_cache('/a.b.COMBINED.css')
        assert self.in_cache('/a.b.COMBINED.min.js')

        # combine
        js_source = javascript_link('/deep/a.js', '/b.js', combined=True)
        css_source = stylesheet_link('/deep/a.css', '/b.css', combined=True)
        assert '"/a.b.COMBINED.css?XYZ"' in css_source
        assert '"/a.b.COMBINED.js?XYZ"' in js_source
        assert os.path.isfile(os.path.join(self.fixture_path, 'a.b.COMBINED.css'))
        assert os.path.isfile(os.path.join(self.fixture_path, 'a.b.COMBINED.js'))
        assert self.in_cache('/a.b.COMBINED.css')
        assert self.in_cache('/a.b.COMBINED.js')

        # combine single source
        js_source = javascript_link('/deep/a.js', combined=True)
        css_source = stylesheet_link('/deep/a.css', combined=True)
        assert '"/deep/a.css?XYZ"' in css_source
        assert '"/deep/a.js?XYZ"' in js_source
        assert os.path.isfile(os.path.join(self.fixture_path, 'deep/a.css'))
        assert os.path.isfile(os.path.join(self.fixture_path, 'deep/a.js'))
        assert self.in_cache('/deep/a.css')
        assert self.in_cache('/deep/a.js')

        # minify
        js_source = javascript_link('/deep/a.js', '/b.js', minified=True)
        assert '"/deep/a.min.js?XYZ"' in js_source
        assert '"/b.min.js?XYZ"' in js_source
        assert os.path.isfile(os.path.join(self.fixture_path, 'deep/a.min.js'))
        assert os.path.isfile(os.path.join(self.fixture_path, 'b.min.js'))
        assert self.in_cache('/deep/a.min.js')
        assert self.in_cache('/b.min.js')

        # root minify and combined
        js_source = javascript_link('/c.js', '/b.js', combined=True, minified=True)
        assert '"/c.b.COMBINED.min.js?XYZ"' in js_source
        assert os.path.isfile(os.path.join(self.fixture_path, 'c.b.COMBINED.min.js'))
        assert self.in_cache('/c.b.COMBINED.min.js')

        # root minify
        js_source = javascript_link('/c.js', '/b.js', minified=True)
        assert '"/b.min.js?XYZ"' in js_source
        assert '"/c.min.js?XYZ"' in js_source
        assert os.path.isfile(os.path.join(self.fixture_path, 'b.min.js'))
        assert os.path.isfile(os.path.join(self.fixture_path, 'c.min.js'))
        assert self.in_cache('/b.min.js')
        assert self.in_cache('/c.min.js')

        # both root minify and combined
        js_source = javascript_link('/deep/a.js', '/deep/d.js', combined=True, minified=True)
        css_source = stylesheet_link('/deep/a.css', '/deep/d.css', combined=True)
        assert '"/deep/a.d.COMBINED.css?XYZ"' in css_source
        assert '"/deep/a.d.COMBINED.min.js?XYZ"' in js_source
        assert os.path.isfile(os.path.join(self.fixture_path, 'deep/a.d.COMBINED.css'))
        assert os.path.isfile(os.path.join(self.fixture_path, 'deep/a.d.COMBINED.min.js'))
        assert self.in_cache('/deep/a.d.COMBINED.css')
        assert self.in_cache('/deep/a.d.COMBINED.min.js')

    @fudge.patch('redis.Redis')
    def test_redis(self, FakeRedis):

        class SimpleRedis(object):
            __dict__ = {}
            def get(self, k):
                return self.__dict__.get(k)
            def set(self, k, v):
                self.__dict__[k] = v
            def __iter__(self):
                for k in self.__dict__: yield k

        sub = SimpleRedis()
        (FakeRedis.expects_call().returns(sub))

        """Testing if paths are constructed correctly"""
        # minify and combine
        js_source = javascript_link('/deep/a.js', '/b.js', combined=True, minified=True, data_backend=RedisResourceCache)
        css_source = stylesheet_link('/deep/a.css', '/b.css', combined=True, data_backend=RedisResourceCache)
        assert '"/a.b.COMBINED.css?XYZ"' in css_source
        assert '"/a.b.COMBINED.min.js?XYZ"' in js_source
        assert not os.path.isfile(os.path.join(self.fixture_path, 'a.b.COMBINED.css'))
        assert not os.path.isfile(os.path.join(self.fixture_path, 'a.b.COMBINED.min.js'))
        assert '/a.b.COMBINED.css' in sub
        assert '/a.b.COMBINED.min.js' in sub
        assert self.in_cache('/a.b.COMBINED.css')
        assert self.in_cache('/a.b.COMBINED.min.js')


class TestRedisLookupMiddleware(TestModel):

    @fudge.patch('redis.Redis')
    def test_cache_hit(self, FakeRedis):

        # Fake redis as a simple in-memory key-value hash
        class SimpleRedis(object):
            __dict__ = {}
            def get(self, k):
                return self.__dict__.get(k)
            def set(self, k, v):
                self.__dict__[k] = v
            def __iter__(self):
                for k in self.__dict__: yield k

        sub = SimpleRedis()
        sub.set('/javascript/foo.js', 'RAW JS')
        (FakeRedis.expects_call().returns(sub))

        #
        # Set up a request for /javascript/foo.js, and configure the
        # resource cache backend as Redis
        #
        import pecan
        pecan.conf.cache['data_backend'] = RedisResourceCache
        environ = {
            'PATH_INFO' : '/javascript/foo.js'
        }

        def app(environ, start_response):
            raise AssertionError('The WSGI middleware should return raw JS.')

        def start_response(status, headers):
            assert status == '200 OK'
            assert ('Content-Type', 'application/javascript') in headers
        
        # Make sure the WSGI middleware returns a 200 OK with the raw JS
        resp = ResourceLookupMiddleware(app)(environ, start_response)
        assert resp == ['RAW JS']

    @fudge.patch('redis.Redis')
    def test_cache_miss(self, FakeRedis):

        # Fake redis as a simple in-memory key-value hash
        class SimpleRedis(object):
            __dict__ = {}
            def get(self, k):
                return self.__dict__.get(k)
            def set(self, k, v):
                self.__dict__[k] = v
            def __iter__(self):
                for k in self.__dict__: yield k

        sub = SimpleRedis()
        (FakeRedis.expects_call().returns(sub))

        #
        # Set up a request for /javascript/foo.js, and configure the
        # resource cache backend as Redis
        #
        import pecan
        pecan.conf.cache['data_backend'] = RedisResourceCache
        environ = {
            'PATH_INFO' : '/javascript/foo.js'
        }

        start_response = lambda status, headers: None

        passed = [False]
        def app(e, s):
            assert e == environ
            assert s == start_response
            passed[0] = True
        
        # Make sure the WSGI middleware returns a 200 OK with the raw JS
        resp = ResourceLookupMiddleware(app)(environ, start_response)

        assert passed[0] == True
        assert resp == None
