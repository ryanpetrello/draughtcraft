from draughtcraft.tests import TestApp


class TestErrorHandler(TestApp):

    def test_404(self):
        response = self.get('/missing', status=404)
        assert response.status_int == 404

        assert 'Not Found' in response.body
