from draughtcraft.tests     import TestAuthenticatedApp


class TestProfileSettings(TestAuthenticatedApp):

    def test_profile_render(self):
        assert self.get('/settings/profile/').status_int == 200
