from unittest                   import TestCase
from beaker.session             import SessionObject
from webob                      import Request, exc
from draughtcraft.lib.csrf      import (CSRFPreventionHook, token_key, 
                                        auth_token_hidden_field, secure_form,
                                        auth_token_pair, authentication_token)

import pecan


class TestHelpers(TestCase):

    def tearDown(self):
        if hasattr(pecan.core.state, 'request'):
            del pecan.core.state.request

    def test_authentication_token(self):
        pecan.core.state.request = Request.blank('/')
        pecan.core.state.request.environ['beaker.session'] = SessionObject(
            pecan.core.state.request.environ
        )
        value = authentication_token()
        assert value is not None
        assert pecan.core.state.request.environ['beaker.session'][token_key] == value

    def test_token_hidden_field(self):
        pecan.core.state.request = Request.blank('/')
        pecan.core.state.request.environ['beaker.session'] = SessionObject(
            pecan.core.state.request.environ
        )
        val = '<div style="display: none;"><input id="%s" name="%s" type="hidden" value="%s" /></div>' % (
            token_key,
            token_key,
            authentication_token()
        )
        assert str(auth_token_hidden_field()) == val

    def test_secure_form(self):
        pecan.core.state.request = Request.blank('/')
        pecan.core.state.request.environ['beaker.session'] = SessionObject(
            pecan.core.state.request.environ
        )
        val = '<div style="display: none;"><input id="%s" name="%s" type="hidden" value="%s" /></div>' % (
            token_key,
            token_key,
            authentication_token()
        )
        assert val in str(secure_form('POST'))

    def test_token_pair(self):
        pecan.core.state.request = Request.blank('/')
        pecan.core.state.request.environ['beaker.session'] = SessionObject(
            pecan.core.state.request.environ
        )
        assert auth_token_pair() == (token_key, authentication_token())

    def test_same_origin(self):
        hook = CSRFPreventionHook()
        assert hook.same_origin(
            'http://localhost',
            'http://localhost'
        )
        assert hook.same_origin(
            'http://localhost:80',
            'http://localhost:80'
        )
        assert not hook.same_origin(
            'http://localhost:80',
            'http://localhost:8001'
        )
        assert not hook.same_origin(
            'http://localhost:80',
            'http://somehost:80'
        )
        assert not hook.same_origin(
            'http://localhost:80',
            'ftp://localhost:80'
        )


class TestCSRFIdempotent(TestCase):

    def setUp(self):
        self.hook = CSRFPreventionHook()

    def tearDown(self):
        if hasattr(pecan.core.state, 'request'):
            del pecan.core.state.request

    def test_simple_get(self):
        pecan.core.state.request = Request.blank('/')
        assert pecan.core.state.request.method == 'GET'

        self.hook.on_route(pecan.core.state)

    def test_simple_head(self):
        pecan.core.state.request = Request.blank('/', method='HEAD')
        assert pecan.core.state.request.method == 'HEAD'

        self.hook.on_route(pecan.core.state)

    def test_simple_options(self):
        pecan.core.state.request = Request.blank('/', method='OPTIONS')
        assert pecan.core.state.request.method == 'OPTIONS'

        self.hook.on_route(pecan.core.state)

    def test_simple_trace(self):
        pecan.core.state.request = Request.blank('/', method='TRACE')
        assert pecan.core.state.request.method == 'TRACE'

        self.hook.on_route(pecan.core.state)


class TestCSRFPOST(TestCase):

    def setUp(self):
        self.hook = CSRFPreventionHook()

    def tearDown(self):
        if hasattr(pecan.core.state, 'request'):
            del pecan.core.state.request

    def test_referer_required(self):
        """
        If no referer is provided in a POST request, it should fail with a 403
        """
        pecan.core.state.request = Request.blank('/', method='POST')
        assert pecan.core.state.request.method == 'POST'

        try:
            self.hook.on_route(pecan.core.state)
        except exc.HTTPForbidden: pass
        else:
            raise AssertionError('HTTPForbidden should have been raised.')

    def test_referer_domain_mismatch(self):
        """
        If the referer in a POST request doesn't match the destination,
        the request should fail with a 403.
        """
        pecan.core.state.request = Request.blank(
            '/', 
            method = 'POST', 
            headers = {
                'Referer': 'http://example.com/'
            }
        )

        assert pecan.core.state.request.method == 'POST'

        try:
            self.hook.on_route(pecan.core.state)
        except exc.HTTPForbidden: pass
        else:
            raise AssertionError('HTTPForbidden should have been raised.')

    def test_invalid_session_token(self):
        """
        If a CSRF token doesn't match a request parameter, the request should 
        fail with a 403.
        """
        pecan.core.state.request = Request.blank(
            '/', 
            body = '%s=FOO' % token_key,
            method = 'POST', 
            headers = {
                'Referer': 'http://localhost:80/some/path'
            }
        )
        pecan.core.state.request.environ['beaker.session'] = SessionObject(
            pecan.core.state.request.environ
        )

        assert pecan.core.state.request.method == 'POST'

        try:
            self.hook.on_route(pecan.core.state)
        except exc.HTTPForbidden: pass
        else:
            raise AssertionError('HTTPForbidden should have been raised.')

    def test_valid_session_token(self):
        """
        If a CSRF token matchs a request parameter, the request should pass.
        """
        pecan.core.state.request = Request.blank(
            '/', 
            body = '%s=XYZ' % token_key,
            method = 'POST', 
            headers = {
                'Referer': 'http://localhost:80/some/path'
            }
        )
        pecan.core.state.request.environ['beaker.session'] = SessionObject(
            pecan.core.state.request.environ
        )
        pecan.core.state.request.environ['beaker.session'][token_key] = 'XYZ'

        assert pecan.core.state.request.method == 'POST'
        assert self.hook.on_route(pecan.core.state) == None
