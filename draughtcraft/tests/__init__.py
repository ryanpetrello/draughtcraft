from draughtcraft       import model as dcmodel
from webtest            import TestApp as WebTestApp
from unittest           import TestCase

import py.test

class TestModel(TestCase):

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


class TestApp(TestModel):
    """
    A controller test starts a database transaction and creates a fake
    WSGI app.
    """

    __headers__ = {}

    def setUp(self):
        # Set up a fake app
        self.app = WebTestApp(py.test.wsgi_app)

        super(TestApp, self).setUp()

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


class TestAuthenticatedApp(TestApp):
    """
    A controller test that creates a default user and logs in as them.
    """

    def setUp(self):
        super(TestAuthenticatedApp, self).setUp()

        #
        # Make a user and authenticate as them.
        #
        dcmodel.User(
            username = 'ryanpetrello',
            password = 'secret',
            email    = 'ryan@example.com'
        )
        dcmodel.commit()
        response = self.post('/login', params={
            'username'  : 'ryanpetrello',
            'password'  : 'secret'
        })
        assert 'user_id' in response.environ['beaker.session']
