from draughtcraft.tests import TestAuthenticatedApp


class TestRoot(TestAuthenticatedApp):

    def test_index_redirection(self):
        """
        When / is hit by an authenticated user, we should redirect to their
        profile.
        """
        response = self.get('/')
        assert response.status_int == 302
        assert response.headers['Location'].endswith('/profile/ryanpetrello')

    def test_browser_upgrade(self):
        assert self.get('/browser').status_int == 200
