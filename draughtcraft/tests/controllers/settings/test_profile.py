from draughtcraft           import model
from draughtcraft.tests     import TestApp, TestAuthenticatedApp


class TestUnauthenticatedProfileSettings(TestApp):

    def test_profile_render(self):
        assert self.get('/settings/profile/', status=401).status_int == 401


class TestProfileSettings(TestAuthenticatedApp):

    def test_profile_render(self):
        assert self.get('/settings/profile/').status_int == 200

    def test_missing_name(self):
        params = {
            'first_name'    : '',
            'last_name'     : '',
            'email'         : 'ryantesting123@example.com',
            'location'      : ''
        }
        self.post('/settings/profile/', params=params)

        assert model.User.get(1).email == 'ryantesting123@example.com'

    def test_missing_email(self):
        params = {
            'first_name'    : '',
            'last_name'     : '',
            'email'         : '',
            'location'      : ''
        }

        assert model.User.get(1).email == 'ryan@example.com'

        response = self.post('/settings/profile/', params=params)
        assert 'validation_errors' in response.request.pecan

        assert model.User.get(1).email == 'ryan@example.com'

    def test_invalid(self):
        params = {
            'first_name'    : '',
            'last_name'     : '',
            'email'         : 'ryan@invalid',
            'location'      : ''
        }

        assert model.User.get(1).email == 'ryan@example.com'

        response = self.post('/settings/profile/', params=params)
        assert 'validation_errors' in response.request.pecan

        assert model.User.get(1).email == 'ryan@example.com'

    def test_success(self):
        params = {
            'first_name'    : 'Ryan',
            'last_name'     : 'Petrello',
            'email'         : 'ryantesting123@example.com',
            'location'      : ''
        }
        self.post('/settings/profile/', params=params)

        assert model.User.get(1).first_name == 'Ryan'
        assert model.User.get(1).last_name == 'Petrello'
        assert model.User.get(1).email == 'ryantesting123@example.com'
