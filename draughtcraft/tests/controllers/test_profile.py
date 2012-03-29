from draughtcraft.tests     import TestAuthenticatedApp


import unittest
@unittest.expectedFailure
class TestProfileView(TestAuthenticatedApp):

    def test_simple_profile_render(self):
        assert self.get('/profile/ryanpetrello/').status_int == 200

    def test_nonexistant_profile(self):
        assert self.get('/profile/nobody/', status=404).status_int == 404
