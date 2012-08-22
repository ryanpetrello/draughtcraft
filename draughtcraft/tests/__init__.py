from copy import deepcopy
from unittest import TestCase
import os

from pecan import conf, set_config
from pecan.testing import load_test_app
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from draughtcraft import model as dcmodel


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

    #
    # This approach is definitely not thread-safe, but we're operating on the
    # assumption that tests aren't running in parallel.
    #
    _database_created = False
    _tables_created = False

    def setUp(self):

        config = deepcopy(self.config)

        # ...and add the appropriate connection string to the app config.
        bind = 'postgresql+psycopg2://localhost'
        db = 'draughtcrafttest'
        config['sqlalchemy'] = {
            'url': '%s/%s' % (bind, db),
            'encoding': 'utf-8',
            'poolclass': NullPool
        }

        # Connect and create the temporary database if it doesn't exist
        if not self._database_created:
            print "=" * 80
            print "CREATING TEMPORARY DATABASE FOR TESTS"
            print "=" * 80
            conn = create_engine(bind + '/template1', echo=True).connect()
            conn.connection.set_isolation_level(0)
            conn.execute('DROP DATABASE IF EXISTS %s' % db)
            conn.execute('CREATE DATABASE %s' % db)
            conn.connection.set_isolation_level(1)
            TestModel._database_created = True
            conn.close()

        # Set up a fake app
        self.app = load_test_app(config)

        # Create the database tables (if we haven't already)
        if not TestModel._tables_created:
            dcmodel.clear()
            dcmodel.start()
            dcmodel.init_model()
            dcmodel.metadata.create_all(conf.sqlalchemy.sa_engine)
            dcmodel.commit()
            dcmodel.clear()
            TestModel._tables_created = True

    def tearDown(self):
        from sqlalchemy.engine import reflection
        from sqlalchemy.schema import (
            MetaData,
            Table,
            ForeignKeyConstraint,
            DropConstraint
        )

        # Tear down and dispose the DB binding
        dcmodel.clear()

        engine = conf.sqlalchemy.sa_engine
        conn = engine.connect()

        # start at transaction
        trans = conn.begin()

        inspector = reflection.Inspector.from_engine(engine)

        # gather all data first before dropping anything.
        # some DBs lock after things have been dropped in
        # a transaction.

        metadata = MetaData()

        tbs = []
        all_fks = []

        for table_name in inspector.get_table_names():
            fks = []
            for fk in inspector.get_foreign_keys(table_name):
                if not fk['name']:
                    continue
                fks.append(
                    ForeignKeyConstraint((), (), name=fk['name'])
                    )
            t = Table(table_name, metadata, *fks)
            tbs.append(t)
            all_fks.extend(fks)

        for fkc in all_fks:
            conn.execute(DropConstraint(fkc))

        for table in tbs:
            conn.execute('TRUNCATE TABLE %s RESTART IDENTITY' % table.name)

        trans.commit()
        conn.close()

        set_config({}, overwrite=True)
        super(TestModel, self).tearDown()


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
