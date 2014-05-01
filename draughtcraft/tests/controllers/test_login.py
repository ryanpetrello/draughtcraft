from hashlib import sha256

from draughtcraft.tests import TestApp
from draughtcraft import model


class TestLogin(TestApp):

    def test_login_form(self):
        assert self.get('/login').status_int == 200

    def test_empty_username(self):
        response = self.post('/login', params={
            'username': '',
            'password': 'secret'
        })

        assert response.status_int == 200
        assert len(self.get_form(response).errors)
        assert 'user_id' not in response.request.environ['beaker.session']

    def test_empty_password(self):
        response = self.post('/login', params={
            'username': 'ryanpetrello',
            'password': ''
        })

        assert response.status_int == 200
        assert len(self.get_form(response).errors)
        assert 'user_id' not in response.request.environ['beaker.session']

    def test_invalid_credentials(self):
        model.User(
            username='ryanpetrello',
            password='secret'
        )
        model.commit()

        response = self.post('/login', params={
            'username': 'ryanpetrello',
            'password': 'password'
        })

        assert response.status_int == 200
        assert len(self.get_form(response).errors)
        assert 'user_id' not in response.request.environ['beaker.session']

    def test_valid_login(self):
        model.User(
            username='ryanpetrello',
            password='secret'
        )
        model.commit()

        response = self.post('/login', params={
            'username': 'ryanpetrello',
            'password': 'secret'
        })

        assert response.request.environ['beaker.session']['user_id'] == 1

    def test_valid_sha256_login(self):
        salt = 'example'
        model.User(
            username='ryanpetrello',
            _password=sha256('secret' + salt).hexdigest()
        )
        model.commit()

        response = self.post('/login', params={
            'username': 'ryanpetrello',
            'password': 'secret'
        })

        assert response.request.environ['beaker.session']['user_id'] == 1

    def test_valid_logout(self):
        model.User(
            username='ryanpetrello',
            password='secret'
        )
        model.commit()

        response = self.post('/login', params={
            'username': 'ryanpetrello',
            'password': 'secret'
        })

        assert response.request.environ['beaker.session']['user_id'] == 1
        response = self.get('/logout')
        assert 'user_id' not in response.request.environ['beaker.session']


class TestRecipeConversion(TestApp):

    def test_trial_recipe_conversion(self):
        """
        Create a recipe as a guest.
        After login, the recipe should belong to the authenticated user.
        """

        params = {
            'name': 'Rocky Mountain River IPA',
            'type': 'MASH',
            'volume': 25,
            'unit': 'GALLON'
        }

        self.post('/recipes/create', params=params)
        assert model.Recipe.query.count() == 1
        assert model.Recipe.get(1).author is None

        # Create a new user
        model.User(
            username='ryanpetrello',
            password='secret'
        )
        model.commit()

        # Log in as the new user
        assert len(model.User.get(1).recipes) == 0
        response = self.post('/login', params={
            'username': 'ryanpetrello',
            'password': 'secret'
        })
        assert response.request.environ['beaker.session']['user_id'] == 1

        #
        # The recipe should have been attached to the new user, and the
        # `trial_recipe_id` record should have been removed from the session.
        #
        assert len(model.User.get(1).recipes) == 1
        assert 'trial_recipe_id' not in response.request.environ[
            'beaker.session']
