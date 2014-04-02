from draughtcraft import model
from draughtcraft.tests import TestApp, TestAuthenticatedApp


class TestUnauthenticatedPasswordChange(TestApp):

    def test_password_render(self):
        resp = self.get('/settings/password/', status=302)
        assert resp.status_int == 302
        assert resp.headers['Location'].endswith('/signup')


class TestChangePassword(TestAuthenticatedApp):

    def test_password_render(self):
        assert self.get('/settings/password/').status_int == 200

    def test_missing_values(self):
        params = {
            'old_password': 'secret',
            'password': 'secret2',
            'password_confirm': 'secret2'
        }

        for k in params:
            copy = params.copy()
            del copy[k]
            response = self.post('/settings/password/', params=copy)
            assert len(self.get_form(response).errors)

        assert model.User.validate('ryanpetrello', 'secret') == \
            model.User.query.first()

    def test_incorrect_old_password(self):
        params = {
            'old_password': 'wrong',
            'password': 'password',
            'password_confirm': 'password'
        }

        response = self.post('/settings/password/', params=params)
        assert len(self.get_form(response).errors)

        assert model.User.validate('ryanpetrello', 'secret') == \
            model.User.query.first()

    def test_passwords_not_match(self):
        params = {
            'old_password': 'secret',
            'password': 'password',
            'password_confirm': 'password2'
        }

        response = self.post('/settings/password/', params=params)
        assert len(self.get_form(response).errors)

        assert model.User.validate('ryanpetrello', 'secret') == \
            model.User.query.first()

    def test_new_password_length(self):
        params = {
            'old_password': 'secret',
            'password': 'foo',
            'password_confirm': 'foo'
        }

        response = self.post('/settings/password/', params=params)
        assert len(self.get_form(response).errors)

        assert model.User.validate('ryanpetrello', 'secret') == \
            model.User.query.first()

    def test_success(self):
        params = {
            'old_password': 'secret',
            'password': 'newpassword',
            'password_confirm': 'newpassword'
        }

        self.post('/settings/password/', params=params)

        assert model.User.validate('ryanpetrello', 'newpassword') == \
            model.User.query.first()
