from draughtcraft.tests     import TestApp
from draughtcraft           import model


class TestLogin(TestApp):

    def test_login_form(self):
        assert self.get('/login').status_int == 200

    def test_empty_username(self):
        response = self.post('/login', params={
            'username'  : '',
            'password'  : 'secret'
        })

        assert response.status_int == 200
        assert 'validation_errors' in response.request.pecan
        assert 'user_id' not in response.environ['beaker.session']

    def test_empty_password(self):
        response = self.post('/login', params={
            'username'  : 'ryanpetrello',
            'password'  : ''
        })

        assert response.status_int == 200
        assert 'validation_errors' in response.request.pecan
        assert 'user_id' not in response.environ['beaker.session']

    def test_invalid_credentials(self):
        model.User(
            username = 'ryanpetrello',
            password = 'secret'
        )
        model.commit()

        response = self.post('/login', params={
            'username'  : 'ryanpetrello',
            'password'  : 'password'
        })

        assert response.status_int == 200
        assert 'validation_errors' in response.request.pecan
        assert 'user_id' not in response.environ['beaker.session']

    def test_valid_login(self):
        model.User(
            username = 'ryanpetrello',
            password = 'secret'
        )
        model.commit()

        response = self.post('/login', params={
            'username'  : 'ryanpetrello',
            'password'  : 'secret'
        })

        assert response.environ['beaker.session']['user_id'] == 1

    def test_valid_logout(self):
        model.User(
            username = 'ryanpetrello',
            password = 'secret'
        )
        model.commit()

        response = self.post('/login', params={
            'username'  : 'ryanpetrello',
            'password'  : 'secret'
        })

        assert response.environ['beaker.session']['user_id'] == 1
        response = self.get('/logout')
        assert 'user_id' not in response.environ['beaker.session']
