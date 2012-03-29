from pecan                  import conf, abort
from draughtcraft.tests     import TestApp
from draughtcraft           import model

import fudge


class TestSignup(TestApp):

    def test_signup_form(self):
        assert model.User.query.count() == 0
        self.get('/signup')
        assert model.User.query.count() == 0

    def test_schema_validation(self):
        params = {
            'username': 'testing',
            'password': 'secret',
            'password_confirm': 'secret',
            'email': 'ryan@example.com'
        }
        for k in params:
            copy = params.copy()
            del copy[k]

            response = self.post('/signup/', params=copy)
            assert response.status_int == 200
            assert len(response.request.pecan['form'].errors)

        assert model.User.query.count() == 0

    @fudge.patch('draughtcraft.lib.email.send')
    def test_successful_signup(self, fake_send):
        (fake_send.expects_call().with_args(
            'ryan@example.com',
            'signup',
            'Welcome to DraughtCraft',
            {'username': 'test'},
            bcc=[conf.signups.bcc]
        ))

        params = {
            'username': 'test',
            'password': 'secret',
            'password_confirm': 'secret',
            'email': 'ryan@example.com'
        }

        assert model.User.query.count() == 0
        self.post('/signup/', params=params)

        assert model.User.query.count() == 1
        user = model.User.get(1)

        assert user.username == 'test'
        assert user.password
        assert user.email == 'ryan@example.com'

    @fudge.patch('draughtcraft.lib.email.send', 'pecan.redirect')
    def test_signup_failure(self, fake_send, fake_redirect):
        """
        If signup fails for some reason (a traceback is thrown, for instance)
        a welcome email should *not* be queued through Postmark.
        """

        #
        # Cause the redirect at the end of the signup method to fail and throw
        # an HTTP 500 for some reason.
        #
        (fake_redirect.expects_call().with_args(
            '/login?welcome'
        ).calls(lambda code: abort(500)))

        # Make sure that emaillib.send() is not called.
        (fake_send.is_callable().times_called(0))

        params = {
            'username': 'test',
            'password': 'secret',
            'password_confirm': 'secret',
            'email': 'ryan@example.com'
        }

        assert model.User.query.count() == 0
        self.post('/signup/', params=params, status=500)

        assert model.User.query.count() == 0

    def test_username_length(self):
        """
        Usernames should be >= 4 chars
        """
        params = {
            'username': 'test',
            'password': 'secret',
            'password_confirm': 'secret',
            'email': 'ryan@example.com'
        }

        assert model.User.query.count() == 0
        self.post('/signup/', params=params)

        assert model.User.query.count() == 1

        params = {
            'username': 'tes',
            'password': 'secret',
            'password_confirm': 'secret',
            'email': 'ryan@example.com'
        }

        self.post('/signup/', params=params)

        assert model.User.query.count() == 1

    def test_username_uniqueness(self):
        """
        Usernames should be globally unique
        """
        params = {
            'username': 'test',
            'password': 'secret',
            'password_confirm': 'secret',
            'email': 'ryan@example.com'
        }

        assert model.User.query.count() == 0
        self.post('/signup/', params=params)
        assert model.User.query.count() == 1

        params = {
            'username': 'test',
            'password': 'secret',
            'password_confirm': 'secret',
            'email': 'ryan2@example.com'
        }

        self.post('/signup/', params=params)
        assert model.User.query.count() == 1

    def test_username_regex_format(self):
        """
        Usernames should only contain numbers, letters, and underscores
        """
        params = {
            'username': 'testing_023456789_TESTING_',
            'password': 'secret',
            'password_confirm': 'secret',
            'email': 'ryan@example.com'
        }

        assert model.User.query.count() == 0
        self.post('/signup/', params=params)

        assert model.User.query.count() == 1

        for username in [
            'testing_023456789_TESTING_ ',
            'testing_023456789_TESTING_-',
            'testing_023456789_TESTING_?',
            'testing_023456789_TESTING_!',
            'testing_023456789_TESTING_$',
        ]:
            params = {
                'username': username,
                'password': 'secret',
                'password_confirm': 'secret',
                'email': 'ryan@example.com'
            }
            self.post('/signup/', params=params)
            assert model.User.query.count() == 1

    def test_password_match(self):
        """
        Passwords should match exactly
        """
        params = {
            'username': 'test',
            'password': 'secret',
            'password_confirm': 'secret2',
            'email': 'ryan@example.com'
        }

        assert model.User.query.count() == 0
        self.post('/signup/', params=params)
        assert model.User.query.count() == 0

    def test_password_length(self):
        """
        Passwords should be at least 4 characters in length.
        """
        params = {
            'username': 'test',
            'password': 'foo',
            'password_confirm': 'foo',
            'email': 'ryan@example.com'
        }

        assert model.User.query.count() == 0
        self.post('/signup/', params=params)
        assert model.User.query.count() == 0

    def test_invalid_email(self):
        """
        Emails should be valid email addresses
        """
        for email in [
            'ryan',
            'ryan@',
            'ryan@example',
            'ryan@example.',
            'ryan@example.x',
        ]:
            params = {
                'username': 'test',
                'password': 'secret',
                'password_confirm': 'secret',
                'email': email
            }

            assert model.User.query.count() == 0
            self.post('/signup/', params=params)
            assert model.User.query.count() == 0

    def test_email_uniqueness(self):
        """
        Emails should be globally unique
        """
        params = {
            'username': 'test',
            'password': 'secret',
            'password_confirm': 'secret',
            'email': 'ryan@example.com'
        }

        assert model.User.query.count() == 0
        self.post('/signup/', params=params)
        assert model.User.query.count() == 1

        params = {
            'username': 'testing',
            'password': 'secret',
            'password_confirm': 'secret',
            'email': 'ryan@example.com'
        }

        self.post('/signup/', params=params)
        assert model.User.query.count() == 1

import unittest
@unittest.expectedFailure
class TestRecipeConversion(TestApp):

    def test_trial_recipe_conversion(self):
        """
        Create a recipe as a guest.
        After signup, the recipe should belong to the newly created user.
        """

        params = {
            'name'      : 'Rocky Mountain River IPA',
            'type'      : 'MASH',
            'volume'    : 25,
            'unit'      : 'GALLON'
        }

        self.post('/recipes/create', params=params)
        assert model.Recipe.query.count() == 1
        assert model.Recipe.get(1).author == None

        params = {
            'username'          : 'test',
            'password'          : 'secret',
            'password_confirm'  : 'secret',
            'email'             : 'ryan@example.com'
        }

        assert model.User.query.count() == 0
        response = self.post('/signup/', params=params)

        assert model.User.query.count() == 1
        user = model.User.get(1)

        assert user.username == 'test'
        assert user.password
        assert user.email == 'ryan@example.com'

        #
        # The recipe should have been attached to the new user, and the
        # `trial_recipe_id` record should have been removed from the session.
        #
        assert len(user.recipes) == 1
        assert 'trial_recipe_id' not in response.environ['beaker.session']
