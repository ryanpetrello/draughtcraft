from draughtcraft       import model as dcmodel
from webtest            import TestApp as WebTestApp
from unittest           import TestCase

import py.test

class TestApp(TestCase):

    __headers__ = {}

    def setUp(self):
        # Set up a fake app
        self.app = WebTestApp(py.test.wsgi_app)
        
        # Create the database tables
        dcmodel.start()
        dcmodel.metadata.create_all()
        dcmodel.clear()

    def tearDown(self):
        # Tear down and dispose the DB binding
        dcmodel.metadata.bind.dispose()
        dcmodel.Session.expunge_all()

    def _do_request(self, url, method='GET', **kwargs):
        methods = {
            'GET': self.app.get,
            'POST': self.app.post,
            'PUT': self.app.put,
            'DELETE': self.app.delete
        }
        kwargs.setdefault('headers', {}).update(self.__headers__)
        return methods.get(method, self.app.get)(str(url), **kwargs)

    def post(self, url, **kwargs):
        """
        @param (string) url - The URL to emulate a POST request to
        @returns (paste.fixture.TestResponse)
        """
        return self._do_request(url, 'POST', **kwargs)

    def get(self, url, **kwargs):
        """
        @param (string) url - The URL to emulate a GET request to
        @returns (paste.fixture.TestResponse)
        """
        return self._do_request(url, 'GET', **kwargs)

    def put(self, url, **kwargs):
        """
        @param (string) url - The URL to emulate a PUT request to
        @returns (paste.fixture.TestResponse)
        """
        return self._do_request(url, 'PUT', **kwargs)

    def delete(self, url, **kwargs):
        """
        @param (string) url - The URL to emulate a DELETE request to
        @returns (paste.fixture.TestResponse)
        """
        return self._do_request(url, 'DELETE', **kwargs)
