from draughtcraft.tests     import TestApp
from draughtcraft           import model


class TestRecipeCreation(TestApp):

    def test_signup_form(self):
        assert model.User.query.count() == 0
        self.get('/signup')
        assert model.User.query.count() == 0

    def test_schema_validation(self):
        params = {
            'username'          : 'testing',
            'password'          : 'secret',
            'password_confirm'  : 'secret',
            'email'             : 'ryan@example.com'
        }
        for k in params:
            copy = params.copy()
            del copy[k]

            response = self.post('/signup/', params=copy)
            assert response.status_int == 200
            assert 'validation_errors' in response.request.pecan

        assert model.User.query.count() == 0

    def test_successful_signup(self):
        params = {
            'username'          : 'test',
            'password'          : 'secret',
            'password_confirm'  : 'secret',
            'email'             : 'ryan@example.com'
        }

        assert model.User.query.count() == 0
        self.post('/signup/', params=params)

        assert model.User.query.count() == 1
        user = model.User.get(1)

        assert user.username == 'test'
        assert user.password
        assert user.email == 'ryan@example.com'

    def test_username_length(self):
        """
        Usernames should be >= 4 chars
        """
        params = {
            'username'          : 'test',
            'password'          : 'secret',
            'password_confirm'  : 'secret',
            'email'             : 'ryan@example.com'
        }

        assert model.User.query.count() == 0
        self.post('/signup/', params=params)

        assert model.User.query.count() == 1

        params = {
            'username'          : 'tes',
            'password'          : 'secret',
            'password_confirm'  : 'secret',
            'email'             : 'ryan@example.com'
        }

        self.post('/signup/', params=params)

        assert model.User.query.count() == 1

    def test_username_uniqueness(self):
        """
        Usernames should be globally unique
        """
        params = {
            'username'          : 'test',
            'password'          : 'secret',
            'password_confirm'  : 'secret',
            'email'             : 'ryan@example.com'
        }

        assert model.User.query.count() == 0
        self.post('/signup/', params=params)
        assert model.User.query.count() == 1

        params = {
            'username'          : 'test',
            'password'          : 'secret',
            'password_confirm'  : 'secret',
            'email'             : 'ryan2@example.com'
        }

        self.post('/signup/', params=params)
        assert model.User.query.count() == 1

    def test_username_regex_format(self):
        """
        Usernames should only contain numbers, letters, and underscores
        """
        params = {
            'username'          : 'testing_023456789_TESTING_',
            'password'          : 'secret',
            'password_confirm'  : 'secret',
            'email'             : 'ryan@example.com'
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
                'username'          : username,
                'password'          : 'secret',
                'password_confirm'  : 'secret',
                'email'             : 'ryan@example.com'
            }
            self.post('/signup/', params=params)
            assert model.User.query.count() == 1
            
    def test_password_match(self):
        """
        Passwords should match exactly
        """
        params = {
            'username'          : 'test',
            'password'          : 'secret',
            'password_confirm'  : 'secret2',
            'email'             : 'ryan@example.com'
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
                'username'          : 'test',
                'password'          : 'secret',
                'password_confirm'  : 'secret',
                'email'             : email
            }

            assert model.User.query.count() == 0
            self.post('/signup/', params=params)
            assert model.User.query.count() == 0

    def test_email_uniqueness(self):
        """
        Emails should be globally unique
        """
        params = {
            'username'          : 'test',
            'password'          : 'secret',
            'password_confirm'  : 'secret',
            'email'             : 'ryan@example.com'
        }

        assert model.User.query.count() == 0
        self.post('/signup/', params=params)
        assert model.User.query.count() == 1

        params = {
            'username'          : 'testing',
            'password'          : 'secret',
            'password_confirm'  : 'secret',
            'email'             : 'ryan@example.com'
        }

        self.post('/signup/', params=params)
        assert model.User.query.count() == 1
