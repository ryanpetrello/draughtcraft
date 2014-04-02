from copy import deepcopy
from unittest import TestCase
import subprocess
import os

from pecan import conf
from pecan.testing import load_test_app
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from draughtcraft import model as dcmodel

__bind__ = 'postgresql+psycopg2://localhost'


class TestModel(TestCase):

    config = {
        'app': {
            'root': 'draughtcraft.controllers.root.RootController',
            'modules': ['draughtcraft'],
            'static_root': '%s/../../public' % os.path.dirname(__file__),
            'template_path': '%s/../templates' % os.path.dirname(__file__),
            'stamp': 'XYZ',
            'reload': False,
            'debug': True,
            'logging': False
        },
        'signups': {
            'bcc': 'ryan@example.com'
        },
        'postmark': {
            'api_key': 'POSTMARK_API_TEST'
        },
        'cache': {
            'key': 'resources_to_compile',
            '__force_dict__': True
        },
        'redis': {
            '__force_dict__': True
        }
    }

    __db__ = None

    @classmethod
    def setUpClass(cls):
        if TestModel.__db__ is None:
            TestModel.__db__ = 'draughtcrafttest'
            # Connect and create the temporary database
            print "=" * 80
            print "CREATING TEMPORARY DATABASE FOR TESTS"
            print "=" * 80
            subprocess.call(['createdb', TestModel.__db__])

            # Bind and create the database tables
            dcmodel.clear()
            dcmodel.bind(create_engine(
                '%s/%s' % (__bind__, TestModel.__db__), **{
                    'encoding': 'utf-8',
                    'poolclass': NullPool
                }
            ))
            dcmodel.metadata.create_all()
            dcmodel.commit()
            dcmodel.clear()

    def setUp(self):
        config = deepcopy(self.config)

        # Add the appropriate connection string to the app config.
        config['sqlalchemy'] = {
            'url': '%s/%s' % (__bind__, TestModel.__db__),
            'encoding': 'utf-8',
            'poolclass': NullPool
        }

        # Set up a fake app
        self.app = self.load_test_app(config)
        dcmodel.clear()

    def load_test_app(self, config):
        return load_test_app(config)

    def tearDown(self):
        from sqlalchemy.engine import reflection

        # Tear down and dispose the DB binding
        dcmodel.clear()

        # start a transaction
        engine = conf.sqlalchemy.sa_engine
        conn = engine.connect()
        trans = conn.begin()

        inspector = reflection.Inspector.from_engine(engine)

        # gather all data first before dropping anything.
        # some DBs lock after things have been dropped in
        # a transaction.
        conn.execute("TRUNCATE TABLE %s RESTART IDENTITY CASCADE" % (
            ', '.join(inspector.get_table_names())
        ))

        trans.commit()
        conn.close()


class TestApp(TestModel):
    """
    A controller test starts a database transaction and creates a fake
    WSGI app.
    """

    __headers__ = {}

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

    def get_form(self, response):
        return response.request.environ['webob.adhoc_attrs']['pecan'].get(
            'form'
        )


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
            username='ryanpetrello',
            password='secret',
            email='ryan@example.com'
        )
        dcmodel.commit()
        response = self.post('/login', params={
            'username': 'ryanpetrello',
            'password': 'secret'
        })
        assert 'user_id' in response.request.environ['beaker.session']
