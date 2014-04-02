from draughtcraft import model
from draughtcraft.tests import TestApp, TestAuthenticatedApp


class TestUnauthenticatedProfileSettings(TestApp):

    def test_profile_render(self):
        resp = self.get('/settings/profile/', status=302)
        assert resp.status_int == 302
        assert resp.headers['Location'].endswith('/signup')


class TestProfileSettings(TestAuthenticatedApp):

    def test_profile_render(self):
        assert self.get('/settings/profile/').status_int == 200

    def test_missing_name(self):
        params = {
            'first_name': '',
            'last_name': '',
            'email': 'ryantesting123@example.com',
            'location': '',
            'bio': ''
        }
        self.post('/settings/profile/', params=params)

        assert model.User.get(1).email == 'ryantesting123@example.com'

    def test_missing_email(self):
        params = {
            'first_name': '',
            'last_name': '',
            'email': '',
            'location': '',
            'bio': ''
        }

        assert model.User.get(1).email == 'ryan@example.com'

        response = self.post('/settings/profile/', params=params)
        assert len(self.get_form(response).errors)

        assert model.User.get(1).email == 'ryan@example.com'

    def test_invalid_email(self):
        params = {
            'first_name': '',
            'last_name': '',
            'email': 'ryan@invalid',
            'location': '',
            'bio': ''
        }

        assert model.User.get(1).email == 'ryan@example.com'

        response = self.post('/settings/profile/', params=params)
        assert len(self.get_form(response).errors)

        assert model.User.get(1).email == 'ryan@example.com'

    def test_success(self):
        params = {
            'first_name': 'Ryan',
            'last_name': 'Petrello',
            'email': 'ryantesting123@example.com',
            'location': 'Atlanta, GA',
            'bio': 'I am Ryan.'
        }
        self.post('/settings/profile/', params=params)

        assert model.User.get(1).first_name == 'Ryan'
        assert model.User.get(1).last_name == 'Petrello'
        assert model.User.get(1).email == 'ryantesting123@example.com'
        assert model.User.get(1).location == 'Atlanta, GA'
        assert model.User.get(1).bio == 'I am Ryan.'
