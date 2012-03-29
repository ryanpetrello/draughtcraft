from pecan              import conf, set_config
from pecan.testing      import load_test_app
from draughtcraft       import model as dcmodel
from unittest           import TestCase

import os


class TestModel(TestCase):

    def setUp(self):
        # Set up a fake app
        self.app = load_test_app(os.path.join(
            os.path.dirname(__file__),
            'config.py'
        ))

        # Create the database tables
        dcmodel.clear()
        dcmodel.start()
        dcmodel.metadata.create_all()
        dcmodel.commit()
        dcmodel.clear()

    def tearDown(self):
        from sqlalchemy.engine import reflection
        from sqlalchemy.schema import (
            MetaData,
            Table,
            DropTable,
            ForeignKeyConstraint,
            DropConstraint,
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
            conn.execute(DropTable(table))

        trans.commit()
        conn.close()

        set_config({}, overwrite=True)


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
        assert 'user_id' in response.environ['beaker.session']
