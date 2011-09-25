from draughtcraft.tests     import TestAuthenticatedApp


class TestProfileView(TestAuthenticatedApp):

    def test_simple_profile_render(self):
        assert self.get('/profile/ryanpetrello/').status_int == 200
